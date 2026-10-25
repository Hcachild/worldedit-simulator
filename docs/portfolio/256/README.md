# 256³ Image — Trefoil Knot

![Trefoil Knot](19_trefoil_256_iso.png)

A 256×256×256 reproduction of the trefoil-knot sweep shared by **imhols**. The
author's Lua builds the knot from a square cross-section transported along a
parametric curve; this version ports the same sweep to a deterministic Python
voxelizer so a 16.7M-cell canvas does not need 16.7M `//gen` evaluations.

## Reproduce

```bat
python tools\make_trefoil.py --out schematics\portfolio_19_trefoil_256.schem ^
  --frame frenet --rotation 75
```

The browser's **＋ → 256 × 256 × 256 超大画布** option can create the blank
canvas, but the generated file is already a ready-to-open `.schem`. Reload the
file list and open `portfolio_19_trefoil_256.schem`.

## Curve and sweep

```text
hx = S * (cos(t) + 2*cos((n-1)*t))
hy = 2*S*a*sin(n*t)
hz = S * (sin(t) - 2*sin((n-1)*t))
```

With `n=3`, `a=0.5`, this is the trefoil projection. At each segment the
generator builds a moving frame and a square cross-section:

```text
T = normalize(P(t+dt) - P(t))
frame = Frenet N/B  (default), parallel transported, or --frame projected
R' = N*cos(twist) + B*sin(twist)
U' = B*cos(twist) - N*sin(twist)
|lx| <= thickness && |ly| <= thickness && -0.5 <= lz <= seg_len+0.5
```

The original Lua uses a **projected** frame with one axis kept horizontal; that
is why its square can look axis-aligned. The default here is **Frenet**, which
uses the curve's curvature normal so the square turns with the actual 3D path.
`--frame parallel` minimizes twist instead, and `--frame projected` reproduces
the Lua frame.

Defaults for this render:

| Parameter | Value |
|---|---:|
| size | 256³ |
| knot order `n` | 3 |
| vertical ratio `a` | 0.5 |
| scale `S` | 30 |
| thickness | 8 blocks (square half-width) |
| step | 0.04 rad |
| rotation | 75° |
| full twists | 0 |
| frame | `frenet` |
| material | `minecraft:stone` |
| blocks | 221,143 |

The output is 180 × 80 × 179 blocks inside the 256 cube. `scale=30` is larger
than the author's 20 so the knot fills the bigger canvas; use `--scale 20
--thickness 8` for a closer-to-source 128-ish footprint.

## Camera

`19_trefoil_256_iso.json` records the exact orthographic camera. The image is
the app's 900×900 canvas capture, not a viewport screenshot with HUD or sidebar.
