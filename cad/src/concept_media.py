"""PVTrace concept media (TRL 3), generated from the parametric model in cad/src/model.py.

Run from the repo root:  python cad/src/concept_media.py
CONCEPT, NOT FOR FABRICATION.

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
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build123d import Box, Cylinder, Pos, Rot, Solid, Plane, Vector
from concept import Part, render_all
from model import PARAMS as P, build_parts

# ---------------- key dimensions (mm) ----------------
L, W, H = P["case_l"], P["case_w"], P["case_h"]
GZ = 30.0                         # gland height
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


M = build_parts()

# ---------------- leads and sensor pod ----------------
# MC4 mating point near the module's lower edge, where the module's own leads hang
MATE = [(250.0, 150.0, 35.0), (320.0, 150.0, 35.0)]
# 11 Test leads, 1 m, 4 mm2 double insulated, with MC4 connectors
leads = None
for (y0, m) in zip((-P["gland_y"], P["gland_y"]), MATE):
    run = path([(L / 2 + 12, y0, GZ), (L / 2 + 45, y0, 12), (m[0] - 20, y0 + 40, 12),
                (m[0], m[1] - 45, 20), (m[0], m[1] - 30, m[2])], 3.5)
    plug = Pos(m[0], m[1], m[2]) * Rot(-90, 0, 0) * Cylinder(9, 60)
    leads = run + plug if leads is None else leads + run + plug

# 12 Sensor pod: reference cell and shaded temperature probe, clipped to the module frame
POD_X = -420.0
pc = on_module(-48, 2, POD_X)
pod = Pos(*pc) * Rot(TILT, 0, 0) * M["pod"]
probe = path([on_module(8, -20, POD_X + 30), on_module(80, -40, POD_X + 30)], 3)
probe = probe + Pos(*on_module(80, -40, POD_X + 30)) * Box(20, 20, 8)
pod_cable = path([on_module(-40, -12, POD_X), (POD_X + 30, 150, 12),
                  (-L / 2 - 60, 35, 12), (-L / 2 - 12, 35, GZ)], 3)
pod_all = pod + probe + pod_cable

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
    Part("Enclosure body, IP54 ABS", M["body"], "#8B95A1", 1, (0, 0, 0)),
    Part("Enclosure lid with window", M["lid"] + M["window"], "#D1D5DB", 2, (0, 0, 330)),
    Part("Controller and 2.8 in display", M["controller"], "#0F766E", 3, scr(-60, 190)),
    Part("Measurement board (shunt, ADC)", M["meas"], "#16A34A", 4, scr(230, 150)),
    Part("Load capacitors, 3 x 2200 uF 160 V", M["caps"], "#1D4ED8", 5, scr(-110, -230)),
    Part("Load and discharge MOSFETs", M["fets"], "#7C3AED", 6, scr(90, 60)),
    Part("Discharge resistor, 22 ohm 50 W", M["dump_res"], "#B45309", 7, scr(10, -200)),
    Part("DC fuse, 20 A, and holder", M["fuse"], "#DC2626", 8, scr(190, -170)),
    Part("DC isolator, 2-pole", M["isolator"], "#F59E0B", 9, scr(200, 330)),
    Part("Li-ion 18650 cell and charger", M["battery"], "#C2410C", 10, scr(-20, -330)),
    Part("Test leads with MC4 connectors", leads, "#111827", 11, scr(250, 0)),
    Part("Sensor pod: reference cell, temperature", pod_all, "#0EA5E9", 12, scr(-40, -470)),
    Part("Isolation barrier (isolator, DC-DC)", M["isolation"], "#DB2777", 14, scr(40, 240)),
    Part("Display sun hood, printed", M["hood"], "#E5E7EB", 15, (0, 0, 470)),
]

if __name__ == "__main__":
    render_all(
        parts, project="PVTrace", title="Handheld IV curve tracer concept", dwg_no="PVT-DWG-010", rev="P3",
        key_figures=["Single modules and short strings to 100 V, 20 A",
                     "Capacitive load 6.6 mF: sweep about 20 to 68 ms (PVT-CAL-001)",
                     "Up to 33 J per sweep dumped in a 50 W resistor",
                     "Case 220 x 130 x 80 mm with sun hood; about 1.43 kg; isolated",
                     "$164 in parts (indicative; budget $165)"],
        scale_figure=False, context=context,
        cut_exclude=("Test leads with MC4 connectors", "Sensor pod: reference cell, temperature"),
        flow={"title": "one sweep, from panel to grade (calculated in PVT-CAL-001; energy in J for a 450 W module)", "unit": "J",
              "stages": [("Module under test", "about 50 V, 12 A"), ("Capacitor load", 7.9),
                         ("Sampled V-I pairs", "about 800 in 32 ms"), ("On-device analysis", "Pmax, FF, Rs, Rsh"),
                         ("STC translation", "IEC 60891"), ("Grade and log", "A, B, C or reject")],
              "losses": [(1, "Dump resistor heat", 7.9)]},
    )
    import shutil
    for d in Path("media").glob("_views*"):
        shutil.rmtree(d, ignore_errors=True)
