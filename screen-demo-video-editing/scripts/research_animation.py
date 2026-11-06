"""Display-only primitives for measured research results; NumPy and Pillow only.

These helpers consume existing coordinates, memberships and candidate states.
They do not extract features, cluster images, solve layer order or diagnose data.
"""
import math

import numpy as np
from PIL import Image, ImageColor


def _finite(value):
    value = np.asarray(value, dtype=float)
    if not np.isfinite(value).all():
        raise ValueError('Coordinates and parameters must be finite')
    return value


def tint_texture(image, color, amount=.58, black_level=.43, contrast=.42):
    """Lift display blacks, reduce contrast and blend color; preserve alpha.

    All scalar parameters use [0,1]. This creates a new display image, never
    modifies scientific pixels, and deliberately changes display intensity.
    """
    amount, black_level, contrast = _finite([amount, black_level, contrast])
    if not (0 <= amount <= 1 and 0 <= black_level <= 1 and
            0 <= contrast <= 1 and black_level + contrast <= 1):
        raise ValueError('Require [0,1] parameters and black_level + contrast <= 1')
    rgba = image.convert('RGBA')
    pixels = np.asarray(rgba)
    source = pixels[..., :3].astype(float) / 255
    shade = np.array(ImageColor.getrgb(color), dtype=float) / 255
    if shade.shape != (3,):
        raise ValueError('Use an opaque RGB color')
    display = (black_level + contrast * source) * (1 - amount) + shade * amount
    result = np.empty_like(pixels)
    result[..., :3] = np.rint(display * 255).astype(np.uint8)
    result[..., 3] = pixels[..., 3]
    output = Image.fromarray(result)
    return output if 'A' in image.getbands() else output.convert('RGB')


def normalize_cloud(points):
    """One translation and uniform scale for all points; no per-cluster edits."""
    points = _finite(points)
    if points.ndim != 2 or points.shape[1] != 3 or not len(points):
        raise ValueError('Expected nonempty N by 3 coordinates')
    center = np.median(points, axis=0)
    scale = float(np.quantile(np.linalg.norm(points - center, axis=1), .98))
    scale = scale if scale > 0 else 1.
    return (points - center) / scale, {'center': center.tolist(), 'scale': scale}


def camera_basis(yaw_degrees, pitch_degrees):
    """Right-handed rows: horizontal, vertical, depth."""
    yaw, pitch = np.deg2rad(_finite([yaw_degrees, pitch_degrees]))
    c, s, p, q = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch)
    horizontal = np.array([c, 0, s])
    vertical = np.array([-q*s, -p, q*c])
    return np.stack([horizontal, vertical, np.cross(horizontal, vertical)])


def _basis(value):
    value = _finite(value)
    if value.shape != (3, 3) or not np.allclose(value @ value.T, np.eye(3), atol=1e-7) or not np.isclose(np.linalg.det(value), 1):
        raise ValueError('Camera must be an orthonormal right-handed 3 by 3 basis')
    return value


def _quaternion(matrix):
    trace = float(np.trace(matrix))
    if trace > 0:
        s = math.sqrt(1 + trace) * 2
        return np.array([s/4, (matrix[2, 1]-matrix[1, 2])/s,
                         (matrix[0, 2]-matrix[2, 0])/s, (matrix[1, 0]-matrix[0, 1])/s])
    i = int(np.argmax(np.diag(matrix)))
    j, k = (i+1) % 3, (i+2) % 3
    s = math.sqrt(1 + matrix[i, i] - matrix[j, j] - matrix[k, k]) * 2
    result = np.zeros(4)
    result[0], result[i+1] = (matrix[k, j]-matrix[j, k])/s, s/4
    result[j+1], result[k+1] = (matrix[j, i]+matrix[i, j])/s, (matrix[k, i]+matrix[i, k])/s
    return result


def slerp_camera(before, after, progress):
    """Shortest rotation; unlike linear matrix interpolation, stays rigid."""
    progress = float(_finite(progress))
    if not 0 <= progress <= 1:
        raise ValueError('Progress must be in [0,1]')
    a, b = _quaternion(_basis(before)), _quaternion(_basis(after))
    dot = float(a @ b)
    if dot < 0:
        b, dot = -b, -dot
    if dot > .9995:
        q = a*(1-progress) + b*progress
    else:
        theta = math.acos(np.clip(dot, -1, 1))
        q = (math.sin((1-progress)*theta)*a + math.sin(progress*theta)*b) / math.sin(theta)
    w, x, y, z = q / np.linalg.norm(q)
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])


def project_cloud(points, basis, center=(0, 0), scale=1):
    points, center = _finite(points), _finite(center)
    scale = float(_finite(scale))
    if points.ndim != 2 or points.shape[1] != 3 or center.shape != (2,) or scale <= 0:
        raise ValueError('Expected N by 3 points, 2D center and positive scale')
    rotated = points @ _basis(basis).T
    return rotated[:, :2]*scale + center, rotated[:, 2]


def camera_report(points, target_mask, basis, viewport, center, scale, radius=3, occluders=()):
    """Report visibility and target/background clearance in output pixels.

    viewport and occluders use [x,y,w,h]. Clearance is center-to-center,
    not a clinical metric or a clustering accuracy score.
    """
    xy, _ = project_cloud(points, basis, center, scale)
    mask = np.asarray(target_mask, dtype=bool)
    if mask.shape != (len(xy),) or not mask.any() or mask.all():
        raise ValueError('Need target and non-target points')
    x, y, w, h = _finite(viewport)
    radius = float(_finite(radius))
    if min(w, h) <= 0 or radius < 0:
        raise ValueError('Invalid viewport or radius')
    target, other = xy[mask], xy[~mask]
    visible = ((target[:, 0]-radius >= x) & (target[:, 0]+radius <= x+w) &
               (target[:, 1]-radius >= y) & (target[:, 1]+radius <= y+h))
    for ox, oy, ow, oh in map(_finite, occluders):
        if min(ow, oh) <= 0:
            raise ValueError('Invalid occluder rectangle')
        visible &= ~((target[:, 0]+radius >= ox) & (target[:, 0]-radius <= ox+ow) &
                     (target[:, 1]+radius >= oy) & (target[:, 1]-radius <= oy+oh))
    nearest = np.full(len(target), np.inf)
    # Chunk both axes; do not allocate an N by N distance matrix for large clouds.
    for i in range(0, len(target), 128):
        a = target[i:i+128]
        for j in range(0, len(other), 1024):
            b = other[j:j+1024]
            dist2 = ((a*a).sum(1)[:, None] + (b*b).sum(1)[None, :] - 2*a @ b.T)
            nearest[i:i+len(a)] = np.minimum(nearest[i:i+len(a)], np.sqrt(np.maximum(dist2, 0)).min(1))
    return {'target_count': len(target), 'visible_target_count': int(visible.sum()),
            'clearance_min_px': float(nearest.min()),
            'clearance_p10_px': float(np.quantile(nearest, .1)),
            'clearance_median_px': float(np.median(nearest))}


def interpolate_tiles(before, after, progress):
    """Interpolate {id, xy, color} display records with identical stable IDs."""
    progress = float(_finite(progress))
    if not 0 <= progress <= 1:
        raise ValueError('Progress must be in [0,1]')
    def index(records):
        result = {row['id']: row for row in records}
        if len(result) != len(records):
            raise ValueError('Duplicate image identity')
        return result
    a, b = index(before), index(after)
    if not a or a.keys() != b.keys():
        raise ValueError('States must contain the same nonempty identity set')
    output = []
    for key in a:
        p, q = _finite(a[key]['xy']), _finite(b[key]['xy'])
        if p.shape != (2,) or q.shape != (2,):
            raise ValueError('Tile position must have two coordinates')
        c, d = np.array(ImageColor.getrgb(a[key]['color'])), np.array(ImageColor.getrgb(b[key]['color']))
        if c.shape != (3,) or d.shape != (3,):
            raise ValueError('Use RGB tile colors')
        color = np.rint(c*(1-progress) + d*progress).astype(int)
        output.append({'id': key, 'xy': (p*(1-progress) + q*progress).tolist(),
                       'color': '#%02x%02x%02x' % tuple(color)})
    return output


def validate_sequence_trace(states, image_ids):
    """Each state is a full permutation; measured quality may decrease.

    Trace schema: {order:[id,...], groups:[group_id,...], quality:number}.
    Quality's scientific definition and evidence belong in the project manifest.
    """
    ids = list(image_ids)
    if not ids or len(set(ids)) != len(ids) or not states:
        raise ValueError('Need unique IDs and at least one state')
    for state in states:
        order, groups = state['order'], state['groups']
        if len(order) != len(ids) or set(order) != set(ids) or len(groups) != len(ids):
            raise ValueError('A state lost, duplicated or introduced an identity')
        if not np.isfinite(float(state['quality'])):
            raise ValueError('Quality must be finite')
    return True
