#!/usr/bin/env python3
"""Acceptance check against a running real Slicer session, using PyAutoGUI HTTP actions."""
import argparse
import json
import time
import urllib.request
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('run_dir', type=Path)
args = parser.parse_args()
run_dir = args.run_dir
for _ in range(180):
    if (run_dir / 'session.json').exists():
        break
    time.sleep(1)
else:
    raise SystemExit('desktop did not start within 180s; inspect install.log and bridge.log')
session = json.loads((run_dir / 'session.json').read_text())
token = Path(session['token_file']).read_text().strip()
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
base = f'http://127.0.0.1:{session["port"]}'

def request(path, data=None):
    headers = {'Authorization': f'Bearer {token}'}
    if data is not None:
        data = json.dumps(data).encode()
        headers['Content-Type'] = 'application/json'
    with opener.open(urllib.request.Request(base+path, data=data, headers=headers), timeout=30) as r:
        return r.read()

def act(action):
    result = json.loads(request('/action', action))
    assert result['ok'], result
    return result

health = json.loads(request('/healthz'))
assert health['backend'] == 'pyautogui', health
act({'type': 'move', 'x': 420, 'y': 260})
assert json.loads(request('/position'))['position'] == [420, 260]
time.sleep(15)  # Allow Slicer modules to finish loading before opening its console.
(run_dir / 'slicer-before.png').write_bytes(request('/screenshot'))
# Activate the application explicitly: a newly mapped window may not own keyboard focus.
width, height = health['size']
act({'type': 'click', 'x': width//2, 'y': height//2})
time.sleep(1)
# A fresh Slicer profile shows its first-run acknowledgement after activation.
act({'type': 'keypress', 'keys': ['enter']})
time.sleep(1)
# Use the GUI's Python console to build a small 3D surface and a tiny image volume.
# Marker creation proves the keyboard events reached Slicer, rather than just X11.
marker = run_dir / 'slicer-input-confirmed.json'
command = (
    'import json, vtk, numpy as np; '
    'slicer.util.mainWindow().showMaximized(); '
    'slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView); '
    'source=vtk.vtkSphereSource(); source.SetRadius(30); source.SetThetaResolution(48); '
    'source.SetPhiResolution(48); source.Update(); '
    'model=slicer.modules.models.logic().AddModel(source.GetOutput()); '
    'model.SetName("CPU llvmpipe test sphere"); '
    'model.GetDisplayNode().SetColor(0.2,0.7,1.0); '
    'slicer.util.resetThreeDViews(); '
    'slicer.app.processEvents(); '
    'caps=slicer.app.layoutManager().threeDWidget(0).threeDView().renderWindow().ReportCapabilities(); '
    f'open({str(marker)!r},"w").write(json.dumps({{"slicer_version":slicer.app.applicationVersion,"sphere_points":source.GetOutput().GetNumberOfPoints(),"render_capabilities":caps}}))'
)
act({'type': 'keypress', 'keys': ['ctrl', '3']})
time.sleep(1)
(run_dir / 'slicer-console-open.png').write_bytes(request('/screenshot'))
act({'type': 'type', 'text': command})
act({'type': 'keypress', 'keys': ['enter']})
for _ in range(30):
    if marker.exists():
        break
    time.sleep(1)
if not marker.exists():
    (run_dir / 'slicer-console-error.png').write_bytes(request('/screenshot'))
    raise SystemExit('Slicer console did not execute the typed command; inspect slicer-console-error.png')
act({'type': 'keypress', 'keys': ['ctrl', '3']})
time.sleep(2)
# Rotate the actual 3D view by dragging, then capture the result.
act({'type': 'drag', 'start': {'x': width*3//4, 'y': height//2},
     'end': {'x': width*3//4+60, 'y': height//2+35}})
time.sleep(1)
(run_dir / 'slicer-pyautogui.png').write_bytes(request('/screenshot'))
result = {'health': health, 'input': json.loads(marker.read_text()),
          'checks': ['PyAutoGUI move', 'PyAutoGUI hotkey', 'PyAutoGUI type',
                     'Slicer GUI console execution', 'VTK 3D sphere', 'PyAutoGUI drag', 'PNG screenshot']}
assert result['input']['sphere_points'] > 1000
assert 'llvmpipe' in result['input']['render_capabilities'].lower(), 'Slicer did not use the expected software renderer'
for stat,paths in {
    'memory_current_bytes':['/sys/fs/cgroup/memory.current','/sys/fs/cgroup/memory/memory.usage_in_bytes'],
    'memory_peak_bytes':['/sys/fs/cgroup/memory.peak','/sys/fs/cgroup/memory/memory.max_usage_in_bytes'],
}.items():
    for path in paths:
        if Path(path).exists():
            result[stat]=int(Path(path).read_text())
            break
(run_dir / 'verification.json').write_text(json.dumps(result, indent=2))
print(json.dumps({'health':health,'slicer_version':result['input']['slicer_version'],'checks':result['checks']}, indent=2), flush=True)
