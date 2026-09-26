"""PVTrace parametric model (build123d), TRL 3.

Run from the repo root:  python cad/src/model.py
Exports STEP and STL into cad/step and cad/stl, prints the main envelopes and
checks that no two internal parts overlap.

Massing-plus detail: correct interfaces (cable glands, isolator knob, display
window and sun hood, sensor pod with frame clip) and main dimensions; not fabrication detail.
PRELIMINARY, NOT FOR FABRICATION.

Axes: X along the case length (test lead glands on the +X end, sensor cable
gland on the -X end), Y across the case, Z up with the case floor at Z = 0.
Units mm. The sensor pod is modeled in its own frame: reference cell face +Z,
frame clip toward +Y.
"""
from pathlib import Path

# Top-level parameters (mm). Edit these, not the geometry below.
PARAMS = {
    # Enclosure (PVT-PRC-001 v0.3, R12)
    "case_l": 220.0, "case_w": 130.0, "case_h": 80.0,
    "wall": 3.0,
    "z_split": 52.0,            # body and lid parting line
    "bumper": 14.0,             # rubber corner bumper, square, centered on each vertical edge
    "window": (78.0, 56.0),     # display window in the lid
    # Display sun hood over the window (PVT-DDR-002, item 12): three walls and a roof lip,
    # open on the -Y (user) side; top level with the isolator knob top (Z 98), inside R12
    "hood_in": (82.0, 60.0), "hood_wall": 2.0, "hood_h": 18.0, "hood_lip": 20.0,
    "gland_lead_r": 9.0,        # M16 glands for the test leads
    "gland_sensor_r": 7.0,      # M12 gland for the sensor cable
    "gland_y": 20.0,            # test lead glands at +/- this Y
    # Load capacitors, 3 x 2200 uF 160 V snap-in, lying along Y (decision 3, PVT-DDR-001)
    "n_caps": 3, "cap_d": 35.0, "cap_l": 62.0,
    "cap_x": (-84.0, -46.0, -8.0), "cap_y": -28.0,
    # Electronics envelopes (L x W x H) and centers (x, y)
    "controller": (90.0, 62.0, 12.0), "controller_xy": (-50.0, 0.0),
    "meas": (56.0, 44.0, 12.0), "meas_xy": (78.0, 8.0),
    "isolation": (30.0, 24.0, 10.0), "isolation_xy": (30.0, 34.0),   # decision 4
    "fets": (40.0, 16.0, 25.0), "fets_xy": (30.0, -8.0),
    "dump_res": (50.0, 28.0, 16.0), "dump_res_xy": (35.0, -44.0),
    "fuse": (46.0, 20.0, 24.0), "fuse_xy": (83.5, -40.0),
    "battery": (78.0, 20.0, 20.0), "battery_xy": (-55.0, 48.0),
    "isolator_r": 15.0, "isolator_xy": (78.0, 44.0), "isolator_z0": 30.0,
    "knob_r": 14.0, "knob_h": 10.0,
    "lead_stub": 60.0,          # length of test lead shown leaving each gland
    # Sensor pod (item 12)
    "pod": (100.0, 70.0, 22.0), "refcell": (80.0, 50.0, 1.5),
    "clip": (40.0, 26.0, 44.0), "clip_offset": 48.0,
}

ROOT = Path(__file__).resolve().parents[2]


def _box(size, center):
    from build123d import Box, Pos
    return Pos(*center) * Box(*size)


def build_parts():
    """Return {name: shape} for every modeled part of the instrument and the sensor pod."""
    from build123d import Box, Cylinder, Pos, Rot
    P = PARAMS
    L, W, H, t, zs = P["case_l"], P["case_w"], P["case_h"], P["wall"], P["z_split"]
    parts = {}

    # 1 Enclosure body (lower shell) with corner bumpers and glands
    body = (Pos(0, 0, zs / 2) * Box(L, W, zs)
            - Pos(0, 0, zs / 2 + t) * Box(L - 2 * t, W - 2 * t, zs))
    b = P["bumper"]
    for sx in (-1, 1):
        for sy in (-1, 1):
            body = body + Pos(sx * L / 2, sy * W / 2, 20) * Box(b, b, 40)
    for y in (-P["gland_y"], P["gland_y"]):
        body = body + Pos(L / 2 + 6, y, 30) * Rot(0, 90, 0) * Cylinder(P["gland_lead_r"], 12)
    body = body + Pos(-L / 2 - 6, 35, 30) * Rot(0, 90, 0) * Cylinder(P["gland_sensor_r"], 12)
    parts["body"] = body

    # 2 Lid with display window
    lh = H - zs
    wx, wy = P["window"]
    cx, cy = P["controller_xy"]
    lid = (Pos(0, 0, zs + lh / 2) * Box(L, W, lh)
           - Pos(0, 0, zs + lh / 2 - t) * Box(L - 2 * t, W - 2 * t, lh)
           - Pos(cx, cy, H - 1) * Box(wx, wy, 4))
    ix, iy = P["isolator_xy"]
    lid = lid - Pos(ix, iy, H - 1.5) * Cylinder(P["isolator_r"] - 3, 5)
    parts["lid"] = lid
    parts["window"] = Pos(cx, cy, H - 1.5) * Box(wx, wy, 1.5)

    # 15 Display sun hood (printed, screwed to the lid around the window)
    hx, hy = P["hood_in"]; hw, hh, hl = P["hood_wall"], P["hood_h"], P["hood_lip"]
    ox, oy = hx + 2 * hw, hy + 2 * hw
    zc = H + hh / 2
    hood = (Pos(cx, cy + hy / 2 + hw / 2, zc) * Box(ox, hw, hh)                 # back wall (+Y)
            + Pos(cx - hx / 2 - hw / 2, cy, zc) * Box(hw, oy, hh)               # side walls
            + Pos(cx + hx / 2 + hw / 2, cy, zc) * Box(hw, oy, hh)
            + Pos(cx, cy + oy / 2 - hl / 2, H + hh - hw / 2) * Box(ox, hl, hw))  # roof lip
    parts["hood"] = hood

    # 3 Controller and display board under the window
    c = P["controller"]
    parts["controller"] = _box(c, (cx, cy, H - t - c[2] / 2 - 1))

    # floor-mounted boards and parts
    def floor(key):
        s = P[key]; x, y = P[key + "_xy"]
        return _box(s, (x, y, t + s[2] / 2))
    parts["meas"] = floor("meas")              # 4
    parts["isolation"] = floor("isolation")    # 14
    parts["fets"] = floor("fets")              # 6
    parts["dump_res"] = floor("dump_res")      # 7
    parts["fuse"] = floor("fuse")              # 8
    parts["battery"] = floor("battery")        # 10

    # 5 Load capacitors lying along Y
    caps = None
    for x in P["cap_x"][: P["n_caps"]]:
        cap = Pos(x, P["cap_y"], t + P["cap_d"] / 2) * Rot(90, 0, 0) * Cylinder(P["cap_d"] / 2, P["cap_l"])
        caps = cap if caps is None else caps + cap
    parts["caps"] = caps

    # 9 DC isolator: body below the lid, knob and handle above it
    z0 = P["isolator_z0"]; zt = H - 1.5
    parts["isolator"] = (Pos(ix, iy, (z0 + zt) / 2) * Cylinder(P["isolator_r"], zt - z0)
                         + Pos(ix, iy, H + P["knob_h"] / 2) * Cylinder(P["knob_r"], P["knob_h"])
                         + Pos(ix, iy, H + P["knob_h"] + 4) * Box(2 * P["knob_r"] + 6, 8, 8))

    # 11 Test lead stubs leaving the +X glands (1 m leads are not modeled in full)
    s = P["lead_stub"]
    leads = None
    for y in (-P["gland_y"], P["gland_y"]):
        stub = Pos(L / 2 + 12 + s / 2, y, 30) * Rot(0, 90, 0) * Cylinder(3.5, s)
        leads = stub if leads is None else leads + stub
    parts["leads"] = leads

    # 12 Sensor pod, own frame
    pw = P["pod"]
    parts["pod"] = (Box(*pw)
                    + Pos(0, 0, pw[2] / 2 + P["refcell"][2] / 2) * Box(*P["refcell"])
                    + Pos(0, P["clip_offset"], -2) * Box(*P["clip"]))
    return parts


INTERNAL = ["controller", "meas", "isolation", "fets", "dump_res", "fuse", "battery", "caps", "isolator"]


def interference(parts):
    """Pairwise overlap volume (mm3) between internal parts; empty dict means no clashes."""
    bad = {}
    for i, a in enumerate(INTERNAL):
        for b in INTERNAL[i + 1:]:
            v = (parts[a] & parts[b]).volume
            if v > 1.0:
                bad[(a, b)] = v
    for a in INTERNAL:
        v = (parts[a] & parts["body"]).volume + (parts[a] & parts["lid"]).volume
        if v > 1.0 and a != "isolator":
            bad[(a, "case")] = v
    v = (parts["hood"] & parts["isolator"]).volume
    if v > 1.0:
        bad[("hood", "isolator")] = v
    return bad


def assemblies(parts):
    from build123d import Compound
    inst = [parts[k] for k in ["body", "lid", "window", "hood", "controller", "meas", "isolation", "fets",
                                "dump_res", "fuse", "battery", "caps", "isolator", "leads"]]
    return {
        "pvtrace-assembly": Compound(inst),
        "pvtrace-enclosure": Compound([parts["body"], parts["lid"], parts["window"], parts["hood"]]),
        "pvtrace-sensor-pod": parts["pod"],
    }


if __name__ == "__main__":
    from build123d import export_step, export_stl
    parts = build_parts()
    clash = interference(parts)
    for k, v in clash.items():
        print(f"CLASH {k[0]} / {k[1]}: {v:.0f} mm3")
    for name, shape in assemblies(parts).items():
        export_step(shape, str(ROOT / "cad/step" / f"{name}.step"))
        export_stl(shape, str(ROOT / "cad/stl" / f"{name}.stl"))
        bb = shape.bounding_box()
        print(f"{name}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")
    shell = parts["body"].volume + parts["lid"].volume
    print(f"case shell volume incl. bumpers and glands: {shell / 1000:.0f} cm3")
    print(f"sun hood volume: {parts['hood'].volume / 1000:.1f} cm3")
    print("interference check:", "none" if not clash else f"{len(clash)} clashes")
