#!/usr/bin/env python3
"""Forward-test research display primitives with synthetic, non-patient data."""
import argparse
import math
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from media_common import FrameWriter, ffmpeg_bin, smooth, validate, write_json
from research_animation import (tint_texture, normalize_cloud, camera_basis, slerp_camera,
                                project_cloud, camera_report, interpolate_tiles, validate_sequence_trace)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-dir', required=True)
    parser.add_argument('--font', required=True)
    parser.add_argument('--ffmpeg')
    args = parser.parse_args()
    root = Path(args.work_dir).resolve()
    if root.exists() and any(root.iterdir()):
        raise ValueError('Use a new/empty output directory')
    root.mkdir(parents=True, exist_ok=True)
    ff = ffmpeg_bin(args.ffmpeg)
    fonts = {n: ImageFont.truetype(args.font, n) for n in [16, 20, 26]}
    rng = np.random.default_rng(731)
    # Synthetic textured slices, not a simulated medical finding.
    yy, xx = np.mgrid[-1:1:96j, -1:1:96j]
    textures = {}
    for i in range(24):
        pixels = 175*np.exp(-((xx-.36*math.sin(i*.12))**2 + (yy-.3)**2)*8)
        pixels += 60*(np.cos(22*np.hypot(xx, yy)) + 1)*np.exp(-3*(xx*xx+yy*yy))
        textures[str(i)] = Image.fromarray(np.uint8(np.clip(pixels, 0, 255))).convert('RGB')
    raw = textures['7']
    original = raw.tobytes()
    blue = tint_texture(raw, '#298bb4')
    assert raw.tobytes() == original and np.asarray(blue).std() > 8
    assert np.array_equal(np.asarray(tint_texture(raw, '#298bb4', 0, 0, 1)), np.asarray(raw))
    rgba = raw.convert('RGBA')
    rgba.putalpha(Image.fromarray(np.uint8(np.clip((xx+1)*127, 0, 255))))
    assert np.array_equal(np.asarray(tint_texture(rgba, '#9965bc'))[..., 3], np.asarray(rgba)[..., 3])

    cloud = np.r_[rng.normal([-.95, .2, 0], .11, (36, 3)),
                  rng.normal([.5, -.15, .1], .28, (140, 3)),
                  rng.normal([.2, .5, .6], .2, (90, 3))]
    cloud, normalization = normalize_cloud(cloud)
    mask = np.arange(len(cloud)) < 36
    starting_cloud = rng.uniform(-1, 1, cloud.shape)
    before = camera_basis(30, -20)
    candidates = []
    for yaw in range(-90, 91, 30):
        for pitch in [-35, 0, 35]:
            basis = camera_basis(yaw, pitch)
            report = camera_report(cloud, mask, basis, [18, 64, 590, 280], [310, 204], 145, 3)
            candidates.append((report['visible_target_count'], report['clearance_p10_px'], yaw, pitch, report))
    _, _, yaw, pitch, report = max(candidates, key=lambda row: (row[0], row[1]))
    after = camera_basis(yaw, pitch)
    original_distance = np.linalg.norm(cloud[:24, None] - cloud[None, :24], axis=2)
    for endpoint in [after, camera_basis(180, 0), before]:
        for u in [0, .25, .5, .75, 1]:
            matrix = slerp_camera(before, endpoint, u)
            assert np.allclose(matrix @ matrix.T, np.eye(3), atol=1e-10)
            assert np.isclose(np.linalg.det(matrix), 1)
            rotated = cloud @ matrix.T
            assert np.allclose(np.linalg.norm(rotated[:24, None]-rotated[None, :24], axis=2), original_distance)
        assert np.allclose(slerp_camera(before, endpoint, 0), before)
        assert np.allclose(slerp_camera(before, endpoint, 1), endpoint)
    xy, _ = project_cloud(cloud, after, [310, 204], 145)
    brute = np.linalg.norm(xy[mask, None]-xy[None, ~mask], axis=2).min(1)
    assert np.isclose(report['clearance_p10_px'], np.quantile(brute, .1))
    blocked = camera_report(cloud, mask, after, [18, 64, 590, 280], [310, 204], 145,
                            3, [[18, 64, 590, 280]])
    assert blocked['visible_target_count'] == 0

    ids = [str(i) for i in range(24)]
    feature = np.arange(24)/23
    left, right = rng.permutation(14).tolist(), (14+rng.permutation(10)).tolist()
    def quality(order):
        return int((np.abs(np.diff(list(map(int, order)))) == 1).sum())
    def state(a, b, joined=False):
        order = list(map(str, a+b))
        groups = ['global']*24 if joined else ['left']*len(a)+['right']*len(b)
        return {'order': order, 'groups': groups, 'quality': quality(order)}
    initial = state(left, right)
    failed = []
    # Actual synthetic feature projections and their measured adjacency counts.
    second_feature = np.sin(np.arange(24)*1.7)
    for angle in np.linspace(-.15, .15, 6):
        score = second_feature*math.cos(angle) + feature*math.sin(angle)
        failed.append(state(sorted(left, key=lambda i: score[i]), sorted(right, key=lambda i: score[i])))
    assert failed[-1]['quality'] < 23
    # Local feature ordering followed by a common layout; no claim of general CT solving.
    local_a, local_b = sorted(left, key=lambda i: feature[i]), sorted(right, key=lambda i: feature[i])
    local = state(local_a, local_b)
    final = state(local_a, local_b, True)
    trace = [initial, *failed, initial, local, final]
    validate_sequence_trace(trace, ids)
    try:
        validate_sequence_trace([dict(initial, order=['0']*24)], ids)
    except ValueError:
        pass
    else:
        raise AssertionError('Duplicate identities accepted')
    def layout(s):
        rows = []
        for j, (identity, group) in enumerate(zip(s['order'], s['groups'])):
            if group == 'global':
                x, y = 90 + (j % 12)*90, 438 + (j // 12)*74
                color = '#438f91'
            elif group == 'left':
                x, y = 24 + (j % 7)*76, 438 + (j // 7)*74
                color = '#298bb4'
            else:
                k = j-14
                x, y = 716 + (k % 5)*90, 438 + (k // 5)*74
                color = '#9965bc'
            rows.append({'id': identity, 'xy': [x, y], 'color': color})
        return rows
    start_layout, final_layout = layout(initial), layout(final)
    for u in [0, .5, 1]:
        assert {r['id'] for r in interpolate_tiles(start_layout, final_layout, u)} == set(ids)
    assert {r['id']: r['xy'] for r in interpolate_tiles(start_layout, final_layout, 1)} == {r['id']: r['xy'] for r in final_layout}
    for a, b in [(start_layout, final_layout[:-1]), (start_layout+[start_layout[0]], final_layout)]:
        try:
            interpolate_tiles(a, b, .5)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid tile identities accepted')
    for invalid in [np.full((3, 3), np.nan), np.ones((3, 3)), np.diag([1, 1, -1])]:
        try:
            project_cloud(cloud, invalid)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid camera accepted')

    # Interpolate positions and reveal the graph at the SAME candidate event.
    schedule = [(0., initial, 'Initial groups'),
                *[(1+j*.35, failed[k], 'Attempt 1: feature hypotheses')
                  for j, k in enumerate([0, 2, 5])],
                (2.05, failed[-1], 'Consistency failed'), (2.4, initial, 'Reset'),
                (3.4, local, 'Attempt 2: local feature order'),
                (4.6, final, 'Global merge')]
    assert all(b[0]-a[0] >= .3 for a, b in zip(schedule, schedule[1:]))
    colors = {}
    def render(n):
        t = n/20
        im = Image.new('RGB', (1280, 800), '#f5f5f7')
        d = ImageDraw.Draw(im)
        d.text((24, 12), 'SYNTHETIC DISPLAY TEST - not a scientific result', font=fonts[26], fill='#162330')
        cloud_u = smooth((t-.2)/1)
        displayed_cloud = starting_cloud*(1-cloud_u)+cloud*cloud_u
        pose = slerp_camera(before, after, smooth((t-1.2)/2.6))
        xy, depth = project_cloud(displayed_cloud, pose, [310, 204], 145)
        d.rectangle((18, 64, 608, 344), outline='#b7c2c8', width=2)
        for i in np.argsort(depth):
            x, y = xy[i]
            if 22 < x < 604 and 68 < y < 340:
                color = '#278e86' if mask[i] else '#c2b4ce' if i < 176 else '#88a9b7'
                d.ellipse((x-3, y-3, x+3, y+3), fill=color)
        d.text((660, 76), 'Display tint preserves texture', font=fonts[20], fill='#162330')
        for i, color in enumerate([None, '#298bb4', '#9965bc']):
            tile = raw if color is None else tint_texture(raw, color, .58*smooth(t/.6))
            im.paste(tile.resize((150, 150)), (660+i*190, 134))
        index = max(j for j, event in enumerate(schedule) if event[0] <= t)
        at, current, label = schedule[index]
        previous = schedule[max(0, index-1)][1]
        u = smooth((t-at)/.3)
        records = interpolate_tiles(layout(previous), layout(current), u)
        d.text((24, 378), label, font=fonts[26], fill='#9c633d' if label == 'Consistency failed' else '#162330')
        if current is not final:
            for y in range(430, 606, 24):
                d.line((628, y, 628, y+12), fill='#a6acb4', width=2)
        for row in records:
            key = row['id'], row['color']
            # Finite smoke clip; production uses cached endpoints, not all intermediate colors.
            if key not in colors:
                colors[key] = tint_texture(textures[row['id']], row['color']).resize((60, 60))
            x, y = np.rint(row['xy']).astype(int)
            im.paste(colors[key], (x, y))
            d.text((x, y+59), row['id'], font=fonts[16], fill='#253646')
        d.text((24, 650), 'Last evaluated synthetic adjacent links (out of 23)', font=fonts[20], fill='#455465')
        completed = [(event[0]+(.3 if j else 0), event[1]['quality'])
                     for j, event in enumerate(schedule[:index])]
        # Do not invent fractional measured links while cards are in transit.
        q = current['quality'] if u >= 1 else previous['quality']
        if index and u >= 1:
            completed.append((at+.3, q))
        completed.append((t, q))
        graph = [(24 + when/6*1000, 765-quality/23*72) for when, quality in completed]
        d.line((24, 690, 24, 765, 1040, 765), fill='#b4bdc5', width=2)
        if len(graph) > 1:
            d.line(graph, fill='#357f87', width=3)
        d.text((1080, 700), f'{q:.1f}/23', font=fonts[26], fill='#162330')
        return im

    # Last second must be static: do not keep extending the graph's x coordinate.
    def frame(n):
        return render(min(n, 100))
    movie = root/'research-display.mkv'
    with FrameWriter(ff, movie, (1280, 800), 20) as writer:
        for n in range(120):
            writer.write(frame(n))
    verified = validate(ff, movie, 6, burned_only=True)
    assert verified['frames'] == 120
    contact = Image.new('RGB', (1280, 1200), 'white')
    for i, n in enumerate([0, 30, 42, 52, 80, 105]):
        path = root/f'actual-{n:03}.png'
        subprocess.run([ff, '-v', 'error', '-y', '-i', str(movie), '-vf', f'select=eq(n\\,{n})',
                        '-frames:v', '1', str(path)], check=True)
        actual = Image.open(path).convert('RGB')
        assert np.abs(np.asarray(actual).astype(int)-np.asarray(frame(n)).astype(int)).max() <= 1
        contact.paste(actual.resize((640, 400)), ((i % 2)*640, (i // 2)*400))
    contact.save(root/'contact.jpg', quality=95)
    hashes = subprocess.check_output([ff, '-v', 'error', '-i', str(movie), '-vf',
        'select=between(n\\,100\\,119)', '-f', 'framemd5', '-'], text=True)
    values = [line.split(',')[-1].strip() for line in hashes.splitlines() if line and not line.startswith('#')]
    assert len(values) == 20 and len(set(values)) == 1
    write_json(root/'research-smoke.json', {
        'synthetic_only': True, 'seed': 731, 'validation': verified,
        'normalization': normalization, 'camera': {'yaw': yaw, 'pitch': pitch, **report},
        'source_texture_unchanged': True, 'texture_alpha_preserved': True,
        'camera_rigidity_and_endpoints_verified': True, 'screen_clearance_matches_brute_force': True,
        'permutation_and_invalid_input_checks': True,
        'states': trace, 'schedule': [{'time': t, 'quality': s['quality'], 'label': label} for t, s, label in schedule],
        'actual_frames_compared': [0, 30, 42, 52, 80, 105], 'complete_static_hold_frames': len(values),
    })
    print('PASS: tint/alpha, rigid cameras, clearance, state identities, actual frames and 20-frame hold')


if __name__ == '__main__':
    main()
