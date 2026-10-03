#!/usr/bin/env python3
"""Install proxy helpers; migrate private Claude state only with explicit input arguments."""

import argparse
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import uuid


IDENTITY_KEYS = {"oauthAccount", "userID", "hasCompletedOnboarding", "hasIdeOnboardingBeenShown",
                 "installMethod", "autoUpdates", "firstStartVersion", "claudeCodeFirstTokenDate",
                 "opusProMigrationComplete"}


def object_file(path):
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError("Expected JSON object")
    return value


def write_private(path, content):
    if path.is_symlink():
        raise ValueError(f"Refusing symlink destination: {path.name}")
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.exists():
        backup = path.with_name(path.name + '.bak-' + uuid.uuid4().hex)
        shutil.copy2(path, backup)
        backup.chmod(0o600)
    descriptor, temporary_name = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(0o600)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user-home', type=Path, default=Path.home(), help='Explicit installation home; useful for isolated validation')
    parser.add_argument('--credentials', type=Path)
    parser.add_argument('--identity-seed', type=Path)
    parser.add_argument('--settings', type=Path)
    args = parser.parse_args()
    root = args.user_home.absolute()
    directory = root / '.cc'
    claude = root / '.claude'
    for path in (root, directory, claude):
        if path.is_symlink():
            raise ValueError('Refusing symlink installation directory')
    source = Path(__file__).resolve().parent
    scripts = ('cc_env.sh', 'cc_proxy.py', 'cc_proxy_chain.py')
    payloads = {name: (source / name).read_bytes() for name in scripts}
    template = (source / 'cc_proxy.conf.example').read_bytes()
    spec = importlib.util.spec_from_file_location('cc_proxy_manager', source / 'cc_proxy.py')
    manager = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(manager)
    # Validate all private inputs and destinations before any write.
    private = {}
    if args.credentials:
        object_file(args.credentials)
        private[claude / '.credentials.json'] = args.credentials.read_bytes()
    if args.settings:
        object_file(args.settings)
        if not (claude / 'settings.json').exists():
            private[claude / 'settings.json'] = args.settings.read_bytes()
    if args.identity_seed:
        seed = object_file(args.identity_seed)
        if set(seed) - IDENTITY_KEYS:
            raise ValueError('Identity seed has unknown top-level fields')
        destination = root / '.claude.json'
        current = object_file(destination) if destination.exists() else {}
        current.update(seed)
        private[destination] = (json.dumps(current, indent=2) + '\n').encode()
    config_target = directory / ('cc_proxy.conf.new' if (directory / 'cc_proxy.conf').exists() else 'cc_proxy.conf')
    targets = [*(directory / name for name in scripts), config_target, *private]
    if any(p.is_symlink() or (p.exists() and not p.is_file()) for p in targets):
        raise ValueError('Destination contains a symlink or non-file')
    os.umask(0o077)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if directory.stat().st_uid != os.getuid():
        raise ValueError('Proxy directory is owned by another user')
    lock_path = directory / 'cc_proxy.lock'
    if lock_path.is_symlink():
        raise ValueError('Refusing symlink lock')
    with lock_path.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        pidfile = directory / 'cc_proxy_chain.pid'
        record = manager.read_record(pidfile)
        if record and (manager.matches(record, directory / 'cc_proxy_chain.py') or Path(f'/proc/{record["pid"]}').exists()):
            raise RuntimeError('A relay may still be active; do not overwrite its scripts')
        for name, payload in payloads.items():
            write_private(directory / name, payload)
        write_private(config_target, template)
        for target, payload in private.items():
            write_private(target, payload)
    print('Proxy helpers installed; existing config retained; no shell startup file modified.')
    print('Review cc_proxy.conf, then source cc_env.sh and explicitly use cc_on.')
    print('Private state files written:', len(private))


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError) as error:
        # Do not print JSON values or credentials when reporting parse/validation failures.
        print('Installation stopped: ' + type(error).__name__ + '; inspect inputs, destinations and active relay.', file=sys.stderr)
        sys.exit(2)
