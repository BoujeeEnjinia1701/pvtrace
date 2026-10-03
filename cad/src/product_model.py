"""PVTrace product appearance model (build123d), TRL 3.

Finished-product look for photoreal renders: filleted IP54 case and lid with a parting-line
groove, rubber corner boots and ribbed side grips, cable glands, clear display window over a
lit 2.8 in screen showing an IV curve, printed sun hood, membrane keypad with status LEDs,
DC isolator with a red handle, lid screws, raised labels, red and black test leads with MC4
connectors, and visible internals (capacitor bank, load stage and heat sink, boards, cell).
The "in-use" view adds a clay hand holding the tracer beside the corner of a small PV module.
APPEARANCE MODEL ONLY: no tolerances, no fabrication detail. CONCEPT, NOT FOR FABRICATION.

Every main dimension and interface comes from PARAMS and build_parts() in model.py
(model.py has no derived() function; its envelopes are used directly).
Axes as model.py: X along the case length (test lead glands at +X, sensor gland at -X),
Y across the case (user side, where the sun hood opens, is -Y), Z up, case floor at Z = 0.

    from product_model import product_parts
    for p in product_parts(): print(p["name"], p["group"], p["material"])
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / ".kit"))

from build123d import (Axis, Box, Circle, Compound, Cylinder, Edge, Plane, Pos, RectangleRounded,
                       RegularPolygon, Rot, Solid, Sphere, Spline, Text, Vector, extrude, fillet, sweep)
from model import PARAMS, build_components, build_parts, derived

TITLE = "PVTrace: handheld solar panel IV curve tracer"

RENDER_VIEWS = [
    {"name": "hero", "groups": ["shell", "internal"], "explode": False, "el": 30, "az": -40,
     "note": "Product render from the front right and above (about 30 deg elevation); lit screen under "
             "the sun hood at left, DC isolator and MC4 test leads at right"},
    {"name": "exploded", "groups": ["shell", "internal", "accessory"], "explode": True, "el": 28, "az": -55,
     "note": "Exploded view from the front right and above (about 28 deg elevation): sun hood, lid and "
             "window, display board, load stage and heat sink, capacitor bank, measurement and isolation "
             "boards, fuse, isolator, 18650 cell, case body, test leads and sensor pod"},
    {"name": "in-use", "groups": ["shell", "internal", "context"], "explode": False, "el": 26, "az": -58,
     "note": "In use, from the front right and above (about 26 deg elevation): tracer resting in the "
             "left hand beside the corner of a small PV module, test leads mated to the module's leads"},
]

# Colours (restrained product palette; accent from the kit)
C_BODY = "#D3D7DC"
C_LID = "#E6E8EB"
C_HOOD = "#CBD0D6"
C_RUBBER = "#2B2F36"
C_ACCENT = "#0F766E"
C_DARK = "#1C1F24"
C_METAL = "#B8BEC6"
C_ALU = "#A9B0B8"
C_WINDOW = "#DCEBF5"
C_SCREEN = "#0E2436"
C_CURVE = "#5EEAD4"
C_POWER = "#FBBF24"
C_GRID = "#35506A"
C_RED = "#B91C1C"
C_PCB = "#1A1D21"
C_PCB_GREEN = "#1F5134"
C_CHIP = "#111827"
C_CAP = "#1E3A8A"
C_CELL = "#1F4E8C"
C_CLAY = "#A9ADB2"
C_PV_CELL = "#1E2A44"
C_PV_BACK = "#E9ECEF"
C_WOOD = "#B08A5A"

# Appearance-only detail sizes (mm)
R_PLAN = 10.0            # plan radius of the vertical case edges
FIL_TOP = 4.0            # lid top edge
FIL_BOT = 3.0            # body bottom edge
GROOVE = 0.8             # parting-line groove width and depth
BOOT = 18.0              # rubber corner boot, square, centred on each case corner (model: 14 mm bumper)
LID_SCREWS = [(-96.0, -50.0), (-96.0, 50.0), (96.0, -50.0), (96.0, 50.0)]
LEAD_R = 3.5             # 4 mm2 double-insulated PV cable
MC4_R = 8.0


def _fillet_try(shape, edges, radii):
    """Fillet `edges` with the first radius that gives a valid solid; else return the input."""
    edges = list(edges)
    if not edges:
        return shape
    for r in radii:
        try:
            out = fillet(edges, r)
            if out.is_valid and out.volume > 0:
                return out
        except Exception:
            pass
    return shape


def _prism(L, W, r, z0, h, x=0.0, y=0.0):
    """Rounded-rectangle prism in plan, from z0 up by h."""
    r = max(min(r, min(L, W) / 2 - 0.01), 0.01)
    return Pos(x, y, z0) * extrude(RectangleRounded(L, W, r), amount=h)


def _top_edges(s):
    return s.faces().sort_by(Axis.Z)[-1].edges()


def _bottom_edges(s):
    return s.faces().sort_by(Axis.Z)[0].edges()


def _xcyl(r, x0, x1, y, z):
    """Cylinder along X from x0 to x1."""
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(r, abs(x1 - x0))


def _cable(points, r):
    """Round cable swept along a smooth spline through `points`; capsule chain as fallback."""
    pts = [Vector(*p) for p in points]
    try:
        path = Spline(*pts)
        prof = Plane(origin=pts[0], z_dir=path.tangent_at(0)) * Circle(r)
        s = sweep(prof, path)
        s = s.solids()[0] if hasattr(s, "solids") else s
        if s.is_valid and s.volume > 0:
            return s
    except Exception:
        pass
    out = None
    for a, b in zip(pts[:-1], pts[1:]):
        d = b - a
        seg = Solid.make_cylinder(r, d.length, Plane(origin=a, z_dir=d.normalized()))
        out = seg if out is None else out + seg
    for p in pts[1:-1]:
        out = out + Pos(p.X, p.Y, p.Z) * Sphere(r)
    return out


def _band(p0, p1, w, h, z):
    """Thin raised strip of width w and height h from p0 to p1 (XY), sitting on z."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) + w * 0.6
    a = math.degrees(math.atan2(dy, dx))
    return Pos((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, z + h / 2) * Rot(0, 0, a) * Box(L, w, h)


def _polyline_band(pts, w, h, z):
    out = None
    for a, b in zip(pts[:-1], pts[1:]):
        s = _band(a, b, w, h, z)
        out = s if out is None else out + s
    return out


def _text(txt, size, x, y, z, h=0.3, rot=0.0, plane=None):
    """Raised text (IBM Plex Sans from the kit), or None if the font path fails."""
    font = HERE.parents[1] / ".kit/fonts/IBMPlexSans-SemiBold.ttf"
    try:
        t = extrude(Text(txt, size, font_path=str(font)), amount=h)
        t = Rot(0, 0, rot) * t
        if plane is not None:
            return plane * t
        return Pos(x, y, z) * t
    except Exception:
        return None


def _mc4(x0, y, z, direction=1, female=False):
    """MC4 connector body with cable entering at x0 and mating face toward `direction` (+1 or -1)."""
    d = direction
    nut = _xcyl(MC4_R + 0.8, x0, x0 + d * 13, y, z)
    for k in range(12):   # knurled gland nut
        a = 2 * math.pi * k / 12
        nut -= Pos(x0 + d * 6.5, y + (MC4_R + 0.9) * math.cos(a), z + (MC4_R + 0.9) * math.sin(a)) * \
            Rot(a * 180 / math.pi, 0, 0) * Box(14.0, 1.4, 1.2)
    body = Pos(x0 + d * 30, y, z) * Box(34.0, 2 * MC4_R, 2 * MC4_R - 1.0)
    body = _fillet_try(body, body.edges().filter_by(Axis.X), [4.5, 3.0, 1.5])
    if female:
        sleeve = _xcyl(MC4_R - 0.6, x0 + d * 47, x0 + d * 60, y, z)
        sleeve -= _xcyl(MC4_R - 2.2, x0 + d * 50, x0 + d * 61, y, z)
    else:
        sleeve = _xcyl(MC4_R - 1.8, x0 + d * 47, x0 + d * 62, y, z)
        for sz in (-1, 1):   # latch tabs
            sleeve += Pos(x0 + d * 54, y, z + sz * (MC4_R - 1.4)) * Box(10.0, 5.0, 1.8)
    s = nut + body + sleeve
    s += _xcyl(LEAD_R + 1.2, x0 - d * 8, x0, y, z)          # strain relief
    return s


# ---------------------------------------------------------------- enclosure
def _enclosure(P, M):
    L, W, H, t, zs = P["case_l"], P["case_w"], P["case_h"], P["wall"], P["z_split"]
    outer = _prism(L, W, R_PLAN, 0.0, H)
    outer = _fillet_try(outer, _top_edges(outer), [FIL_TOP, 3.0, 2.0])
    outer = _fillet_try(outer, _bottom_edges(outer), [FIL_BOT, 2.0, 1.0])
    shell = outer - _prism(L - 2 * t, W - 2 * t, R_PLAN - t, t, H - 2 * t)
    groove = _prism(L + 2, W + 2, R_PLAN + 1, zs - GROOVE / 2, GROOVE) - \
        _prism(L - 2 * GROOVE, W - 2 * GROOVE, R_PLAN - GROOVE, zs - GROOVE, 2 * GROOVE)
    shell -= groove
    body = shell & Pos(0, 0, zs / 2) * Box(L + 10, W + 10, zs)
    lid = shell & Pos(0, 0, zs + (H - zs) / 2 + 1) * Box(L + 10, W + 10, H - zs + 2)

    # body: side grip recesses (for the ribbed rubber pads) and the USB-C flap seat at -X
    for sy in (-1, 1):
        body -= Pos(0, sy * W / 2, 25.0) * Box(148.0, 2.0, 30.0)
    body -= Pos(-L / 2, -22.0, 30.0) * Box(2.0, 17.0, 9.0)

    # lid: display window, window rebate, isolator hole, screw counterbores, keypad seat
    cx, cy = P["controller_xy"]
    wx, wy = P["window"]
    lid -= _prism(wx, wy, 3.0, H - 4.0, 5.0, x=cx, y=cy)
    ix, iy = P["isolator_xy"]
    lid -= Pos(ix, iy, H - 1.5) * Cylinder(P["isolator_r"] - 3, 5)
    for (x, y) in LID_SCREWS:
        lid -= Pos(x, y, H - 0.6) * Cylinder(3.6, 1.6)
        lid -= Pos(x, y, H - 6.0) * Cylinder(1.7, 12.0)
    return body, lid


def _boots(P):
    """Rubber corner boots wrapping each vertical case edge, 0 to 40 mm high, standing 7 mm proud of the
    faces like the 14 mm bumpers in model.py, reaching 24 mm along each face."""
    L, W = P["case_l"], P["case_w"]
    proud = P["bumper"] / 2
    ring = _prism(L + 2 * proud, W + 2 * proud, R_PLAN + proud, 0.0, 40.0)
    ring = _fillet_try(ring, _top_edges(ring), [3.0, 2.0, 1.0])
    ring = _fillet_try(ring, _bottom_edges(ring), [2.0, 1.0])
    ring -= _prism(L - 0.2, W - 0.2, R_PLAN, -1.0, 42.0)
    for z in (15.0, 21.0, 27.0):        # three shallow horizontal grooves
        ring -= _prism(L + 2 * proud + 2, W + 2 * proud + 2, R_PLAN + proud + 1, z - 0.6, 1.2) - \
            _prism(L + 2 * proud - 2.0, W + 2 * proud - 2.0, R_PLAN + proud - 1, z - 1, 2)
    out = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            b = ring & Pos(sx * (L / 2 - 12.0), sy * (W / 2 - 12.0), 20.0) * Box(48.0, 48.0, 44.0)
            b = _fillet_try(b, b.edges().filter_by(Axis.Z).filter_by_position(Axis.Z, 5, 35), [1.5, 0.8])
            out = b if out is None else out + b
    return out


def _grips(P):
    """Ribbed rubber grip pads set into both long sides of the body, between the corner boots."""
    W = P["case_w"]
    out = None
    for sy in (-1, 1):
        pad = _prism(146.0, 1.4, 0.6, 11.0, 28.0, y=sy * (W / 2 - 0.3))
        for k in range(-11, 12):
            rib = Pos(k * 6.2, sy * (W / 2 + 0.6), 25.0) * Box(2.6, 1.4, 24.0)
            pad += _fillet_try(rib, rib.edges().filter_by(Axis.Z), [0.6, 0.3])
        out = pad if out is None else out + pad
    return out


def _gland(x_face, y, z, r, d):
    """Cable gland on an end face at x_face, pointing d (+1 or -1): hex nut, domed cap with flutes."""
    nut = Pos(x_face + d * 2.5, y, z) * Rot(0, 90, 0) * extrude(RegularPolygon(r + 2.5, 6), amount=5.0, both=True)
    nut = Pos(0, 0, 0) * nut
    cap = _xcyl(r, x_face + d * 5.0, x_face + d * 11.0, y, z)
    for k in range(10):
        a = 2 * math.pi * k / 10
        cap -= Pos(x_face + d * 8.0, y + r * math.cos(a), z + r * math.sin(a)) * \
            Rot(math.degrees(a), 0, 0) * Box(6.4, 1.6, 1.2)
    tip = _xcyl(r - 2.0, x_face + d * 11.0, x_face + d * 12.0, y, z)
    return nut + cap + tip


# ---------------------------------------------------------------- display and keypad
def _iv_points(cx, cy, w, h, n=40):
    """Screen-space points of a module IV curve (V along +X, I along +Y) and its power curve."""
    isc, voc, a = 1.0, 1.0, 0.055
    iv, pv = [], []
    pmax = max(v * (isc - math.exp((v - voc) / a) + math.exp(-voc / a)) for v in [k / 200 for k in range(201)])
    for k in range(n + 1):
        v = k / n
        i = max(isc - math.exp((v - voc) / a) + math.exp(-voc / a), 0.0)
        x = cx - w / 2 + v * w
        iv.append((x, cy - h / 2 + i * h * 0.86))
        pv.append((x, cy - h / 2 + (v * i / pmax) * h * 0.62))
    return iv, pv


def _screen_graphics(cx, cy, z):
    """Emissive curve, axes and readout bars drawn on the lit screen (raised 0.15 mm)."""
    pw, ph = 44.0, 30.0          # plot area on the 57.6 x 43.2 mm active area
    px, py = cx - 4.0, cy - 3.0
    iv, pv = _iv_points(px, py, pw, ph)
    curve = _polyline_band(iv, 0.9, 0.15, z)
    power = _polyline_band(pv, 0.6, 0.15, z)
    grid = _band((px - pw / 2, py - ph / 2), (px + pw / 2, py - ph / 2), 0.45, 0.12, z)
    grid += _band((px - pw / 2, py - ph / 2), (px - pw / 2, py + ph / 2), 0.45, 0.12, z)
    for k in (1, 2, 3):
        grid += _band((px - pw / 2 + k * pw / 4, py - ph / 2), (px - pw / 2 + k * pw / 4, py + ph / 2), 0.2, 0.08, z)
    # readout: grade tile and value bars in the right column, title bar at the top
    grade = Pos(cx + 23.0, cy + 10.0, z + 0.075) * Box(7.0, 7.0, 0.15)
    bars = None
    for k, ln in enumerate((7.0, 5.0, 6.0)):
        b = Pos(cx + 23.0 - (7.0 - ln) / 2, cy - 2.0 - 4.5 * k, z + 0.06) * Box(ln, 1.2, 0.12)
        bars = b if bars is None else bars + b
    title = Pos(cx - 9.0, cy + 18.0, z + 0.06) * Box(24.0, 1.4, 0.12)
    mpp = max(pv, key=lambda p: p[1])
    dot = Pos(iv[pv.index(mpp)][0], iv[pv.index(mpp)][1], z + 0.1) * Cylinder(1.1, 0.2)
    return curve, power, grid + bars + title, grade + dot


# ---------------------------------------------------------------- internals
def _internals(P, M, add):
    t = P["wall"]
    # 3 controller and display board under the window
    cx, cy = P["controller_xy"]
    c = P["controller"]
    z0 = P["case_h"] - t - c[2] - 1          # model.py envelope bottom (64)
    pcb = _prism(c[0], c[1], 2.0, z0, 1.6, x=cx, y=cy)
    add("Controller board PCB", pcb, C_PCB, "plastic", 3, "internal", (0, 0, 150))
    module = _prism(70.0, 52.0, 1.5, z0 + 1.6, c[2] - 1.6 - 0.3, x=cx, y=cy)
    add("Display module frame", module, "#2A2F37", "plastic", 3, "internal", (0, 0, 150))
    ztop = z0 + c[2] - 0.3
    screen = _prism(58.0, 43.5, 0.6, ztop, 0.3, x=cx, y=cy)
    add("Display screen (lit)", screen, C_SCREEN, "emissive", 3, "internal", (0, 0, 150))
    curve, power, grid, grade = _screen_graphics(cx, cy, ztop + 0.3)
    add("Screen IV curve", curve, C_CURVE, "emissive", 3, "internal", (0, 0, 150))
    add("Screen power curve", power, C_POWER, "emissive", 3, "internal", (0, 0, 150))
    add("Screen grid and readout", grid, C_GRID, "emissive", 3, "internal", (0, 0, 150))
    add("Screen grade tile and MPP marker", grade, "#34D399", "emissive", 3, "internal", (0, 0, 150))
    sd = Pos(cx - c[0] / 2 + 8, cy - 20, z0 - 1.0) * Box(14.0, 15.0, 2.0)
    esp = Pos(cx + 20, cy + 10, z0 - 1.5) * Box(18.0, 25.0, 3.0)
    add("Controller board components", sd + esp, C_METAL, "metal", 3, "internal", (0, 0, 150))

    # floor-mounted boards: PCB plate plus a few component blocks, within the model.py envelopes
    def board(key, bom, name, comps, color=C_PCB_GREEN, lift=(0, 0, 95)):
        s = P[key]; x, y = P[key + "_xy"]
        plate = _prism(s[0], s[1], 1.5, t + 6.0, 1.6, x=x, y=y)      # 6 mm standoffs (model.py board_standoff)
        posts = None
        for sx in (-1, 1):
            for sy in (-1, 1):
                p = Pos(x + sx * (s[0] / 2 - 3), y + sy * (s[1] / 2 - 3), t + 3.0) * Cylinder(1.8, 6.0)
                posts = p if posts is None else posts + p
        add(name, plate + posts, color, "plastic", bom, "internal", lift)
        parts = None
        for (dx, dy, lx, ly, lz) in comps:
            b = Pos(x + dx, y + dy, t + 7.6 + lz / 2) * Box(lx, ly, lz)
            parts = b if parts is None else parts + b
        add(name + " components", parts, C_CHIP, "plastic", bom, "internal", lift)
        return x, y

    mx, my = board("meas", 4, "Measurement board",
                   [(-12, 8, 8, 8, 2.0), (6, 8, 6, 5, 1.6), (14, -6, 10, 6, 1.5), (-16, -10, 12, 4, 1.2)],
                   lift=(0, 0, 95))
    shunt = Pos(mx - 2, my - 12, P["wall"] + 7.6 + 2.5) * Box(20.0, 5.0, 5.0)
    add("Four-terminal shunt (metal)", shunt, "#C08A55", "metal", 4, "internal", (0, 0, 95))
    board("isolation", 14, "Isolation board", [(-6, 0, 8, 7, 1.6), (7, 2, 12, 10, 6.0)], lift=(0, 0, 95))

    # 6 load and discharge MOSFETs on an aluminium bar with a finned heat sink (40 x 16 x 25 envelope)
    fx, fy = P["fets_xy"]; fs = P["fets"]
    bar = Pos(fx, fy - 4.0, t + 11.0) * Box(fs[0], 6.0, 22.0)
    for k in range(6):
        bar += Pos(fx - fs[0] / 2 + 3.5 + k * 6.6, fy - 4.0 - 4.0, t + 11.0) * Box(1.6, 2.0, 22.0)
    add("Load stage heat sink (aluminium)", bar, C_ALU, "metal", 6, "internal", (0, 0, 95))
    fets = None
    for dx in (-9.0, 9.0):
        pkg = Pos(fx + dx, fy + 2.0, t + 13.0) * Box(10.0, 4.5, 15.0)
        tab = Pos(fx + dx, fy - 0.6, t + 17.0) * Box(10.0, 1.2, 16.0)
        legs = None
        for lx in (-2.54, 0.0, 2.54):
            l = Pos(fx + dx + lx, fy + 3.0, t + 3.2) * Box(0.8, 0.6, 6.4)
            legs = l if legs is None else legs + l
        s = pkg + legs
        fets = s if fets is None else fets + s
        add(f"MOSFET tab {1 if dx < 0 else 2} (metal)", tab, C_METAL, "metal", 6, "internal", (0, 0, 95))
    add("Load and discharge MOSFETs", fets, C_CHIP, "plastic", 6, "internal", (0, 0, 95))

    # 7 aluminium-clad discharge resistor with fins (50 x 28 x 16 envelope)
    dx_, dy_ = P["dump_res_xy"]; ds = P["dump_res"]
    res = Pos(dx_, dy_, t + 3.0) * Box(ds[0], ds[1], 2.0)
    res += Pos(dx_, dy_, t + 9.0) * Box(30.0, 16.0, 12.0)
    for k in range(-2, 3):
        res += Pos(dx_, dy_ + k * 3.2, t + 9.0) * Box(38.0, 1.2, 14.0)
    res = Pos(0, 0, 0) * res
    add("Discharge resistor, aluminium clad", res, "#C7A45A", "metal", 7, "internal", (0, 0, 95))

    # 8 DC fuse holder (46 x 20 x 24 envelope)
    ux, uy = P["fuse_xy"]; us = P["fuse"]
    holder = _prism(us[0], us[1], 2.0, t, 18.0, x=ux, y=uy)
    holder = _fillet_try(holder, _top_edges(holder), [1.5, 1.0])
    holder -= Pos(ux, uy, t + 18.0) * Box(20.0, 12.0, 4.0)
    add("DC fuse holder", holder, "#4B5563", "plastic", 8, "internal", (0, 0, 95))
    fuse = _xcyl(5.0, ux - 19.0, ux + 19.0, uy, t + 18.0)
    add("gPV fuse 10 x 38", fuse, "#F4F1EA", "plastic", 8, "internal", (0, 0, 95))

    # 5 load capacitors, 3 x 2200 uF, lying along Y (model.py geometry)
    caps = M["caps"]
    add("Load capacitors, blue sleeve", caps, C_CAP, "painted", 5, "internal", (0, 0, 95))
    ends = None
    for x in P["cap_x"][: P["n_caps"]]:
        e = Pos(x, P["cap_y"] - P["cap_l"] / 2 - 0.4, t + P["cap_d"] / 2) * Rot(90, 0, 0) * Cylinder(P["cap_d"] / 2 - 1.2, 0.8)
        e += Pos(x, P["cap_y"] + P["cap_l"] / 2 + 0.4, t + P["cap_d"] / 2) * Rot(90, 0, 0) * Cylinder(P["cap_d"] / 2 - 1.2, 0.8)
        ends = e if ends is None else ends + e
    add("Capacitor end discs (aluminium)", ends, C_METAL, "metal", 5, "internal", (0, 0, 95))

    # 10 battery: 18650 cell in a holder with charger board (78 x 20 x 20 envelope)
    bx, by = P["battery_xy"]; bs = P["battery"]
    holder = Pos(bx, by, t + 4.0) * Box(bs[0], bs[1], 8.0)
    holder -= Pos(bx, by, t + 11.0) * Rot(0, 90, 0) * Cylinder(9.6, 70.0)
    add("18650 cell holder", holder, C_DARK, "plastic", 10, "internal", (0, 0, 95))
    cell = Pos(bx, by, t + 11.0) * Rot(0, 90, 0) * Cylinder(9.0, 64.0)
    cell = _fillet_try(cell, cell.edges(), [0.6, 0.3])
    add("18650 cell wrap", cell, C_CELL, "painted", 10, "internal", (0, 0, 95))

    # 9 DC isolator body below the lid (model.py geometry)
    ix, iy = P["isolator_xy"]
    zt = P["case_h"] - 1.5
    body = Pos(ix, iy, (P["isolator_z0"] + zt - 2) / 2) * Cylinder(P["isolator_r"], zt - 2 - P["isolator_z0"])
    body = _fillet_try(body, _bottom_edges(body), [2.0, 1.0])
    add("DC isolator body", body, "#6B7280", "plastic", 9, "internal", (0, 0, 150))


# ---------------------------------------------------------------- context: hand and PV module
PV = {"x0": 165.0, "y0": -130.0, "l": 450.0, "w": 350.0, "frame_w": 14.0, "frame_d": 30.0}


def _module(P):
    """Small framed PV module (about 450 x 350 mm, 12 cells) lying face up, frame top at Z = 0."""
    x0, y0, l, w, fw, fd = (PV[k] for k in ("x0", "y0", "l", "w", "frame_w", "frame_d"))
    cxm, cym = x0 + l / 2, y0 + w / 2
    frame = _prism(l, w, 1.0, -fd, fd, x=cxm, y=cym) - _prism(l - 2 * fw, w - 2 * fw, 0.5, -fd - 1, fd + 2, x=cxm, y=cym)
    frame += _prism(l - 2 * fw + 1, w - 2 * fw + 1, 0.5, -6.0, 1.5, x=cxm, y=cym) - \
        _prism(l - 2 * fw - 8, w - 2 * fw - 8, 0.5, -7, 3, x=cxm, y=cym)   # inner lip over the laminate
    back = _prism(l - 2 * fw + 1, w - 2 * fw + 1, 0.5, -6.0, 3.2, x=cxm, y=cym)
    cells = None
    nx, ny, pitch, gap = 4, 3, 100.0, 3.0
    for i in range(nx):
        for j in range(ny):
            x = cxm + (i - (nx - 1) / 2) * (pitch + gap)
            y = cym + (j - (ny - 1) / 2) * (pitch + gap)
            c = _prism(pitch, pitch, 8.0, -2.8, 0.4, x=x, y=y)
            cells = c if cells is None else cells + c
    bus = None
    for i in range(nx):
        for j in range(ny):
            x = cxm + (i - (nx - 1) / 2) * (pitch + gap)
            y = cym + (j - (ny - 1) / 2) * (pitch + gap)
            for k in (-1, 0, 1):
                b = Pos(x + k * 33.0, y, -2.3) * Box(1.2, pitch - 2, 0.12)
                bus = b if bus is None else bus + b
    return frame, back, cells, bus


def _battens(z_floor):
    """Two timber battens under the module so it rests on the same floor as the hand."""
    x0, y0, l, w, fd = (PV[k] for k in ("x0", "y0", "l", "w", "frame_d"))
    h = -fd - z_floor
    if h <= 0.5:
        return None
    out = None
    for f in (0.2, 0.8):
        b = Pos(x0 + l * f, y0 + w / 2, z_floor + h / 2) * Box(45.0, w + 60.0, h)
        out = b if out is None else out + b
    return out


def _hand(P, ox=-132.0, oy=-20.0, oz=97.0, lean=8.0):
    """Clay left hand carrying the tracer at its side by the -X end: palm against the end face, fingers
    hooked under the case floor, thumb round the front corner, forearm rising and leaning slightly out."""
    from context_parts import forearm_hand
    arm = forearm_hand(side="left", pose="grip")
    # fingers down (-Z), palm toward +X (the case end), thumb toward -Y (the user side)
    hand = Pos(ox, oy, oz) * Rot(0, 0, 180) * Rot(0, 90, 0) * arm
    # lean the forearm outward (toward -X) about the finger hook under the case edge
    return Pos(-110.0, 0, 0) * Rot(0, -lean, 0) * Pos(110.0, 0, 0) * hand


# ---------------------------------------------------------------- assembly
def product_parts(P=PARAMS):
    M = build_parts()
    L, W, H, t = P["case_l"], P["case_w"], P["case_h"], P["wall"]
    out = []

    def add(name, shape, color, material, bom, group, explode):
        if shape is None:
            return
        out.append({"name": name, "shape": shape, "color": color, "material": material,
                    "bom": bom, "group": group, "explode": tuple(float(v) for v in explode)})

    LID_UP = 230.0
    body, lid = _enclosure(P, M)
    add("Enclosure body, light grey ABS", body, C_BODY, "plastic", 1, "shell", (0, 0, 0))
    add("Enclosure lid, light grey ABS", lid, C_LID, "plastic", 2, "shell", (0, 0, LID_UP))
    add("Rubber corner boots", _boots(P), C_RUBBER, "rubber", 1, "shell", (0, 0, 0))
    add("Ribbed side grips (rubber)", _grips(P), C_RUBBER, "rubber", 1, "shell", (0, 0, 0))

    # glands: 2 x M16 at +X for the test leads, 1 x M12 at -X for the sensor cable
    gl = None
    for y in (-P["gland_y"], P["gland_y"]):
        g = _gland(L / 2, y, 30.0, P["gland_lead_r"], 1)
        gl = g if gl is None else gl + g
    gl += _gland(-L / 2, 35.0, 30.0, P["gland_sensor_r"], -1)
    add("Cable glands (M16, M12)", gl, "#3A3F47", "plastic", 1, "shell", (0, 0, 0))
    flap = Pos(-L / 2 - 0.2, -22.0, 30.0) * Box(2.4, 16.0, 8.0)
    flap = _fillet_try(flap, flap.edges().filter_by(Axis.X), [2.0, 1.2])
    add("USB-C port rubber flap", flap, C_RUBBER, "rubber", 10, "shell", (0, 0, 0))

    # window, sun hood, lid screws
    cx, cy = P["controller_xy"]
    wx, wy = P["window"]
    win = _prism(wx - 0.4, wy - 0.4, 2.8, H - 4.0, 3.9, x=cx, y=cy)
    add("Display window, clear polycarbonate", win, C_WINDOW, "clear", 2, "shell", (0, 0, LID_UP - 45))
    hood = M["hood"]
    hood = _fillet_try(hood, hood.edges().filter_by(Axis.Z), [1.0, 0.6])
    hood = _fillet_try(hood, _top_edges(hood), [0.8, 0.5])
    add("Display sun hood, printed PETG", hood, C_HOOD, "plastic", 15, "shell", (0, 0, LID_UP + 100))
    for i, (x, y) in enumerate(LID_SCREWS):
        head = Pos(x, y, H - 0.6 + 0.8) * Cylinder(3.3, 1.6)
        head = _fillet_try(head, _top_edges(head), [0.6, 0.3])
        head -= Pos(x, y, H + 0.6) * extrude(RegularPolygon(1.3, 6), amount=1.0)
        head += Pos(x, y, H - 8.0) * Cylinder(1.5, 14.0)
        add(f"Lid screw {i + 1}", head, C_METAL, "metal", 13, "shell", (0, 0, LID_UP + 50))

    # membrane keypad (BOM 18): dark overlay, teal sweep key, two menu keys; two status LEDs above it (model.py positions)
    kx, ky = P["keypad_xy"]
    kw, kd, kt = P["keypad"]
    pad = _prism(kw, kd, 4.0, H, kt, x=kx, y=ky)
    add("Keypad overlay", pad, "#30353C", "plastic", 18, "shell", (0, 0, LID_UP))
    sweep_key = Pos(kx + 16.0, ky, H + kt) * extrude(Circle(8.5), amount=1.8)
    sweep_key = _fillet_try(sweep_key, _top_edges(sweep_key), [1.0, 0.6])
    add("Sweep key", sweep_key, C_ACCENT, "plastic", 18, "shell", (0, 0, LID_UP))
    keys = None
    for dy in (-8.0, 8.0):
        k = _prism(12.0, 9.0, 2.0, H + kt, 1.2, x=kx - 12.0, y=ky + dy)
        k = _fillet_try(k, _top_edges(k), [0.6, 0.3])
        keys = k if keys is None else keys + k
    add("Menu keys", keys, "#6B7280", "plastic", 18, "shell", (0, 0, LID_UP))
    for (lx, ly), col, nm in zip(P["led_xy"], ("#22C55E", "#F59E0B"), ("ready (green)", "live DC (amber)")):
        led = Pos(lx, ly, H + 0.5) * Cylinder(P["led_flange_r"], 1.0) + Pos(lx, ly, H + 1.0) * Sphere(P["led_body_r"])
        add(f"Status LED {nm}", led, col, "emissive", 18, "shell", (0, 0, LID_UP))

    # raised markings: brand on the lid front face, warning label by the isolator
    brand = _text("PVTrace", 9.0, 0, 0, 0, h=0.4,
                  plane=Plane(origin=(62.0, -W / 2 - 0.05, 66.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0)))
    add("Brand marking (teal)", brand, C_ACCENT, "painted", 13, "shell", (0, 0, LID_UP))
    warn = _prism(34.0, 16.0, 1.5, H, 0.3, x=78.0, y=10.0)
    add("Warning label 100 V DC max (yellow)", warn, "#E5B80B", "paper", 13, "shell", (0, 0, LID_UP))
    tri = Pos(67.5, 10.0, H + 0.3) * extrude(RegularPolygon(4.2, 3, rotation=90), amount=0.2)
    txt = _text("100 V DC", 4.2, 0, 0, 0, h=0.2)
    mark = tri if txt is None else tri + Pos(81.0, 10.0, H + 0.3) * txt
    add("Warning label print", mark, C_DARK, "paper", 13, "shell", (0, 0, LID_UP))

    # DC isolator: base ring with ON/OFF ticks, grey knob, red handle (model.py knob and handle)
    ix, iy = P["isolator_xy"]
    ring = Pos(ix, iy, H + 0.75) * (Cylinder(19.0, 1.5) - Cylinder(P["isolator_r"] - 3, 2.0))
    ring = _fillet_try(ring, _top_edges(ring), [0.6, 0.3])
    add("Isolator base ring", ring, "#4B5563", "plastic", 9, "shell", (0, 0, LID_UP))
    knob = Pos(ix, iy, H + P["knob_h"] / 2) * Cylinder(P["knob_r"], P["knob_h"])
    knob = _fillet_try(knob, _top_edges(knob), [1.5, 1.0])
    add("Isolator knob", knob, "#9CA3AF", "plastic", 9, "shell", (0, 0, LID_UP + 30))
    handle = Pos(ix, iy, H + P["knob_h"] + 4) * Box(2 * P["knob_r"] + 6, 8, 8)
    handle = _fillet_try(handle, handle.edges(), [2.5, 1.5, 0.8])
    add("Isolator handle (red)", handle, C_RED, "plastic", 9, "shell", (0, 0, LID_UP + 30))
    ticks = None
    for a, ln in ((0.0, 5.0), (90.0, 5.0)):
        s = Pos(ix, iy, 0) * Rot(0, 0, a) * Pos(16.5, 0, H + 1.6) * Box(ln, 1.0, 0.3)
        ticks = s if ticks is None else ticks + s
    add("Isolator ON/OFF ticks", ticks, "#F3F4F6", "paper", 9, "shell", (0, 0, LID_UP))

    # 11 test leads: red (+) and black (-) cables from the M16 glands down to the floor, MC4 ends
    lead_parts = []
    for (y0, y1, col, name) in ((-P["gland_y"], -42.0, C_RED, "red"), (P["gland_y"], 30.0, C_DARK, "black")):
        xe = L / 2 + 12.0
        xm = 300.0 if name == "red" else 285.0
        pts = [(xe, y0, 30.0), (xe + 14.0, y0, 27.0), (xe + 34.0, y0 + (y1 - y0) * 0.2, 10.0),
               (xe + 70.0, y0 + (y1 - y0) * 0.6, LEAD_R + 0.2), (xm - 40.0, y1, LEAD_R + 0.2),
               (xm - 8.0, y1, MC4_R - 1.0)]
        cab = _cable(pts, LEAD_R)
        add(f"Test lead, {name} PV cable", cab, col, "rubber", 11, "shell", (120, 0, 0))
        mc = _mc4(xm, y1, MC4_R, 1, female=(name == "black"))
        add(f"MC4 connector on {name} lead", mc, "#23272E", "plastic", 11, "shell", (120, 0, 0))
        lead_parts.append((xm, y1, name))
        # coloured polarity band on the connector nut
        band = _xcyl(MC4_R + 1.0, xm + 13.0, xm + 15.0, y1, MC4_R)
        add(f"MC4 polarity band {name}", band, col, "plastic", 11, "shell", (120, 0, 0))

    # The constructable design carries every board and part on a 1.5 mm chassis plate on five standoffs (PVT-DDR-003 C5)
    # and hangs the display board from the lid on 7 mm spacers (C4); the concept drew them on the floor.
    DV = derived(P)
    dz_floor = DV["plate_top"] - t                     # parts that stood on the floor now stand on the plate
    dz_board = DV["pcb_bot"] - (H - t - P["controller"][2] - 1)   # display board at its constructable height

    def add_int(name, shape, color, material, bom, group, explode):
        if shape is not None and group == "internal":
            if bom in (4, 5, 6, 7, 8, 10, 14):
                shape = Pos(0, 0, dz_floor) * shape
            elif bom == 3:
                shape = Pos(0, 0, dz_board) * shape
        add(name, shape, color, material, bom, group, explode)
    _internals(P, M, add_int)
    CC = build_components(P)
    add("Chassis plate, 1.5 mm polycarbonate", CC["plate"], "#CDD3D9", "plastic", 16, "internal", (0, 0, 60))
    add("Chassis plate standoffs (five)", CC["plate_standoffs"], C_METAL, "metal", 13, "internal", (0, 0, 30))

    # 12 sensor pod (accessory, beside the case), model.py pod in its own frame
    pod_at = Pos(-40.0, -230.0, 24.0)
    pw = P["pod"]
    housing = _prism(pw[0], pw[1], 8.0, -pw[2] / 2, pw[2])
    housing = _fillet_try(housing, _top_edges(housing), [3.0, 2.0, 1.0])
    housing = _fillet_try(housing, _bottom_edges(housing), [2.0, 1.0])
    housing -= _prism(P["refcell"][0] + 2, P["refcell"][1] + 2, 2.0, pw[2] / 2 - 1.0, 2.0)
    add("Sensor pod housing", pod_at * housing, C_LID, "plastic", 12, "accessory", (0, -40, 0))
    rc = P["refcell"]
    cell = _prism(rc[0], rc[1], 1.5, pw[2] / 2 - 1.0, rc[2])
    add("Reference cell (mono-Si)", pod_at * cell, C_PV_CELL, "screen", 12, "accessory", (0, -40, 0))
    fingers = None
    for k in range(-3, 4):
        f = Pos(k * 10.0, 0, pw[2] / 2 + rc[2] - 1.0 + 0.05) * Box(0.6, rc[1] - 4, 0.1)
        fingers = f if fingers is None else fingers + f
    add("Reference cell busbars (metal)", pod_at * fingers, C_METAL, "metal", 12, "accessory", (0, -40, 0))
    clip = Pos(0, P["clip_offset"], -2) * Box(*P["clip"])
    clip -= Pos(0, P["clip_offset"] - 2, -10) * Box(P["clip"][0] + 2, 10.0, 30.0)   # frame slot
    clip = _fillet_try(clip, clip.edges().filter_by(Axis.Z), [2.0, 1.0])
    add("Frame clip", pod_at * clip, C_RUBBER, "plastic", 12, "accessory", (0, -40, 0))

    # context: clay hand holding the tracer, small PV module beside it with its own leads
    hand = _hand(P)
    add("Hand (clay)", hand, C_CLAY, "clay", None, "context", (0, 0, 0))
    add("Timber battens under the module", _battens(hand.bounding_box().min.Z), C_WOOD, "wood", None,
        "context", (0, 0, 0))
    frame, back, cells, bus = _module(P)
    add("PV module frame, aluminium", frame, C_ALU, "metal", None, "context", (0, 0, 0))
    add("PV module backsheet", back, C_PV_BACK, "plastic", None, "context", (0, 0, 0))
    add("PV module cells", cells, C_PV_CELL, "screen", None, "context", (0, 0, 0))
    add("PV module cell busbars", bus, C_METAL, "metal", None, "context", (0, 0, 0))
    for (xm, y1, name) in lead_parts:
        mate = _mc4(xm + 124.0, y1, MC4_R, -1, female=(name != "black"))
        add(f"Module MC4 connector ({name})", mate, "#23272E", "plastic", None, "context", (0, 0, 0))
        y0m = PV["y0"]
        pts = [(xm + 132.0, y1, MC4_R - 1.0), (xm + 165.0, y1 - 12.0, LEAD_R + 0.2),
               (xm + 180.0, y0m + 30.0, LEAD_R + 0.2), (xm + 184.0, y0m - 3.0, -2.0),
               (xm + 186.0, y0m - 9.0, -PV["frame_d"])]
        add(f"Module lead ({name})", _cable(pts, LEAD_R - 0.5), C_DARK, "rubber", None, "context", (0, 0, 0))
    return out


if __name__ == "__main__":
    for p in product_parts():
        s = p["shape"]
        print(f"{p['name']:40s} {p['group']:9s} {p['material']:8s} valid={s.is_valid} vol={s.volume / 1000:8.2f} cm3")
