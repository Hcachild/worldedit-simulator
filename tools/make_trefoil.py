"""Voxelize the imhols trefoil-knot sweep into a Sponge .schem.

This is a Python port of the author's Lua sweep: a square cross-section is
transported along the parametric knot, with an optional twist, and every block
whose centre falls inside the swept box is filled.

The default frame is Frenet, so the square visibly turns with the 3D curve
instead of keeping one axis horizontal.  Use --frame parallel for a
rotation-minimizing sweep, or --frame projected for the original Lua frame.
"""
import argparse
import math
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from core.schematic import write_schem  # noqa: E402


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def length(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def normalize(v):
    mag = length(v)
    if mag <= 1e-12:
        return (0.0, 0.0, 0.0)
    return (v[0] / mag, v[1] / mag, v[2] / mag)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def knot_point(t, scale, vertical_ratio, knot_order, rotation):
    nm1 = knot_order - 1
    hx = scale * (math.cos(t) + 2 * math.cos(nm1 * t))
    hy = scale * 2 * vertical_ratio * math.sin(knot_order * t)
    hz = scale * (math.sin(t) - 2 * math.sin(nm1 * t))
    cos_r, sin_r = math.cos(rotation), math.sin(rotation)
    return (
        hx * cos_r - hz * sin_r,
        hy,
        hx * sin_r + hz * cos_r,
    )


def knot_derivatives(t, scale, vertical_ratio, knot_order, rotation):
    nm1 = knot_order - 1
    hx = scale * (math.cos(t) + 2 * math.cos(nm1 * t))
    hy = scale * 2 * vertical_ratio * math.sin(knot_order * t)
    hz = scale * (math.sin(t) - 2 * math.sin(nm1 * t))
    dhx = scale * (-math.sin(t) - 2 * nm1 * math.sin(nm1 * t))
    dhy = scale * 2 * vertical_ratio * knot_order * math.cos(knot_order * t)
    dhz = scale * (math.cos(t) - 2 * nm1 * math.cos(nm1 * t))
    ddhx = scale * (-math.cos(t) - 2 * nm1 * nm1 * math.cos(nm1 * t))
    ddhy = -scale * 2 * vertical_ratio * knot_order * knot_order * math.sin(knot_order * t)
    ddhz = scale * (-math.sin(t) + 2 * nm1 * nm1 * math.sin(nm1 * t))
    cos_r, sin_r = math.cos(rotation), math.sin(rotation)
    p = (hx * cos_r - hz * sin_r, hy, hx * sin_r + hz * cos_r)
    dp = (dhx * cos_r - dhz * sin_r, dhy, dhx * sin_r + dhz * cos_r)
    ddp = (ddhx * cos_r - ddhz * sin_r, ddhy, ddhx * sin_r + ddhz * cos_r)
    return p, dp, ddp


def build(args):
    size = args.size
    center = size / 2.0 - 0.5
    two_pi = 2 * math.pi
    rotation = math.radians(args.rotation)
    twist = args.twist * two_pi
    data = bytearray(size * size * size)
    palette = {"minecraft:air": 0, args.material: 1}
    thickness = args.thickness
    total = 0
    bounds = [size, -1, size, -1, size, -1]
    previous_normal = None

    t = 0.0
    while t < two_pi:
        dt = min(args.step, two_pi - t)
        if dt < 0.001:
            break
        p, dp, ddp = knot_derivatives(
            t, args.scale, args.vertical_ratio, args.order, rotation
        )
        q = knot_point(t + dt, args.scale, args.vertical_ratio, args.order, rotation)
        p = (p[0] + center, p[1] + center, p[2] + center)
        q = (q[0] + center, q[1] + center, q[2] + center)
        delta = (q[0] - p[0], q[1] - p[1], q[2] - p[2])
        seg_len = length(delta)
        tangent = normalize(delta)

        up = (0.0, 1.0, 0.0)
        if abs(tangent[1]) > 0.9999:
            up = (1.0, 0.0, 0.0)
        projected = normalize(cross(tangent, up))

        if args.frame == "frenet":
            curvature = (
                ddp[0] - dot(ddp, tangent) * tangent[0],
                ddp[1] - dot(ddp, tangent) * tangent[1],
                ddp[2] - dot(ddp, tangent) * tangent[2],
            )
            normal = normalize(curvature)
            if length(normal) < 0.5:
                normal = projected
        elif args.frame == "parallel":
            if previous_normal is None:
                normal = projected
            else:
                projected_prev = (
                    previous_normal[0] - dot(previous_normal, tangent) * tangent[0],
                    previous_normal[1] - dot(previous_normal, tangent) * tangent[1],
                    previous_normal[2] - dot(previous_normal, tangent) * tangent[2],
                )
                normal = normalize(projected_prev)
                if length(normal) < 0.5:
                    normal = projected
        else:
            normal = projected
        binormal = normalize(cross(tangent, normal))
        if length(binormal) < 0.5:
            binormal = normalize(cross(tangent, projected))
        normal = normalize(cross(binormal, tangent))
        previous_normal = normal

        twist_angle = (t / two_pi) * twist
        ct, st = math.cos(twist_angle), math.sin(twist_angle)
        tr = (
            normal[0] * ct + binormal[0] * st,
            normal[1] * ct + binormal[1] * st,
            normal[2] * ct + binormal[2] * st,
        )
        tu = (
            binormal[0] * ct - normal[0] * st,
            binormal[1] * ct - normal[1] * st,
            binormal[2] * ct - normal[2] * st,
        )

        min_x = max(0, math.floor(min(p[0], q[0]) - thickness - 1))
        max_x = min(size - 1, math.ceil(max(p[0], q[0]) + thickness + 1))
        min_y = max(0, math.floor(min(p[1], q[1]) - thickness - 1))
        max_y = min(size - 1, math.ceil(max(p[1], q[1]) + thickness + 1))
        min_z = max(0, math.floor(min(p[2], q[2]) - thickness - 1))
        max_z = min(size - 1, math.ceil(max(p[2], q[2]) + thickness + 1))

        for bx in range(min_x, max_x + 1):
            ox = bx + 0.5 - p[0]
            for by in range(min_y, max_y + 1):
                oy = by + 0.5 - p[1]
                for bz in range(min_z, max_z + 1):
                    oz = bz + 0.5 - p[2]
                    lx = ox * tr[0] + oy * tr[1] + oz * tr[2]
                    ly = ox * tu[0] + oy * tu[1] + oz * tu[2]
                    lz = ox * tangent[0] + oy * tangent[1] + oz * tangent[2]
                    if (
                        -thickness <= lx <= thickness
                        and -thickness <= ly <= thickness
                        and -0.5 <= lz <= seg_len + 0.5
                    ):
                        index = bx + bz * size + by * size * size
                        if data[index] == 0:
                            data[index] = 1
                            total += 1
                            bounds[0] = min(bounds[0], bx)
                            bounds[1] = max(bounds[1], bx)
                            bounds[2] = min(bounds[2], by)
                            bounds[3] = max(bounds[3], by)
                            bounds[4] = min(bounds[4], bz)
                            bounds[5] = max(bounds[5], bz)
        t += args.step

    if total == 0:
        raise SystemExit("trefoil generated no blocks; check scale/thickness")
    return data, palette, total, bounds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="schematics/portfolio_19_trefoil_256.schem")
    parser.add_argument("--size", type=int, default=256)
    parser.add_argument("--scale", type=float, default=30.0)
    parser.add_argument("--vertical-ratio", type=float, default=0.5)
    parser.add_argument("--thickness", type=int, default=8)
    parser.add_argument("--step", type=float, default=0.04)
    parser.add_argument("--rotation", type=float, default=0.0)
    parser.add_argument("--twist", type=int, default=0)
    parser.add_argument("--frame", choices=("frenet", "parallel", "projected"), default="frenet",
                        help="cross-section frame; frenet follows curve torsion, projected is the source Lua frame")
    parser.add_argument("--order", type=int, default=3)
    parser.add_argument("--material", default="minecraft:stone")
    parser.add_argument("--data-version", type=int, default=3955)
    args = parser.parse_args()
    if not 1 <= args.size <= 256:
        raise SystemExit("--size must be 1..256")
    if args.thickness < 1:
        raise SystemExit("--thickness must be >= 1")
    if args.order < 2:
        raise SystemExit("--order must be >= 2")
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    data, palette, total, bounds = build(args)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_schem(
        out,
        args.size,
        args.size,
        args.size,
        palette,
        bytes(data),
        data_version=args.data_version,
    )
    print(
        f"wrote {out} ({out.stat().st_size} bytes, {total} blocks, "
        f"bounds x={bounds[0]}..{bounds[1]} y={bounds[2]}..{bounds[3]} z={bounds[4]}..{bounds[5]})"
    )


if __name__ == "__main__":
    main()
