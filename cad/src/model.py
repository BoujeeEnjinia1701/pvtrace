"""PVTrace parametric model (build123d), TRL 3, constructable design (PVT-DDR-003).

Run from the repo root:
    python cad/src/model.py            export STEP and STL into cad/step and cad/stl, print envelopes
    python cad/src/model.py --check    run the constructability checks only

The model is the constructable design of PVT-DDR-003: every part is a part that can be made
or bought, and every part is held by something. Internal parts stand on a 1.5 mm polycarbonate
chassis plate carried 5 mm off the case floor on five nylon standoffs; the capacitor bank is
held down by two cable ties through slots in the plate; the display board hangs under the lid
on four standoffs whose screws also hold the sun hood; the window is bonded on top of the lid
over a smaller opening; the glands, USB-C socket and DC isolator go through drilled holes
and are held by their nuts. PRELIMINARY, NOT FOR FABRICATION.

Axes: X along the case length (test lead glands on the +X end, sensor cable gland and USB-C
socket on the -X end), Y across the case (the user side, where the sun hood opens, is -Y),
Z up with the outside of the case floor at Z = 0. Units mm. The sensor pod is modelled in its
own frame: reference cell face +Z, frame clip toward +Y.
"""
import math
import sys
from pathlib import Path

# Top-level parameters (mm). Edit these, not the geometry below.
PARAMS = {
    # Enclosure (PVT-PRC-001, R12): bought IP54 ABS case, lid screws into four corner pillars
    "case_l": 220.0, "case_w": 130.0, "case_h": 80.0,
    "wall": 3.0,
    "z_split": 52.0,            # body and lid parting line
    "bumper": 14.0,             # rubber corner bumper, square, centred on each vertical edge
    "pillar_r": 4.0,            # moulded corner pillar for the lid screws (inside each corner)
    # Display window (PVT-DDR-003 C2): clear PC bonded on top of the lid over a smaller opening
    "window": (72.0, 54.0), "window_t": 3.0,
    "display_open": (62.0, 46.0),
    # Display sun hood over the window (PVT-DDR-002 item 12, PVT-DDR-003 C3): three walls and a
    # roof lip, open on the -Y (user) side; two inside tabs each side carry the four screws
    "hood_in": (88.0, 60.0), "hood_wall": 2.0, "hood_h": 18.0, "hood_lip": 20.0,
    "hood_tab": (7.5, 10.0, 3.0),
    # Cable glands and USB-C socket (PVT-DDR-003 C1, C6)
    "gland_lead_r": 9.0,        # M16 glands for the test leads (outside flange radius)
    "gland_sensor_r": 7.0,      # M12 gland for the sensor cable
    "gland_y": 18.0,            # test lead glands at +/- this Y
    "gland_z": 30.0,
    "gland_sensor_y": 45.0,
    "usb_y": 22.0, "usb_z": 34.0,
    "m16_nut": (11.0, 5.0),     # inside locknut, radius over corners and thickness
    "m12_nut": (8.5, 4.0),
    # Chassis plate (PVT-DDR-003 C4): 1.5 mm polycarbonate on five 5 mm M3 nylon standoffs
    "plate_t": 1.5, "plate_gap": 5.0, "plate_edge": 1.0, "plate_notch": 10.0,
    "plate_feet": ((-98.0, 34.0), (0.0, 25.0), (102.0, 42.0), (-60.0, -57.0), (70.0, -57.0)),
    # Load capacitors, 3 x 2200 uF 160 V snap-in, lying along Y (decision 3, PVT-DDR-001)
    "n_caps": 3, "cap_d": 35.0, "cap_l": 62.0,
    "cap_x": (-86.0, -48.0, -10.0), "cap_y": -22.0,
    "tie_y": (-42.0, -4.0), "tie": (1.2, 4.8),     # cable tie thickness and width
    # Electronics envelopes (L x W x H) and centres (x, y)
    "controller": (86.0, 50.0, 12.0), "controller_xy": (-50.0, 0.0),
    "tft": (69.0, 50.0, 6.0),
    "board_holes": (79.0, 43.0),                     # display board mounting holes, centres
    "board_gap": 1.0,                                # display glass to lid underside
    "meas": (44.0, 56.0, 12.0), "meas_xy": (76.0, 2.0),
    "isolation": (30.0, 24.0, 10.0), "isolation_xy": (30.0, 34.0),   # decision 4
    "board_standoff": 6.0,
    "fets": (40.0, 16.0, 25.0), "fets_xy": (30.0, -8.0),
    "dump_res": (50.0, 28.0, 16.0), "dump_res_xy": (35.0, -44.0),
    "fuse": (44.0, 20.0, 24.0), "fuse_xy": (84.0, -42.5),
    "battery": (78.0, 20.0, 20.0), "battery_xy": (-55.0, 48.0),
    "isolator_r": 15.0, "isolator_xy": (78.0, 44.0), "isolator_z0": 30.0,
    "isolator_screw_dx": 21.0,
    # Keypad and status LEDs (PVT-DEC-001 item 6, decided 2026-10-02): a 3-key membrane keypad bonded on
    # the lid with its flat tail through a slot, and two 3 mm LEDs in panel clips, all on the controller side
    "keypad": (64.0, 40.0, 0.8), "keypad_xy": (36.0, -34.0), "keypad_slot": (12.0, 1.6), "keypad_tail": (10.0, 0.3, 5.0),
    "led_xy": ((14.0, -8.0), (26.0, -8.0)), "led_hole_r": 2.7, "led_flange_r": 3.5, "led_body_r": 2.5,
    "led_nut_r": 3.4, "led_depth": 8.0,
    "knob_r": 14.0, "knob_h": 10.0,
    "lead_stub": 60.0,          # length of test lead shown leaving each gland
    # Sensor pod (item 12, PVT-DDR-003 C7)
    "pod": (100.0, 70.0, 22.0), "refcell": (80.0, 50.0, 1.5),
    "clip": (40.0, 26.0, 44.0), "clip_offset": 48.0,
    "clip_spine": 6.0, "clip_jaw": 15.0, "clip_open": 42.0, "clip_top_t": 4.0, "clip_bot_t": 6.0,
}

ROOT = Path(__file__).resolve().parents[2]


def derived(P=PARAMS):
    t = P["wall"]
    L, W, H = P["case_l"], P["case_w"], P["case_h"]
    D = {
        "in_x": L / 2 - t, "in_y": W / 2 - t,
        "floor": t, "lid_in": H - t,
        "plate_bot": t + P["plate_gap"], "plate_top": t + P["plate_gap"] + P["plate_t"],
    }
    D["pillars"] = [(sx * (D["in_x"] - P["pillar_r"]), sy * (D["in_y"] - P["pillar_r"]))
                    for sx in (-1, 1) for sy in (-1, 1)]
    D["glass_top"] = D["lid_in"] - P["board_gap"]
    D["pcb_top"] = D["glass_top"] - P["tft"][2]
    D["pcb_bot"] = D["pcb_top"] - 1.6
    cx, cy = P["controller_xy"]
    hx, hy = P["board_holes"]
    D["hood_screws"] = [(cx + sx * hx / 2, cy + sy * hy / 2) for sx in (-1, 1) for sy in (-1, 1)]
    D["cap_top"] = D["plate_top"] + P["cap_d"]
    D["plate_holes"] = plate_holes(P)
    return D


def plate_holes(P=PARAMS):
    """Fixing holes in the chassis plate: (x, y, diameter, what goes through)."""
    out = [(x, y, 3.4, "plate screw into standoff") for (x, y) in P["plate_feet"]]
    fx, fy = P["fets_xy"]; by = fy - P["fets"][1] / 2 + 5
    out += [(fx + d, by, 3.4, "MOSFET bar screw, from below") for d in (-12, 12)]
    x, y = P["dump_res_xy"]
    out += [(x + d, y, 3.4, "discharge resistor screw") for d in (-21, 21)]
    x, y = P["fuse_xy"]
    out += [(x + d, y, 3.4, "fuse holder screw") for d in (-17, 17)]
    x, y = P["battery_xy"]
    out += [(x + d, y, 3.4, "cell holder screw") for d in (-30, 30)]
    for key in ("meas", "isolation"):
        s = P[key]; x, y = P[key + "_xy"]
        out += [(x + a * (s[0] / 2 - 4), y + b * (s[1] / 2 - 4), 3.4, "board standoff screw, from below")
                for a in (-1, 1) for b in (-1, 1)]
    return out


def _box(size, center):
    from build123d import Box, Pos
    return Pos(*center) * Box(*size)


def _cyl_x(r, x0, x1, y, z):
    from build123d import Cylinder, Pos, Rot
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(r, abs(x1 - x0))


def _cyl_z(r, z0, z1, x, y):
    from build123d import Cylinder, Pos
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(r, z1 - z0)


def _hex_z(af, z0, z1, x, y):
    """Hex nut or standoff with across-flats af, axis Z."""
    from build123d import Pos, RegularPolygon, extrude, Plane
    sk = Plane.XY.offset(z0) * Pos(x, y) * RegularPolygon(af / math.sqrt(3), 6)
    return extrude(sk, z1 - z0)


def _fuse(shapes):
    out = None
    for s in shapes:
        if s is None:
            continue
        out = s if out is None else out + s
    return out


def build_components(P=PARAMS):
    """Every component of the constructable design, by name: {name: shape}. Fixings are
    separate entries so the build plan pictures can show them."""
    from build123d import Box, Cylinder, Pos, Rot
    D = derived(P)
    L, W, H, t, zs = P["case_l"], P["case_w"], P["case_h"], P["wall"], P["z_split"]
    ix, iy = D["in_x"], D["in_y"]
    C = {}

    # ---- 1 Enclosure body (bought, drilled): shell, corner bumpers, corner pillars, holes
    body = Pos(0, 0, zs / 2) * Box(L, W, zs) - Pos(0, 0, zs / 2 + t) * Box(L - 2 * t, W - 2 * t, zs)
    b = P["bumper"]
    for sx in (-1, 1):
        for sy in (-1, 1):
            body = body + Pos(sx * L / 2, sy * W / 2, 20) * Box(b, b, 40)
    for (px, py) in D["pillars"]:
        body = body + _cyl_z(P["pillar_r"], t, zs, px, py)
    gz = P["gland_z"]
    for y in (-P["gland_y"], P["gland_y"]):
        body = body - _cyl_x(8.1, L / 2 - t - 1, L / 2 + 1, y, gz)            # 16.2 mm holes
    body = body - _cyl_x(6.1, -L / 2 - 1, -L / 2 + t + 1, P["gland_sensor_y"], gz)   # 12.2 mm
    body = body - _cyl_x(8.1, -L / 2 - 1, -L / 2 + t + 1, P["usb_y"], P["usb_z"])    # 16.2 mm
    for (fx, fy) in P["plate_feet"]:
        from build123d import Cone
        body = body - _cyl_z(1.7, -1, t + 1, fx, fy) - Pos(fx, fy, 0.85) * Cone(3.05, 1.55, 1.71)   # 3.4 mm, countersunk below
    C["body"] = body

    # ---- glands, USB-C socket (bought): outside body and dome, thread through the wall, inside nut
    nr, nt = P["m16_nut"]
    glands, gnuts = [], []
    for y in (-P["gland_y"], P["gland_y"]):
        glands.append(_cyl_x(P["gland_lead_r"], L / 2, L / 2 + 6, y, gz)
                      + _cyl_x(7.5, L / 2 + 6, L / 2 + 22, y, gz)
                      + _cyl_x(8.0, L / 2 - t, L / 2, y, gz))
        gnuts.append(_cyl_x(nr, L / 2 - t - nt, L / 2 - t, y, gz))
    sr, st = P["m12_nut"]
    sg = (_cyl_x(P["gland_sensor_r"], -L / 2 - 5, -L / 2, P["gland_sensor_y"], gz)
          + _cyl_x(6.0, -L / 2 - 18, -L / 2 - 5, P["gland_sensor_y"], gz)
          + _cyl_x(6.0, -L / 2, -L / 2 + t, P["gland_sensor_y"], gz))
    C["glands"] = _fuse(glands + [sg])
    C["gland_nuts"] = _fuse(gnuts + [_cyl_x(sr, -L / 2 + t, -L / 2 + t + st, P["gland_sensor_y"], gz)])
    uy, uz = P["usb_y"], P["usb_z"]
    C["usb"] = (_cyl_x(10.0, -L / 2 - 3, -L / 2, uy, uz) + _cyl_x(9.0, -L / 2 - 14, -L / 2 - 3, uy, uz)
                + _cyl_x(8.0, -L / 2, -L / 2 + t + 15, uy, uz))
    C["usb_nut"] = _cyl_x(nr, -L / 2 + t, -L / 2 + t + nt, uy, uz) - _cyl_x(8.0, -L / 2, -L / 2 + t + nt + 1, uy, uz)

    # ---- 2 Lid (bought, cut and drilled): display opening, isolator hole, screw holes
    lh = H - zs
    lid = Pos(0, 0, zs + lh / 2) * Box(L, W, lh) - Pos(0, 0, zs + lh / 2 - t) * Box(L - 2 * t, W - 2 * t, lh)
    for (px, py) in D["pillars"]:
        lid = lid + _cyl_z(P["pillar_r"], zs, H - t, px, py)
    cx, cy = P["controller_xy"]
    ox, oy = P["display_open"]
    lid = lid - Pos(cx, cy, H - t / 2) * Box(ox, oy, t + 2)
    sx_, sy_ = P["isolator_xy"]
    lid = lid - _cyl_z(P["isolator_r"] - 3, H - t - 1, H + 1, sx_, sy_)
    for dx in (-P["isolator_screw_dx"], P["isolator_screw_dx"]):
        lid = lid - _cyl_z(2.2, H - t - 1, H + 1, sx_ + dx, sy_)
    for (hx, hy) in D["hood_screws"]:
        lid = lid - _cyl_z(1.7, H - t - 1, H + 1, hx, hy)
    kx, ky = P["keypad_xy"]
    slx, sly = P["keypad_slot"]
    lid = lid - Pos(kx, ky + P["keypad"][1] / 2 - 4.0, H - t / 2) * Box(slx, sly, t + 2)       # keypad tail slot
    for (lx, ly) in P["led_xy"]:
        lid = lid - _cyl_z(P["led_hole_r"], H - t - 1, H + 1, lx, ly)                          # 5.4 mm LED holes
    C["lid"] = lid

    # ---- 18 keypad (bought): membrane overlay bonded on the lid top, its tail through the slot
    kw, kd, kt = P["keypad"]
    tw, tt2, tl = P["keypad_tail"]
    C["keypad"] = (Pos(kx, ky, H + kt / 2) * Box(kw, kd, kt)
                   + Pos(kx, ky + kd / 2 - 4.0, H - t / 2 - tl / 2 + 0.5) * Box(tw, tt2, t + tl + 1.0))
    # ---- 18 status LEDs (bought): 3 mm LEDs in panel clips, flange above the lid, nut below
    C["leds"] = _fuse([_cyl_z(P["led_flange_r"], H, H + 1.0, lx, ly) + _cyl_z(P["led_body_r"], H - t - P["led_depth"] + 3.0, H, lx, ly)
                       for (lx, ly) in P["led_xy"]])
    C["led_nuts"] = _fuse([_cyl_z(P["led_nut_r"], H - t - 1.6, H - t, lx, ly) - _cyl_z(P["led_body_r"], H - t - 2, H - t + 0.1, lx, ly)
                           for (lx, ly) in P["led_xy"]])

    # ---- window (made): clear PC bonded on the lid top, round the opening
    wx, wy = P["window"]
    C["window"] = Pos(cx, cy, H + P["window_t"] / 2) * Box(wx, wy, P["window_t"])

    # ---- 15 Sun hood (printed): side walls, back wall, roof lip, four screw tabs
    hx_, hy_ = P["hood_in"]; hw, hh, hl = P["hood_wall"], P["hood_h"], P["hood_lip"]
    owx, owy = hx_ + 2 * hw, hy_ + 2 * hw
    zc = H + hh / 2
    hood = (Pos(cx, cy + hy_ / 2 + hw / 2, zc) * Box(owx, hw, hh)
            + Pos(cx - hx_ / 2 - hw / 2, cy, zc) * Box(hw, owy, hh)
            + Pos(cx + hx_ / 2 + hw / 2, cy, zc) * Box(hw, owy, hh)
            + Pos(cx, cy + owy / 2 - hl / 2, H + hh - hw / 2) * Box(owx, hl, hw))
    tx, ty, tt = P["hood_tab"]
    for (sx, sy) in D["hood_screws"]:
        sgn = 1 if sx > cx else -1
        xc = cx + sgn * (hx_ / 2 - tx / 2)
        hood = hood + Pos(xc, sy, H + tt / 2) * Box(tx + 0.01, ty, tt)
        hood = hood - _cyl_z(1.7, H - 1, H + tt + 1, sx, sy)
        hood = hood - _cyl_z(3.5, H + tt + 0.5, H + hh + 1, sx, sy)     # 7 mm screwdriver hole through the roof lip
    C["hood"] = hood
    C["hood_screws"] = _fuse([_cyl_z(1.5, D["pcb_top"] - 2, H + tt, sx, sy) + _cyl_z(2.75, H + tt, H + tt + 2, sx, sy)
                              for (sx, sy) in D["hood_screws"]])

    # ---- 3 Controller and display board (bought): PCB, TFT on top, parts under
    pcb = Pos(cx, cy, (D["pcb_bot"] + D["pcb_top"]) / 2) * Box(86, 50, 1.6)
    for (sx, sy) in D["hood_screws"]:
        pcb = pcb - _cyl_z(1.6, D["pcb_bot"] - 1, D["pcb_top"] + 1, sx, sy)
    tft = Pos(cx, cy, D["pcb_top"] + P["tft"][2] / 2) * Box(*P["tft"])
    under = Pos(cx, cy, D["pcb_bot"] - 2) * Box(66, 40, 4)
    C["controller"] = pcb + tft + under
    C["display_standoffs"] = _fuse([_hex_z(5.5, D["pcb_top"], D["lid_in"], sx, sy) - _cyl_z(1.5, D["pcb_top"] - 1, D["lid_in"] + 1, sx, sy)
                                    for (sx, sy) in D["hood_screws"]])
    C["display_nuts"] = _fuse([_hex_z(5.5, D["pcb_bot"] - 2.4, D["pcb_bot"], sx, sy) - _cyl_z(1.5, D["pcb_bot"] - 3, D["pcb_bot"] + 1, sx, sy) for (sx, sy) in D["hood_screws"]])

    # ---- chassis plate (made): 1.5 mm polycarbonate on five standoffs, corner notches, tie slots
    pz0, pz1 = D["plate_bot"], D["plate_top"]
    e = P["plate_edge"]; nn = P["plate_notch"]
    plw, pll = 2 * (ix - e), 2 * (iy - e)
    plate = Pos(0, 0, (pz0 + pz1) / 2) * Box(plw, pll, P["plate_t"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            plate = plate - Pos(sx * (plw / 2 - nn / 2 + 0.5), sy * (pll / 2 - nn / 2 + 0.5), (pz0 + pz1) / 2) * Box(nn + 1, nn + 1, 4)
    for (hx_, hy_, hd, _) in D["plate_holes"]:
        plate = plate - _cyl_z(hd / 2, pz0 - 1, pz1 + 1, hx_, hy_)
    xs = P["cap_x"][: P["n_caps"]]
    r = P["cap_d"] / 2
    tt_, tw = P["tie"]
    slot_x = (xs[0] - r - 1.25, xs[-1] + r + 1.25)
    for x in slot_x:
        for y in P["tie_y"]:
            plate = plate - Pos(x, y, (pz0 + pz1) / 2) * Box(2.5, 6.0, 4)
    C["plate"] = plate
    C["plate_standoffs"] = _fuse([_hex_z(5.5, t, pz0, fx, fy) - _cyl_z(1.5, t - 1, pz0 + 1, fx, fy) for (fx, fy) in P["plate_feet"]])
    # M3 countersunk screws from under the floor, M3 pan-head screws on top of the plate
    from build123d import Cone
    C["plate_screws"] = _fuse([Pos(fx, fy, 0.85) * Cone(3.0, 1.5, 1.7) + _cyl_z(1.5, 1.7, t + 2.4, fx, fy)
                               + _cyl_z(2.75, pz1, pz1 + 2, fx, fy) + _cyl_z(1.5, pz0 - 2.4, pz1, fx, fy)
                               for (fx, fy) in P["plate_feet"]])
    # screw heads and nuts under the plate for every part fixed to it
    C["plate_fixings"] = _fuse([_cyl_z(2.75, pz0 - 2.4, pz0, hx_, hy_) for (hx_, hy_, hd, w) in D["plate_holes"] if "standoff" not in w or "board" in w])

    # ---- 5 load capacitors lying along Y on the plate; pins toward -Y; two ties round the bank
    caps = None
    for x in xs:
        cap = Pos(x, P["cap_y"], pz1 + r) * Rot(90, 0, 0) * Cylinder(r, P["cap_l"])
        caps = cap if caps is None else caps + cap
    C["caps"] = caps
    ties = None
    x0, x1 = xs[0] - r - tt_, xs[-1] + r + tt_
    z0, z1 = pz0 - tt_ - 0.6, pz1 + P["cap_d"] + tt_
    for y in P["tie_y"]:
        outer = Pos((x0 + x1) / 2, y, (z0 + z1) / 2) * Box(x1 - x0, tw, z1 - z0)
        inner = Pos((x0 + x1) / 2, y, (z0 + z1) / 2) * Box(x1 - x0 - 2 * tt_, tw + 2, z1 - z0 - 2 * tt_)
        loop = outer - inner      # the two side legs pass down through the plate slots
        ties = loop if ties is None else ties + loop
    C["cap_ties"] = ties

    # ---- floor-mounted parts on the plate
    def on_plate(key, lift=0.0):
        s = P[key]; x, y = P[key + "_xy"]
        return _box(s, (x, y, pz1 + lift + s[2] / 2))
    # 6 MOSFET bar: aluminium bar 40 x 10 x 25 with the two TO-220 MOSFETs on its +Y face
    fx_, fy_ = P["fets_xy"]; fl, fw, fh = P["fets"]
    by = fy_ - fw / 2 + 5
    bar = _box((fl, 10, fh), (fx_, by, pz1 + fh / 2))
    zf = pz1 + 18.0                                   # MOSFET tab screw height
    for dx in (-12, 12):
        bar = bar - _cyl_z(1.5, pz1 - 1, pz1 + 8, fx_ + dx, by)             # M3 tapped (drawn at thread size), 8 deep
    for dx in (-10, 10):
        bar = bar - _cyl_y(1.5, by - 1, by + 5.01, fx_ + dx, zf)            # M3 tapped, 6 deep from the face
    fets = None
    fscr = []
    for dx in (-10, 10):
        f = _box((10, 4.5, 15), (fx_ + dx, by + 5 + 2.25, pz1 + 6 + 7.5)) - _cyl_y(1.6, by + 4, by + 10.5, fx_ + dx, zf)
        fets = f if fets is None else fets + f
        fscr.append(_cyl_y(1.5, by - 1, by + 9.5, fx_ + dx, zf) + _cyl_y(2.75, by + 9.5, by + 11.5, fx_ + dx, zf))
    C["fet_screws"] = _fuse(fscr)
    C["fet_bar"] = bar
    C["fets"] = fets
    C["dump_res"] = on_plate("dump_res")             # 7
    C["fuse"] = on_plate("fuse")                     # 8
    C["battery"] = on_plate("battery")               # 10
    so = P["board_standoff"]
    C["meas"] = on_plate("meas", so)                 # 4
    C["isolation"] = on_plate("isolation", so)       # 14
    bstand = []
    for key in ("meas", "isolation"):
        s = P[key]; x, y = P[key + "_xy"]
        for ddx in (-1, 1):
            for ddy in (-1, 1):
                bstand.append(_cyl_z(2.5, pz1, pz1 + so, x + ddx * (s[0] / 2 - 4), y + ddy * (s[1] / 2 - 4)))
    C["board_standoffs"] = _fuse(bstand)

    # ---- 9 DC isolator: body below the lid, flange and knob above, two fixing screws
    z0i = P["isolator_z0"]; zt = D["lid_in"]
    C["isolator"] = (_cyl_z(P["isolator_r"], z0i, zt, sx_, sy_)
                     + _cyl_z(P["isolator_r"] - 3.2, zt, H, sx_, sy_)
                     + _cyl_z(P["knob_r"] + 1, H, H + 2, sx_, sy_)
                     + _cyl_z(P["knob_r"], H + 2, H + P["knob_h"], sx_, sy_)
                     + Pos(sx_, sy_, H + P["knob_h"] + 4) * Box(2 * P["knob_r"] + 6, 8, 8)
                     + Pos(sx_, sy_, zt - 2.5) * Box(2 * P["isolator_screw_dx"] + 12, 14, 5)    # mounting flange
                     - _fuse([_cyl_z(2.0, zt - 6, zt + 0.1, sx_ + dx, sy_) for dx in (-P["isolator_screw_dx"], P["isolator_screw_dx"])]))
    C["isolator_screws"] = _fuse([_cyl_z(2.0, zt - 5, H, sx_ + dx, sy_) + _cyl_z(3.5, H, H + 2.5, sx_ + dx, sy_)
                                  for dx in (-P["isolator_screw_dx"], P["isolator_screw_dx"])])

    # ---- 11 test lead stubs leaving the +X glands (1 m leads are not modelled in full)
    s = P["lead_stub"]
    C["leads"] = _fuse([_cyl_x(3.5, L / 2 + 22, L / 2 + 22 + s, y, gz) for y in (-P["gland_y"], P["gland_y"])])
    return C


def build_pod(P=PARAMS):
    """12 Sensor pod, own frame: printed housing with the reference cell bonded on top, printed
    C-clip screwed to the housing's +Y face, M6 thumb screw in the lower jaw, cable gland."""
    from build123d import Box, Pos
    pw = P["pod"]
    housing = Box(*pw)
    cell = Pos(0, 0, pw[2] / 2 + P["refcell"][2] / 2) * Box(*P["refcell"])
    sp, jaw, op, tt, bt = P["clip_spine"], P["clip_jaw"], P["clip_open"], P["clip_top_t"], P["clip_bot_t"]
    cw = P["clip"][0]
    y0 = pw[1] / 2
    ztop = pw[2] / 2 + tt                     # clip top level with the housing top plus the jaw
    zb = ztop - tt - op - bt
    clip = (Pos(0, y0 + sp / 2, (ztop + zb) / 2) * Box(cw, sp, ztop - zb)
            + Pos(0, y0 + sp + jaw / 2, ztop - tt / 2) * Box(cw, jaw, tt)
            + Pos(0, y0 + sp + jaw / 2, zb + bt / 2) * Box(cw, jaw, bt))
    clip = clip - _cyl_z(3.3, zb - 1, zb + bt + 1, 0, y0 + sp + jaw - 7)
    screw = _cyl_z(3.0, zb - 2, zb + bt + 7, 0, y0 + sp + jaw - 7) + _cyl_z(8.0, zb - 8, zb - 2, 0, y0 + sp + jaw - 7)
    gland = _cyl_x(6.0, -pw[0] / 2 - 14, -pw[0] / 2, 0, 0)
    screws = _fuse([_cyl_y(2.0, y0 - 8, y0 + sp, dx, 0) + _cyl_y(3.5, y0 + sp, y0 + sp + 2.5, dx, 0) for dx in (-12, 12)])
    housing = housing - _fuse([_cyl_y(2.8, y0 - 8.5, y0 + 0.5, dx, 0) for dx in (-12, 12)]) - _cyl_x(6.1, -pw[0] / 2 - 1, -pw[0] / 2 + 12, 0, 0) - _cyl_x(3.25, pw[0] / 2 - 12, pw[0] / 2 + 1, 0, -4)
    clip = clip - _fuse([_cyl_y(2.2, y0 - 0.5, y0 + sp + 0.5, dx, 0) for dx in (-12, 12)])
    return {"housing": housing, "cell": cell, "clip": clip, "thumb": screw, "pod_gland": gland, "clip_screws": screws}


def _cyl_y(r, y0, y1, x, z):
    from build123d import Cylinder, Pos, Rot
    return Pos(x, (y0 + y1) / 2, z) * Rot(90, 0, 0) * Cylinder(r, abs(y1 - y0))


def build_parts(P=PARAMS):
    """Backward-compatible {name: shape} used by concept_media.py and product_model.py."""
    C = build_components(P)
    pod = build_pod(P)
    parts = {
        "body": C["body"] + C["glands"],
        "lid": C["lid"],
        "window": C["window"],
        "hood": C["hood"],
        "controller": C["controller"],
        "meas": C["meas"],
        "isolation": C["isolation"],
        "fets": C["fet_bar"] + C["fets"],
        "dump_res": C["dump_res"],
        "fuse": C["fuse"],
        "battery": C["battery"],
        "caps": C["caps"],
        "isolator": C["isolator"],
        "leads": C["leads"],
        "pod": pod["housing"] + pod["cell"] + pod["clip"],
        "plate": C["plate"],
        "usb": C["usb"],
        "keypad": C["keypad"] + C["leds"] + C["led_nuts"],
    }
    return parts


INTERNAL = ["controller", "meas", "isolation", "fets", "dump_res", "fuse", "battery", "caps", "isolator"]


# ----------------------------------------------------------------- constructability checks
def _dist(a, b):
    return a.distance_to(b)


def constructability(P=PARAMS, verbose=True):
    """Returns a list of (check, ok, detail). Overlaps by volume, contacts and clearances by
    distance, assembly access by sweeping a screwdriver column, envelope against R12."""
    from build123d import Pos, Box
    C = build_components(P)
    D = derived(P)
    pod = build_pod(P)
    res = []

    def ok(name, cond, detail=""):
        res.append((name, bool(cond), detail))

    # 1 no part overlaps any other (fixings included; each fixing sits in its hole)
    names = [k for k in C if k not in ("leads",)]
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ba, bb = C[a].bounding_box(), C[b].bounding_box()
            if (ba.max.X < bb.min.X or bb.max.X < ba.min.X or ba.max.Y < bb.min.Y or bb.max.Y < ba.min.Y
                    or ba.max.Z < bb.min.Z or bb.max.Z < ba.min.Z):
                continue
            v = (C[a] & C[b]).volume
            ok(f"no overlap: {a} / {b}", v < 0.5, f"{v:.1f} mm3")
    pn = list(pod)
    for i, a in enumerate(pn):
        for b in pn[i + 1:]:
            v = (pod[a] & pod[b]).volume
            ok(f"no overlap: pod {a} / {b}", v < 0.5, f"{v:.1f} mm3")

    # 2 contacts: each part rests on or is held by what the design says
    must_touch = [("plate_standoffs", "body"), ("plate", "plate_standoffs"), ("caps", "plate"), ("fet_bar", "plate"),
                  ("fets", "fet_bar"), ("dump_res", "plate"), ("fuse", "plate"), ("battery", "plate"),
                  ("board_standoffs", "plate"), ("meas", "board_standoffs"), ("isolation", "board_standoffs"),
                  ("window", "lid"), ("hood", "lid"), ("hood_screws", "hood"), ("display_standoffs", "lid"),
                  ("controller", "display_standoffs"), ("display_nuts", "controller"), ("isolator", "lid"),
                  ("isolator_screws", "lid"), ("isolator_screws", "isolator"), ("keypad", "lid"), ("leds", "lid"), ("led_nuts", "lid"),
                  ("led_nuts", "leds"), ("gland_nuts", "body"), ("glands", "body"), ("usb", "body"),
                  ("usb_nut", "body"), ("cap_ties", "caps"), ("plate_screws", "plate_standoffs"), ("plate_screws", "plate"),
                  ("fet_screws", "fets"), ("plate_fixings", "plate")]
    for a, b in must_touch:
        d = _dist(C[a], C[b])
        ok(f"touches: {a} on {b}", d < 0.05, f"gap {d:.2f} mm")
    for a, b in (("cell", "housing"), ("clip", "housing"), ("clip_screws", "clip")):
        d = _dist(pod[a], pod[b])
        ok(f"touches: pod {a} on {b}", d < 0.05, f"gap {d:.2f} mm")

    # 3 clearances: parts that must not touch keep at least 0.5 mm
    clear = [("caps", "fet_bar", 1.0), ("caps", "dump_res", 1.0), ("caps", "battery", 5.0), ("caps", "usb", 2.0),
             ("caps", "controller", 5.0), ("gland_nuts", "fuse", 1.0), ("gland_nuts", "meas", 1.0),
             ("gland_nuts", "battery", 1.0), ("fuse", "body", 0.5), ("fuse", "dump_res", 0.5), ("meas", "isolator", 1.0),
             ("meas", "fets", 1.0), ("isolation", "fets", 1.0), ("isolation", "isolator", 1.0), ("battery", "usb", 1.0),
             ("window", "hood_screws", 0.5), ("controller", "lid", 0.5), ("isolator", "fuse", 1.0),
             ("cap_ties", "fet_bar", 0.5), ("cap_ties", "dump_res", 0.5), ("cap_ties", "body", 0.5),
             ("plate", "body", 0.5), ("hood", "isolator", 1.0), ("usb_nut", "gland_nuts", 1.0),
             ("plate_fixings", "cap_ties", 1.0), ("plate_fixings", "body", 1.0), ("plate_fixings", "plate_standoffs", 1.0),
             ("fet_screws", "meas", 1.0), ("fet_screws", "isolation", 1.0),
             ("keypad", "hood", 3.0), ("keypad", "isolator", 3.0), ("keypad", "window", 3.0), ("leds", "hood", 5.0),
             ("leds", "keypad", 2.0), ("leds", "isolator", 5.0), ("leds", "window", 5.0), ("keypad", "controller", 1.0),
             ("keypad", "meas", 1.0), ("led_nuts", "meas", 1.0), ("led_nuts", "controller", 1.0), ("led_nuts", "display_standoffs", 1.0)]
    for a, b, m in clear:
        d = _dist(C[a], C[b])
        ok(f"clearance {m} mm: {a} / {b}", d >= m, f"{d:.2f} mm")

    # 4 assembly access: with the lid off, a screwdriver column (6 mm) above each plate screw is clear
    body_parts = ["caps", "cap_ties", "fet_bar", "fets", "fet_screws", "dump_res", "fuse", "battery", "meas", "isolation",
                  "usb", "usb_nut", "gland_nuts", "board_standoffs"]
    for (fx, fy) in P["plate_feet"]:
        col = _cyl_z(3.0, D["plate_top"] + 0.01, P["z_split"] + 20, fx, fy)
        v = sum((col & C[k]).volume for k in body_parts)
        ok(f"screwdriver reaches plate screw at ({fx:g}, {fy:g})", v < 0.5, f"{v:.1f} mm3 in the way")
    # a screwdriver (6 mm) reaches each hood screw from above, through the roof lip's access holes
    for (sx, sy) in D["hood_screws"]:
        col = _cyl_z(3.0, P["case_h"] + P["hood_tab"][2] + 2.01, 200, sx, sy)
        v = (col & C["hood"]).volume
        ok(f"screwdriver reaches hood screw at ({sx:g}, {sy:g})", v < 0.5, f"{v:.1f} mm3 in the way")
    # the lid lifts straight off: nothing hung from the lid reaches into a body part's column
    lid_parts = ["controller", "display_standoffs", "display_nuts", "isolator", "isolator_screws", "keypad", "leds", "led_nuts"]
    for a in lid_parts:
        bb = C[a].bounding_box()
        col = Pos((bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2, (bb.min.Z + 200) / 2) * Box(bb.size.X, bb.size.Y, 200 - bb.min.Z)
        v = sum((col & C[k]).volume for k in body_parts)
        ok(f"lid lifts straight off: {a}", v < 0.5, f"{v:.1f} mm3 in the way")

    # 5 envelope (R12): 250 x 150 x 100 mm or less including bumpers, knob and hood
    asm = _fuse([C[k] for k in ("body", "lid", "window", "hood", "isolator", "keypad", "leds")])
    bb = asm.bounding_box()
    ok("envelope inside 250 x 150 x 100 mm (glands excluded in length)", (P["case_l"] + P["bumper"]) <= 250 and bb.size.Y <= 150 and bb.max.Z <= 100,
       f"{P['case_l'] + P['bumper']:.0f} x {bb.size.Y:.0f} x {bb.max.Z:.0f} mm")
    if verbose:
        bad = [r for r in res if not r[1]]
        for n, g, dd in res:
            if not g:
                print(f"FAIL {n}: {dd}")
        print(f"constructability: {len(res) - len(bad)} of {len(res)} checks pass")
    return res


def assemblies(parts=None):
    from build123d import Compound
    C = build_components()
    pod = build_pod()
    inst = [C[k] for k in C]
    return {
        "pvtrace-assembly": Compound(inst),
        "pvtrace-enclosure": Compound([C["body"], C["lid"], C["window"], C["hood"]]),
        "pvtrace-sensor-pod": Compound(list(pod.values())),
        "pvtrace-chassis-plate": C["plate"],
    }


def masses(P=PARAMS):
    """Volumes (cm3) of the made parts, for the calculation note."""
    C = build_components(P)
    pod = build_pod(P)
    return {"plate": C["plate"].volume / 1e3, "hood": C["hood"].volume / 1e3, "window": C["window"].volume / 1e3,
            "pod_housing": pod["housing"].volume / 1e3, "clip": pod["clip"].volume / 1e3}


if __name__ == "__main__":
    if "--check" in sys.argv:
        r = constructability()
        sys.exit(0 if all(x[1] for x in r) else 1)
    from build123d import export_step, export_stl
    r = constructability()
    for name, shape in assemblies().items():
        export_step(shape, str(ROOT / "cad/step" / f"{name}.step"))
        if name != "pvtrace-chassis-plate":
            export_stl(shape, str(ROOT / "cad/stl" / f"{name}.stl"), tolerance=0.2, angular_tolerance=0.3)
        bb = shape.bounding_box()
        print(f"{name}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")
    print("volumes (cm3):", {k: round(v, 1) for k, v in masses().items()})
