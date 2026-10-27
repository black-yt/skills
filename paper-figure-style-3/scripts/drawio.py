"""Small native draw.io writer: shapes, editable text, groups and real edges.

Custom contours use draw.io's XML stencil language. No SVG/PNG is inserted.
All geometry is expressed in top-left pixel coordinates.
"""
from __future__ import annotations

import base64
import math
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree as ET
import zlib

INK = "#28313B"


def style_string(values):
    return ";".join(f"{key}={value}" for key, value in values.items()) + ";"


def stencil(path_commands: str, width=100, height=100):
    xml = (f'<shape name="editable-contour" w="{width}" h="{height}" '
           f'aspect="variable" strokewidth="inherit"><foreground>'
           f'<path>{path_commands}</path><fillstroke/></foreground></shape>')
    return stencil_xml(xml)


def stencil_xml(xml):
    ET.fromstring(xml)
    compressor = zlib.compressobj(wbits=-15)
    payload = compressor.compress(quote(xml, safe="~()*!.'").encode()) + compressor.flush()
    return "stencil(" + base64.b64encode(payload).decode() + ")"


class Diagram:
    def __init__(self, name, width, height):
        self.name, self.width, self.height = name, width, height
        self.model = ET.Element("mxGraphModel", {
            "dx": "0", "dy": "0", "grid": "0", "gridSize": "10",
            "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
            "fold": "1", "page": "0", "pageScale": "1",
            "pageWidth": str(width), "pageHeight": str(height),
            "math": "0", "shadow": "0", "background": "#FFFFFF",
        })
        self.root = ET.SubElement(self.model, "root")
        ET.SubElement(self.root, "mxCell", id="0")
        ET.SubElement(self.root, "mxCell", id="1", parent="0")
        self.ids = {"0", "1"}

    def _cell(self, identifier, **attributes):
        if identifier in self.ids:
            raise ValueError(f"duplicate cell ID: {identifier}")
        self.ids.add(identifier)
        return ET.SubElement(self.root, "mxCell", id=identifier,
                             **{k: str(v) for k, v in attributes.items()})

    def shape(self, identifier, x, y, width, height, *, kind="rectangle",
              fill="white", stroke=INK, sw=1.8, parent="1", sketch=True, **options):
        if width <= 0 or height <= 0:
            raise ValueError(f"{identifier}: shape dimensions must be positive")
        styles = dict(shape=kind, fillColor=fill, strokeColor=stroke,
                      strokeWidth=sw, rounded=0, html=0, whiteSpace="wrap")
        if sketch:
            styles.update(sketch=1, jiggle=.45, disableMultiStroke=1,
                          disableMultiStrokeFill=1, fillStyle="solid")
        styles.update(options)
        cell = self._cell(identifier, value="", style=style_string(styles),
                          vertex="1", parent=parent)
        ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y), width=str(width),
                      height=str(height), **{"as": "geometry"})
        return identifier

    def group(self, identifier, x, y, width, height, *, parent="1"):
        return self.shape(identifier, x, y, width, height, kind="group",
                          fill="none", stroke="none", parent=parent, sketch=False,
                          connectable=1, recursiveResize=1)

    def text(self, identifier, x, y, width, height, value, *, size=16,
             color=INK, bold=False, italic=False, align="center", parent="1",
             family="DejaVu Serif", **options):
        styles = dict(shape="text", fillColor="none", strokeColor="none",
                      html=0, whiteSpace="wrap", overflow="visible", spacing=0,
                      fontFamily=family, fontSize=size, fontColor=color,
                      fontStyle=int(bold) + 2 * int(italic), align=align,
                      verticalAlign="middle", resizable=1)
        styles.update(options)
        cell = self._cell(identifier, value=value, style=style_string(styles),
                          vertex="1", parent=parent)
        ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y), width=str(width),
                      height=str(height), **{"as": "geometry"})
        return identifier

    def contour(self, identifier, x, y, width, height, commands, **options):
        return self.shape(identifier, x, y, width, height,
                          kind=stencil(commands), **options)

    def polygon(self, identifier, points, **options):
        left, top = min(p[0] for p in points), min(p[1] for p in points)
        width = max(p[0] for p in points) - left
        height = max(p[1] for p in points) - top
        commands = []
        for index, (x, y) in enumerate(points):
            command = "move" if index == 0 else "line"
            commands.append(f'<{command} x="{(x-left)*100/width:.3f}" y="{(y-top)*100/height:.3f}"/>')
        commands.append("<close/>")
        return self.contour(identifier, left, top, width, height, "".join(commands), **options)

    def edge(self, identifier, source=None, target=None, *, start=None, end=None,
             points=(), color=INK, sw=1.8, arrow="classic", dashed=False,
             curved=False, exit=(1,.5), entry=(0,.5), parent="1", **options):
        styles = dict(edgeStyle="none", rounded=1, html=0,
                      strokeColor=color, strokeWidth=sw, endArrow=arrow,
                      endSize=7, endFill=1, startArrow="none", curved=int(curved),
                      dashed=int(dashed), dashPattern="6 4")
        if source:
            styles.update(exitX=exit[0], exitY=exit[1], exitPerimeter=1)
        if target:
            styles.update(entryX=entry[0], entryY=entry[1], entryPerimeter=1)
        styles.update(options)
        attributes = dict(value="", style=style_string(styles), edge="1", parent=parent)
        if source:
            attributes["source"] = source
        if target:
            attributes["target"] = target
        cell = self._cell(identifier, **attributes)
        geometry = ET.SubElement(cell, "mxGeometry", relative="1", **{"as":"geometry"})
        for value, kind in ((start,"sourcePoint"),(end,"targetPoint")):
            if value:
                ET.SubElement(geometry,"mxPoint",x=str(value[0]),y=str(value[1]),**{"as":kind})
        if points:
            array = ET.SubElement(geometry,"Array",**{"as":"points"})
            for x,y in points:
                ET.SubElement(array,"mxPoint",x=str(x),y=str(y))
        return identifier

    def line(self, identifier, points, **options):
        return self.edge(identifier, start=points[0], end=points[-1],
                         points=points[1:-1], arrow="none", **options)


def save(diagrams, path):
    root = ET.Element("mxfile", host="app.diagrams.net", agent="paper-figure-style-3")
    for index, diagram in enumerate(diagrams, 1):
        page = ET.SubElement(root,"diagram",id=f"figure-{index}",name=diagram.name)
        page.append(diagram.model)
    ET.indent(root, space="  ")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path


def gear_points(cx, cy, radius, teeth=12):
    result=[]
    for i in range(teeth*4):
        angle=2*math.pi*i/(teeth*4)
        r=radius*(1 if i%4 in (1,2) else .85)
        result.append((cx+r*math.cos(angle),cy+r*math.sin(angle)))
    return result
