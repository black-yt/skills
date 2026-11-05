#!/usr/bin/env python3
"""Animate actual image identities from a stack to a cropped mosaic and full reveal."""
import argparse
import hashlib
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageOps

from media_common import (load_config, ffmpeg_bin, check_output, frame_rate, FrameWriter,
                          smooth, write_json, validate)


class CardScene:
    def __init__(self, cfg, root):
        self.cfg, self.root = cfg, root
        self.size, self.fps = tuple(cfg["canvas"]), frame_rate(cfg.get("fps", 20))
        if cfg.get("background"):
            self.background = ImageOps.fit(Image.open(root/cfg["background"]).convert("RGB"),
                                           self.size, Image.Resampling.LANCZOS)
        else:
            self.background = Image.new("RGB", self.size, cfg.get("background_color", "#f6e2ce"))
        grid = cfg["grid"]
        self.rows, self.cols = int(grid["rows"]), int(grid["columns"])
        self.rect = tuple(grid["rect"])
        x, y, w, h = self.rect
        if min(x, y)<0 or min(w, h)<=0 or x+w>self.size[0] or y+h>self.size[1]:
            raise ValueError("Grid rectangle is outside canvas")
        records = cfg.get("images")
        if records is None:
            records = [{"id": str(p.relative_to(root)), "source": str(p.relative_to(root))}
                       for p in sorted(root.glob(cfg["images_glob"])) if p.is_file()]
        self.records = records
        if self.rows<=0 or self.cols<=0 or len(records)!=self.rows*self.cols:
            raise ValueError("Grid capacity must equal the number of supplied images")
        if len({r["id"] for r in records})!=len(records):
            raise ValueError("Image IDs must be unique")
        self.paths = [(root/r["source"]).resolve() for r in records]
        self.full, self.textures = [], []
        self.atlas = Image.new("RGBA", (w*2, h*2))
        gap = grid.get("gap", 4)
        for i, path in enumerate(self.paths):
            row, col = divmod(i, self.cols)
            a, b = round(col*w/self.cols+gap/2), round(row*h/self.rows+gap/2)
            c, d = round((col+1)*w/self.cols-gap/2), round((row+1)*h/self.rows-gap/2)
            if c<=a or d<=b:
                raise ValueError("Grid gap leaves no image area")
            self.full.append([[a, b], [c, b], [c, d], [a, d]])
            im = ImageOps.exif_transpose(Image.open(path)).convert("RGBA")
            card = Image.new("RGB", ((c-a)*2, (d-b)*2), cfg.get("card_background", "black"))
            im = ImageOps.contain(im, card.size, Image.Resampling.LANCZOS)
            card.paste(im, ((card.width-im.width)//2, (card.height-im.height)//2), im)
            self.atlas.paste(card, (a*2, b*2))
            self.textures.append(card)
        self.full = np.array(self.full, dtype=float)
        near = cfg["first_view"]
        r0, c0, nr, nc = (int(near[k]) for k in ["row", "column", "rows", "columns"])
        if min(r0, c0)<0 or min(nr, nc)<=0 or r0+nr>self.rows or c0+nc>self.cols:
            raise ValueError("first_view must select complete grid rows and columns")
        self.first_ids = [r*self.cols+c for r in range(r0, r0+nr) for c in range(c0, c0+nc)]
        group = self.full[self.first_ids]
        lo, hi = group.min(axis=(0, 1)), group.max(axis=(0, 1))
        self.center = (lo+hi)/2
        self.final_center = np.array([w/2, h/2])
        margin = near.get("margin", 4)
        self.zoom = min((w-2*margin)/(hi-lo)[0], (h-2*margin)/(hi-lo)[1])
        if self.zoom<1:
            raise ValueError("first_view plus margin cannot require a wider view than the full grid")
        scope = cfg.get("flight_scope", "first")
        if scope not in {"first", "all"}:
            raise ValueError("flight_scope must be first or all")
        self.flight_ids = self.first_ids if scope=="first" else list(range(len(records)))
        stack = cfg["stack"]
        quad = np.asarray(stack["quad"], float)-[x, y]
        if quad.shape!=(4, 2):
            raise ValueError("Stack quad must have four canvas-coordinate corners")
        shift = np.asarray(stack.get("depth_offset", [-25, -100]), float)
        self.start = np.array([quad+shift*i/max(1, len(self.flight_ids)-1) for i in range(len(self.flight_ids))])
        self.target = self.final_center+self.zoom*(self.full[self.flight_ids]-self.center)
        self.representatives = np.unique(np.linspace(0, len(self.flight_ids)-1,
            min(len(self.flight_ids), stack.get("visible_layers", 12))).astype(int)).tolist()
        self.phases = []
        start = 0
        for phase in ["stack", "spread", "near_hold", "pullback", "full_hold"]:
            count = round(float(cfg["timing"][phase])*float(self.fps))
            if count<1:
                raise ValueError("Each animation phase must contain at least one frame")
            self.phases.append((phase, start, start+count))
            start += count
        self.frames = start
        self.audit = []

    def camera(self, zoom):
        u = (zoom-1)/(self.zoom-1) if self.zoom>1 else 0
        return self.final_center+(self.center-self.final_center)*u

    def grid(self, zoom, allowed=None):
        _, _, w, h = self.rect
        center = self.camera(zoom)
        quads = self.final_center+zoom*(self.full-center)
        lo, hi = quads.min(axis=1), quads.max(axis=1)
        edge = self.cfg.get("edge_policy", "whole")
        if edge=="whole":
            ids = np.flatnonzero((lo[:, 0]>=0)&(lo[:, 1]>=0)&(hi[:, 0]<=w)&(hi[:, 1]<=h)).tolist()
        elif edge=="clip":
            ids = list(range(len(self.records)))
        else:
            raise ValueError("edge_policy must be whole or clip")
        if allowed is not None:
            ids = [i for i in ids if i in allowed]
        mask = Image.new("L", self.atlas.size)
        d = ImageDraw.Draw(mask)
        for i in ids:
            a, b = self.full[i, 0]; c, e = self.full[i, 2]
            d.rectangle((round(a*2), round(b*2), round(c*2)-1, round(e*2)-1), fill=255)
        atlas = self.atlas.copy()
        atlas.putalpha(ImageChops.multiply(mask, atlas.getchannel("A")))
        layer = atlas.transform((w, h), Image.Transform.AFFINE,
            (2/zoom, 0, 2*(center[0]-w/2/zoom), 0, 2/zoom, 2*(center[1]-h/2/zoom)), Image.Resampling.BICUBIC)
        im = self.background.copy(); im.paste(layer, self.rect[:2], layer.getchannel("A"))
        self.audit.append({"zoom": float(zoom), "visible_ids": [self.records[i]["id"] for i in ids],
                           "partial_cards_allowed": edge=="clip"})
        return im

    def quads(self, progress):
        u = smooth(progress)
        return self.start*(1-u)+self.target*u

    def frame(self, index):
        name, a, b = next(p for p in self.phases if p[1]<=index<p[2])
        progress = (index-a)/max(1, b-a-1)
        if name=="near_hold":
            return self.grid(self.zoom, set(self.first_ids))
        if name=="pullback":
            return self.grid(self.zoom+(1-self.zoom)*smooth(progress))
        if name=="full_hold":
            return self.grid(1)
        quads = self.start if name=="stack" else self.quads(progress)
        # Every identity has a trajectory. While the stack is still, the hidden
        # inner layers need not all be rasterized. Nothing fades in at its target.
        ranks = self.representatives if name=="stack" else self.visible_ranks(quads)
        im = self.background.copy()
        x, y, w, h = self.rect
        region = im.crop((x, y, x+w, y+h))
        for rank in ranks:
            project(region, self.textures[self.flight_ids[rank]], quads[rank])
        im.paste(region, (x, y))
        return im

    def visible_ranks(self, quads):
        """Cull covered raster work, while retaining every identity's trajectory."""
        factor = self.cfg.get("occlusion_grid", 4)
        if not factor:
            return range(len(quads))
        if factor<1:
            raise ValueError("occlusion_grid must be zero or at least one pixel")
        w, h = self.rect[2:]
        width, height = math.ceil(w/factor), math.ceil(h/factor)
        coverage = np.zeros((height, width), dtype="uint8")
        chosen = []
        for rank in reversed(range(len(quads))):
            q = quads[rank]/factor
            lo = np.maximum(0, np.floor(q.min(axis=0))).astype(int)
            hi = np.minimum([width, height], np.ceil(q.max(axis=0))+1).astype(int)
            if np.any(hi<=lo):
                continue
            mask = Image.new("L", tuple(hi-lo))
            ImageDraw.Draw(mask).polygon([tuple(p-lo) for p in q], fill=255)
            mask = np.asarray(mask)
            part = coverage[lo[1]:hi[1], lo[0]:hi[0]]
            if np.any((mask!=0)&(part==0)):
                chosen.append(rank)
            np.maximum(part, mask, out=part)
        return sorted(chosen)


def project(canvas, texture, quad):
    """Warp only a card's clipped bounding box, never a full canvas per card."""
    lo = np.maximum(0, np.floor(quad.min(axis=0))).astype(int)
    hi = np.minimum(canvas.size, np.ceil(quad.max(axis=0))).astype(int)
    if np.any(hi<=lo):
        return
    q = quad-lo
    rows, rhs = [], []
    for (x, y), (u, v) in zip(q, [(0, 0), (texture.width, 0), texture.size, (0, texture.height)]):
        rows += [[x,y,1,0,0,0,-u*x,-u*y], [0,0,0,x,y,1,-v*x,-v*y]]
        rhs += [u, v]
    coeff = np.linalg.solve(rows, rhs)
    piece = texture.convert("RGBA").transform(tuple(hi-lo), Image.Transform.PERSPECTIVE,
                                              coeff, Image.Resampling.BICUBIC)
    canvas.paste(piece, tuple(lo), piece.getchannel("A"))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True)
    p.add_argument("--ffmpeg")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--preview-at", type=float)
    args = p.parse_args()
    cfg, root = load_config(args.config)
    scene = CardScene(cfg, root)
    output = check_output(root/cfg["output"], scene.paths, args.overwrite)
    if args.preview_at is not None:
        n = round(args.preview_at*float(scene.fps))
        if not 0<=n<scene.frames:
            raise ValueError("Preview is outside the scene")
        target = check_output(output.with_suffix(f".preview-{n}.png"), scene.paths, args.overwrite)
        scene.frame(n).save(target)
        print(target)
        return
    ffmpeg = ffmpeg_bin(args.ffmpeg)
    with FrameWriter(ffmpeg, output, scene.size, scene.fps, cfg.get("encoding")) as writer:
        for n in range(scene.frames):
            writer.write(scene.frame(n))
    report = validate(ffmpeg, output, scene.frames/float(scene.fps))
    write_json(output.with_suffix(".animation.json"), {
        "validation": report, "phases": scene.phases, "flight_scope": cfg.get("flight_scope", "first"),
        "flight_ids": [scene.records[i]["id"] for i in scene.flight_ids],
        "trajectories": [{"id": scene.records[i]["id"], "stack_quad": scene.start[k].tolist(),
                           "near_quad": scene.target[k].tolist()} for k, i in enumerate(scene.flight_ids)],
        "source_images": [{"id": r["id"], "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                          for r, path in zip(scene.records, scene.paths)],
        "visibility": scene.audit, "mosaic_target_fade_used": False})
    print(output)


if __name__=="__main__":
    main()
