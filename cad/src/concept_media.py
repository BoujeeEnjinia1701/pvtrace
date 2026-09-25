"""PVTrace concept massing model and media (TRL 2).

Run from the repo root:  python cad/src/concept_media.py
Proportions and main parts only; CONCEPT, NOT FOR FABRICATION.

Coordinates in mm. Z up, ground at Z = 0. The handheld tracer lies on the
ground in front of a PV module on a low tilted stand, with its MC4 test leads
mated to the module's own leads and its sensor pod clipped to the module's
lower frame edge so the reference cell lies in the module plane. Grey parts
(module, stand, module leads) are context for scale and carry no BOM number;
every colored part carries the BOM line number used in bom/bom.csv.
"""
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".kit"))
from build123d import Box, Cylinder, Pos, Rot, Solid, Plane, Vector
from concept import Part, render_all

# ---------------- key dimensions (mm) ----------------
L, W, H = 200.0, 120.0, 75.0      # enclosure outside, X x Y x Z
WALL = 3.0
Z_SPLIT = 50.0                    # body and lid parting line
MOD_L, MOD_W, MOD_T = 1722.0, 1134.0, 30.0   # common 400 to 450 W module, landscape
TILT = 30.0                       # module tilt on its stand (degrees from horizontal)
EDGE = (250.0, 300.0)             # (y, z) of the module's lower edge
t = math.radians(TILT)
U = (0.0, math.cos(t), math.sin(t))      # up-slope direction in the module plane
N = (0.0, -math.sin(t), math.cos(t))     # module front normal


def rod(a, b, r):
    """Round bar or cable between two 3D points."""
    a = Vector(*a); b = Vector(*b); d = b - a
    return Solid.make_cylinder(r, d.length, Plane(origin=a, z_dir=d.normalized()))


def path(points, r):
    """Cable along a polyline, with a ball at each bend so it reads as one run."""
    from build123d import Sphere
    s = None
    for a, b in zip(points[:-1], points[1:]):
        seg = rod(a, b, r)
        s = seg if s is None else s + seg
    for p in points[1:-1]:
        s = s + Pos(*p) * Sphere(r)
    return s


def on_module(s, n=0.0, x=0.0):
    """Point at slope distance s from the lower edge and offset n along the front normal."""
    return (x, EDGE[0] + s * U[1] + n * N[1], EDGE[1] + s * U[2] + n * N[2])


# ---------------- enclosure ----------------
# 1 Enclosure body (lower shell), IP54 ABS handheld case with rubber corner bumpers
body = (Pos(0, 0, Z_SPLIT / 2) * Box(L, W, Z_SPLIT)
        - Pos(0, 0, Z_SPLIT / 2 + WALL) * Box(L - 2 * WALL, W - 2 * WALL, Z_SPLIT))
for sx in (-1, 1):
    for sy in (-1, 1):
        body = body + Pos(sx * (L / 2 - 6), sy * (W / 2 - 6), 20) * Box(16, 16, 40)
# glands: two for the test leads on the +X end, one for the sensor cable on the -X end
for y in (-22, 22):
    body = body + Pos(L / 2 + 6, y, 28) * Rot(0, 90, 0) * Cylinder(9, 12)
body = body + Pos(-L / 2 - 6, 30, 28) * Rot(0, 90, 0) * Cylinder(7, 12)

# 2 Enclosure lid with display window
lid_h = H - Z_SPLIT
lid = (Pos(0, 0, Z_SPLIT + lid_h / 2) * Box(L, W, lid_h)
       - Pos(0, 0, Z_SPLIT + lid_h / 2 - WALL) * Box(L - 2 * WALL, W - 2 * WALL, lid_h)
       - Pos(-40, 0, H - 1) * Box(78, 56, 4))
window = Pos(-40, 0, H - 1.5) * Box(78, 56, 1.5)

# 3 Controller and display board (ESP32 with 2.8 in TFT, microSD) under the lid window
ctrl = Pos(-40, 0, H - WALL - 7) * Box(90, 62, 12) + window

# 4 Measurement board: shunt, current amplifier, divider, dual 12-bit ADC
meas = Pos(62, 22, WALL + 8) * Box(64, 46, 12)

# 5 Load capacitors, 2 x 2200 uF 160 V, lying along X
caps = None
for y in (-22, 20):
    c = Pos(-60, y, WALL + 17.5) * Rot(0, 90, 0) * Cylinder(17.5, 62)
    caps = c if caps is None else caps + c

# 6 Load and discharge MOSFETs on an aluminium bar, with gate driver
fets = Pos(8, 26, WALL + 12.5) * Box(40, 16, 25)

# 7 Discharge resistor, 22 ohm 50 W aluminium clad
res = Pos(8, -30, WALL + 8) * Box(50, 30, 16)

# 8 DC fuse, 20 A, in a 10 x 38 mm holder
fuse = Pos(62, -30, WALL + 12) * Box(60, 20, 24)

# 9 DC isolator, 2-pole: body under the lid, rotary knob on top
iso = (Pos(62, 22, 51.5) * Cylinder(15, 41)
       + Pos(62, 22, H + 6) * Cylinder(14, 12)
       + Pos(62, 22, H + 14) * Box(34, 8, 8))

# 10 Li-ion 18650 cell in a holder with USB-C charger and protection
cell = (Pos(-60, 47, WALL + 10) * Box(78, 18, 18)
        + Pos(-60, 47, WALL + 12) * Rot(0, 90, 0) * Cylinder(9, 65))

# ---------------- leads and sensor pod ----------------
# MC4 mating point near the module's lower edge, where the module's own leads hang
MATE = [(250.0, 150.0, 35.0), (320.0, 150.0, 35.0)]
# 11 Test leads, 1 m, 4 mm2 double insulated, with MC4 connectors
leads = None
for (y0, m) in zip((-22, 22), MATE):
    run = path([(L / 2 + 12, y0, 28), (L / 2 + 45, y0, 12), (m[0] - 20, y0 + 40, 12),
                (m[0], m[1] - 45, 20), (m[0], m[1] - 30, m[2])], 3.5)
    plug = Pos(m[0], m[1], m[2]) * Rot(-90, 0, 0) * Cylinder(9, 60)
    leads = run + plug if leads is None else leads + run + plug

# 12 Sensor pod: reference cell and shaded temperature probe, clipped to the module frame
POD_X = -420.0
pc = on_module(-48, 2, POD_X)
pod = Pos(*pc) * Rot(TILT, 0, 0) * Box(100, 70, 22)
refcell = Pos(*on_module(-48, 13.5, POD_X)) * Rot(TILT, 0, 0) * Box(80, 50, 1.5)
clip = Pos(*on_module(0, 0, POD_X)) * Rot(TILT, 0, 0) * Box(40, 26, 44)
probe = path([on_module(8, -20, POD_X + 30), on_module(80, -40, POD_X + 30)], 3)
probe = probe + Pos(*on_module(80, -40, POD_X + 30)) * Box(20, 20, 8)
pod_cable = path([on_module(-40, -12, POD_X), (POD_X + 30, 150, 12),
                  (-L / 2 - 60, 30, 12), (-L / 2 - 12, 30, 28)], 3)
pod_all = pod + refcell + clip + probe + pod_cable

# ---------------- context (grey, hero only) ----------------
module = Pos(*on_module(MOD_W / 2, MOD_T / 2)) * Rot(TILT, 0, 0) * Box(MOD_L, MOD_W, MOD_T)
stand = None
for x in (-700, 700):
    low = on_module(120, 0, x); high = on_module(MOD_W - 150, 0, x)
    legs = (rod((x, low[1], 0), low, 16) + rod((x, high[1], 0), high, 16)
            + rod((x, low[1], 0), (x, high[1], 0), 12))
    stand = legs if stand is None else stand + legs
jbox = on_module(MOD_W * 0.8, -20, 0)
mod_leads = None
for m, dx in zip(MATE, (-60, 60)):
    back = on_module(120, -60, m[0] - 20)
    run = path([(jbox[0] + dx, jbox[1], jbox[2]), back, (m[0], m[1] + 90, 60),
                (m[0], m[1] + 30, m[2])], 3.5)
    mod_leads = run if mod_leads is None else mod_leads + run
context = [Part("PV module under test on a stand, with its own leads", module + stand + mod_leads, "#C8CDD3")]

# Exploded offsets set in screen terms for the default camera (elevation 24, azimuth -58):
# sx to the right, sy up, t toward the viewer (mm).
_e, _a = math.radians(24), math.radians(-58)
_d = (-math.cos(_e) * math.cos(_a), -math.cos(_e) * math.sin(_a), -math.sin(_e))
_r = (_d[1], -_d[0], 0.0); _rn = math.hypot(*_r); _r = tuple(v / _rn for v in _r)
_u = (_r[1] * _d[2] - _r[2] * _d[1], _r[2] * _d[0] - _r[0] * _d[2], _r[0] * _d[1] - _r[1] * _d[0])


def scr(sx, sy, tv=0.0):
    return tuple(sx * _r[i] + sy * _u[i] - tv * _d[i] for i in range(3))


parts = [
    Part("Enclosure body, IP54 ABS", body, "#374151", 1, (0, 0, 0)),
    Part("Enclosure lid with window", lid, "#D1D5DB", 2, (0, 0, 330)),
    Part("Controller and 2.8 in display", ctrl, "#0F766E", 3, scr(0, 190)),
    Part("Measurement board (shunt, ADC)", meas, "#16A34A", 4, scr(230, 150)),
    Part("Load capacitors, 2 x 2200 uF 160 V", caps, "#1D4ED8", 5, scr(-120, -150)),
    Part("Load and discharge MOSFETs", fets, "#7C3AED", 6, scr(100, 100)),
    Part("Discharge resistor, 22 ohm 50 W", res, "#B45309", 7, scr(10, -200)),
    Part("DC fuse, 20 A, and holder", fuse, "#DC2626", 8, scr(190, -170)),
    Part("DC isolator, 2-pole", iso, "#F59E0B", 9, scr(200, 330)),
    Part("Li-ion 18650 cell and charger", cell, "#C2410C", 10, scr(-20, -330)),
    Part("Test leads with MC4 connectors", leads, "#111827", 11, scr(250, 0)),
    Part("Sensor pod: reference cell, temperature", pod_all, "#0EA5E9", 12, scr(-40, -470)),
]

if __name__ == "__main__":
    render_all(
        parts, project="PVTrace", title="Handheld IV curve tracer concept", dwg_no="PVT-DWG-010",
        key_figures=["Single modules and short strings to 100 V, 20 A",
                     "Capacitive load 4.4 mF: sweep about 13 to 43 ms (estimate)",
                     "Up to 22 J per sweep dumped in a 50 W resistor (estimate)",
                     "Enclosure about 200 x 120 x 75 mm; about 1.35 kg (estimate)",
                     "About $149 in parts (indicative)"],
        scale_figure=False, context=context,
        cut_exclude=("Test leads with MC4 connectors", "Sensor pod: reference cell, temperature"),
        flow={"title": "one sweep, from panel to grade (estimates; energy in J for a 450 W module)", "unit": "J",
              "stages": [("Module under test", "about 50 V, 12 A"), ("Capacitor load", 5.4),
                         ("Sampled V-I pairs", "about 500 in 21 ms"), ("On-device analysis", "Pmax, FF, Rs, Rsh"),
                         ("STC translation", "IEC 60891"), ("Grade and log", "A, B, C or reject")],
              "losses": [(1, "Bleed resistor heat", 5.4)]},
    )
    import shutil
    for d in Path("media").glob("_views*"):
        shutil.rmtree(d, ignore_errors=True)
