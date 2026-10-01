"""PVTrace prototype build plan pictures (PVT-BLD-001, STANDARDS section 18).

Run from the repo root:  python cad/src/build_plan_media.py [overview|sheets|layouts|joints|steps|wiring ...]
With no argument it draws everything. Every picture is drawn from cad/src/model.py
(build_components, build_pod), so the pictures and the model never disagree:
    docs/05-build-plan/overview.png        every component pulled apart, numbered in build order
    cad/drawings/PVT-DWG-101 to 108        making sketches for the made and drilled components
    docs/05-build-plan/*-holes.png         hole layouts for the case, the chassis plate and the lid
    docs/05-build-plan/joint-NN.png        close-ups of the joints that need explaining
    docs/05-build-plan/step-NN.png         one picture per assembly step
    docs/05-build-plan/wiring.png          block-level wiring with wire sizes (matplotlib)
A single picture can be drawn with, for example, `steps 4` or `joints 2`.
Uses .kit/build_views.py. BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad" / "src")]
import build_views as bv  # noqa: E402
from build_views import Part  # noqa: E402
from model import PARAMS as P, build_components, build_pod, derived  # noqa: E402

OUT = ROOT / "docs" / "05-build-plan"
DWG = ROOT / "cad" / "drawings"
DATE = "2026-10-01"
REPO = "github.com/BoujeeEnjinia1701/pvtrace"
D = derived(P)
C = build_components(P)
POD = build_pod(P)
L, W, H = P["case_l"], P["case_w"], P["case_h"]

COL = {"body": "#D1D5DB", "lid": "#E5E7EB", "glands": "#1F2937", "usb": "#374151", "plate": "#818CF8",
       "standoff": "#6B7280", "caps": "#1D4ED8", "ties": "#111827", "bar": "#475569", "fets": "#7C3AED",
       "dump": "#B45309", "fuse": "#DC2626", "battery": "#C2410C", "meas": "#16A34A", "iso": "#DB2777",
       "isolator": "#F59E0B", "window": "#7DD3FC", "hood": "#64748B", "ctrl": "#0F766E", "housing": "#0EA5E9",
       "clip": "#0369A1", "cell": "#1E3A8A", "bolt": "#111827", "frame": "#9CA3AF"}


def _fuse(shapes):
    out = None
    for s in shapes:
        out = s if out is None else out + s
    return out


def part(name, shape, color, explode=(0, 0, 0), alpha=1.0):
    return Part(name, shape, color, None, tuple(explode), alpha)


def box(x0, x1, y0, y1, z0, z1):
    from build123d import Box, Pos
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def win(shape, *b):
    return shape & box(*b)


S = lambda *ks: _fuse([C[k] for k in ks])  # noqa: E731
BIG = 1000


def lead_end():
    return win(S("glands", "gland_nuts"), 0, BIG, -BIG, BIG, -BIG, BIG)


def left_end():
    return win(S("glands", "gland_nuts"), -BIG, 0, -BIG, BIG, -BIG, BIG) + S("usb", "usb_nut")


def pod_shape(offset=(0, 0, 0)):
    from build123d import Pos
    return Pos(*offset) * _fuse(list(POD.values()))


def board_standoffs(key):
    s = P[key]; x, y = P[key + "_xy"]
    return win(C["board_standoffs"], x - s[0] / 2, x + s[0] / 2, y - s[1] / 2, y + s[1] / 2, -BIG, BIG)


# ----------------------------------------------------------------- named parts, in build order
def made():
    return {
        "body": part("Enclosure body, drilled", C["body"], COL["body"]),
        "leadg": part("Test lead glands (2)", lead_end(), COL["glands"]),
        "leftg": part("Sensor gland and USB-C socket", left_end(), COL["usb"]),
        "feet": part("Plate standoffs (5) and screws", S("plate_standoffs", "plate_screws"), COL["standoff"]),
        "plate": part("Chassis plate", C["plate"], COL["plate"]),
        "bar": part("MOSFET bar and MOSFETs", S("fet_bar", "fets", "fet_screws"), COL["fets"]),
        "dump": part("Discharge resistor", C["dump_res"], COL["dump"]),
        "fuse": part("Fuse holder and fuse", C["fuse"], COL["fuse"]),
        "battery": part("Cell holder, cell and charger", C["battery"], COL["battery"]),
        "meas": part("Measurement board on standoffs", C["meas"] + board_standoffs("meas"), COL["meas"]),
        "iso": part("Isolation board on standoffs", C["isolation"] + board_standoffs("isolation"), COL["iso"]),
        "caps": part("Load capacitors (3) and ties", S("caps", "cap_ties"), COL["caps"]),
        "lid": part("Lid, cut and drilled", C["lid"], COL["lid"]),
        "window": part("Window", C["window"], COL["window"]),
        "isolator": part("DC isolator", S("isolator", "isolator_screws"), COL["isolator"]),
        "ctrl": part("Display board and spacers", S("controller", "display_standoffs", "display_nuts"), COL["ctrl"]),
        "hood": part("Sun hood and screws", S("hood", "hood_screws"), COL["hood"]),
        "pod": part("Sensor pod", pod_shape(), COL["housing"]),
    }


# ----------------------------------------------------------------- overview
def overview():
    from build123d import Pos
    M = made()
    off = {"body": (0, 0, 0), "leadg": (90, 0, 0), "leftg": (-90, 0, 0), "feet": (0, 0, 45), "plate": (0, 0, 85),
           "bar": (0, 0, 170), "dump": (0, -20, 135), "fuse": (20, -10, 150), "battery": (0, 50, 215), "meas": (20, 0, 190),
           "iso": (0, 20, 205), "caps": (-20, -70, 190), "lid": (0, 0, 330), "window": (0, 0, 385), "isolator": (0, 0, 255),
           "ctrl": (0, 0, 250), "hood": (0, 0, 420), "pod": (-310, -40, 60)}
    order = ["body", "leadg", "leftg", "feet", "plate", "bar", "dump", "fuse", "battery", "meas", "iso", "caps",
             "lid", "window", "isolator", "ctrl", "hood", "pod"]
    parts = []
    for k in order:
        p = M[k]
        p.explode = off[k]
        parts.append(p)
    return bv.overview(parts, OUT / "overview.png", "PVTrace prototype: every component, pulled apart",
                       subtitle="Numbered in build order. The case parts are stacked over the body; the sensor pod is on the left. "
                                "Seen from the front right and above",
                       elev=22, azim=-55, size=(12, 9), dpi=150, key=True)


# ----------------------------------------------------------------- making sketches
def sheets():
    from build123d import Pos, Rot
    M = made()
    base = dict(project="PVTrace", date=DATE)
    out = []
    pz1 = D["plate_top"]
    cx, cy = P["controller_xy"]

    # 101 enclosure body, drilled
    out.append(bv.component_sheet(
        Part("Enclosure body", C["body"], COL["body"]), [M["plate"], M["leadg"], M["leftg"], M["lid"]],
        dwg_no="PVT-DWG-101", title="PVTrace enclosure body: drilling sketch",
        material="Bought IP54 ABS handheld case 220 x 130 x 80 mm, light grey",
        notes=["Drill the body only. Front is the long side toward the user; right is",
               "  the end the test leads leave from. Sizes from outside faces.",
               "Right end: two 16.2 mm holes for the M16 lead glands, 47 and 83 mm",
               "  from the front face, 30 mm up from the bottom.",
               "Left end: 16.2 mm hole for the USB-C socket, 87 mm from the front",
               "  face, 34 mm up; 12.2 mm hole for the M12 sensor gland, 110 mm",
               "  from the front face, 30 mm up.",
               "Floor: five 3.4 mm holes, countersunk from below for M3 screws, at the",
               "  positions on the case hole layout (from the left end and front face).",
               "Tape each face, pilot drill 2 mm with wood behind, open with a step",
               "  drill at low speed. Deburr inside and out.",
               "Check: the glands, socket and plate standoffs fit their holes."],
        inset_view=(22, -55), **base))

    # 102 chassis plate
    out.append(bv.component_sheet(
        Part("Chassis plate", C["plate"], COL["plate"]), [M["body"], M["feet"]],
        dwg_no="PVT-DWG-102", title="PVTrace chassis plate: making sketch", material="Polycarbonate sheet 1.5 mm, clear",
        view_shape=Pos(0, 0, -D["plate_bot"]) * C["plate"], inset_view=(40, -60),
        notes=["Cut a 212 x 122 mm blank from 1.5 mm polycarbonate; keep the film on.",
               "Cut a 10 x 10 mm notch at each corner (clears the lid screw pillars).",
               "Cut four cable tie slots, 2.5 x 6 mm: two open notches on the left edge",
               "  and two slots 113.5 to 116 mm from the left edge; all four centred",
               "  19 and 57 mm from the front edge.",
               "Drill the 21 holes 3.4 mm at the positions on the plate hole layout:",
               "  five for the standoffs, the rest for the parts on the plate.",
               "Score and snap or saw with a fine blade; file the edges smooth.",
               "Fit: the plate sits on five 5 mm standoffs, 1 mm in from every wall.",
               "Every part is screwed to the plate before it goes into the case.",
               "Check: lay it in the case; it drops in flat past the corner pillars."],
        **base))

    # 103 MOSFET bar
    bar = C["fet_bar"]
    bb = bar.bounding_box()
    out.append(bv.component_sheet(
        Part("MOSFET bar", bar, COL["bar"]), [M["plate"], M["dump"], M["caps"], part("MOSFETs", C["fets"], COL["fets"])],
        dwg_no="PVT-DWG-103", title="PVTrace MOSFET bar: making sketch", material="Aluminium flat bar 25 x 10 mm, 6061 or 6082",
        view_shape=Pos(-bb.center().X, -bb.center().Y, -bb.min.Z) * bar, inset_view=(30, 60),
        notes=["Cut 40 mm off 25 x 10 mm flat bar; square and deburr the ends.",
               "The bar stands on a 40 x 10 mm face (the bottom), 25 mm tall.",
               "Bottom: drill 2.5 mm, 9 mm deep, and tap M3 8 deep, 12 mm each side",
               "  of centre, on the centre line. Screws come up through the plate.",
               "Back face (the 40 x 25 face toward the back of the case): drill",
               "  2.5 mm, 7 deep, and tap M3 6 deep, 10 mm each side of centre and",
               "  18 mm up from the bottom. One MOSFET tab is screwed to each.",
               "File the back face flat; no burrs may pierce the insulating pad.",
               "Fit: each MOSFET tab on an insulating thermal pad, with an insulating",
               "  bushing under the screw head. The tabs are live at PV voltage.",
               "Check: with the MOSFETs fitted, a meter reads open circuit from each",
               "  tab to the bar."],
        **base))

    # 104 lid, cut and drilled
    out.append(bv.component_sheet(
        Part("Lid", C["lid"], COL["lid"]), [M["window"], M["hood"], M["isolator"], M["ctrl"]],
        dwg_no="PVT-DWG-104", title="PVTrace lid: cutting and drilling sketch", material="Lid of the bought case, ABS 3 mm",
        view_shape=Pos(0, 0, -P["z_split"]) * C["lid"], inset_view=(30, -55),
        notes=["Positions from the lid's left end and front face, outside, top view.",
               "Display opening 62 x 46 mm, centred 60 from the left end and 65 from",
               "  the front: drill the corners 6 mm, cut between with a fine saw, file.",
               "Four 3.4 mm holes for the display screws at 20.5 and 99.5 from the",
               "  left end, each 43.5 and 86.5 from the front.",
               "DC isolator: 24 mm hole centred 188 from the left end and 109 from",
               "  the front; two 4.4 mm holes 21 mm each side of it, left and right.",
               "Check the isolator maker's cut-out before cutting; follow it if it differs.",
               "Tape the face, cut slowly, deburr; clean with soap and water.",
               "Check: the window covers the opening with 4 to 5 mm all round; the",
               "  hood's four tabs line up with the four small holes."],
        **base))

    # 105 window
    win_ = C["window"]
    out.append(bv.component_sheet(
        Part("Window", win_, COL["window"]), [M["lid"], M["hood"]],
        dwg_no="PVT-DWG-105", title="PVTrace display window: making sketch", material="Clear polycarbonate sheet 3 mm",
        view_shape=Pos(-cx, -cy, -H) * win_, inset_view=(35, -55),
        notes=["Cut 72 x 54 mm from 3 mm clear polycarbonate; keep the film on",
               "  both faces until it is bonded.",
               "Score and snap, or saw with a fine blade; file and polish the edges.",
               "Break the corners 1 mm so the gasket tape does not lift.",
               "Lay 4 mm wide closed-cell adhesive gasket tape round the underside,",
               "  on the edge, in one length with a butt joint at the back.",
               "Fit: bonded on top of the lid, centred over the 62 x 46 mm opening,",
               "  overlapping it 5 mm at the ends and 4 mm at the sides.",
               "The hood's tabs and screws sit just outside its ends, 0.75 mm clear.",
               "Check: no gap in the gasket all round; the display reads through it."],
        **base))

    # 106 sun hood
    hood = C["hood"]
    out.append(bv.component_sheet(
        Part("Sun hood", hood, "#94A3B8"), [M["lid"], M["window"], M["isolator"]],
        dwg_no="PVT-DWG-106", title="PVTrace display sun hood: making sketch", material="PETG, 3D printed, light grey",
        view_shape=Pos(-cx, -cy, -H) * hood, inset_view=(35, -55),
        notes=["Print in light grey PETG, 0.2 mm layers, 4 walls, 30 % infill,",
               "  roof lip down on the bed so the walls need no supports.",
               "Outside 92 x 64 x 18 mm: two side walls and a back wall 2 mm thick,",
               "  a roof lip 20 mm deep along the back; open at the front (user side).",
               "Four tabs inside the side walls, 7.5 x 10 x 3 mm, flush with the",
               "  bottom edge, centred 21.5 mm each side of the hood's middle.",
               "Tab holes 3.4 mm: 79 mm apart across, 43 mm apart front to back;",
               "  7 mm screwdriver holes through the roof lip over the two back tabs.",
               "Fit: four M3 x 20 screws with sealing washers pass through the tabs,",
               "  the lid and the spacers and also hold the display board.",
               "Check: the hood's top is level with the isolator knob top, 98 mm up."],
        **base))

    # 107 sensor pod housing
    hs = POD["housing"]
    out.append(bv.component_sheet(
        Part("Sensor pod housing", hs, COL["housing"]), [part("Reference cell", POD["cell"], COL["cell"]),
                                                          part("Clip", POD["clip"], COL["clip"])],
        dwg_no="PVT-DWG-107", title="PVTrace sensor pod housing: making sketch", material="PETG or ASA, 3D printed, light grey",
        view_shape=Pos(0, 0, P["pod"][2] / 2) * hs, inset_view=(30, -130),
        notes=["Print 100 x 70 x 22 mm, top face up, 4 walls, 30 % infill, with a",
               "  6 mm channel inside from the top centre to the left end hole.",
               "Left end: 12.2 mm hole, 12 deep, centred, for the M12 cable gland.",
               "Right end: 6.5 mm hole for the temperature probe lead, 4 mm below",
               "  centre; fit a rubber grommet.",
               "Clip face (the long side toward the module): two 5.6 mm holes, 8.5",
               "  deep, 12 mm each side of centre, mid height; press in M4 heat-set",
               "  inserts with a soldering iron.",
               "Bond the reference cell centred on the top face with neutral-cure",
               "  silicone; lead its wires down the channel and seal the channel.",
               "Check: the cell face is flat and parallel to the housing base."],
        **base))

    # 108 sensor pod clip
    cl = POD["clip"]
    bb = cl.bounding_box()
    out.append(bv.component_sheet(
        Part("Sensor pod clip", cl, COL["clip"]), [part("Housing", POD["housing"], COL["housing"]),
                                                     part("Thumb screw", POD["thumb"], COL["bolt"])],
        dwg_no="PVT-DWG-108", title="PVTrace sensor pod clip: making sketch", material="PETG or ASA, 3D printed, 100 % infill",
        view_shape=Pos(-bb.center().X, -bb.min.Y, -bb.min.Z) * cl, inset_view=(20, 60),
        notes=["Print on its side, 100 % infill: a C shape 40 mm wide, 21 mm deep and",
               "  52 mm tall; back 6 mm, top jaw 4 mm, bottom jaw 6 mm thick.",
               "Opening between the jaws 42 mm, for module frames 30 to 40 mm deep.",
               "Bottom jaw: 6.6 mm hole 14 mm in from the back face, centred; an M6",
               "  nut sits in a hex pocket on top, or tap the jaw M6 directly.",
               "Back: two 4.4 mm holes, 12 mm each side of centre, 15 mm below the",
               "  top; two M4 x 12 screws go into the housing's inserts.",
               "Fit: the top jaw rests on the frame's top edge and the thumb screw",
               "  presses up under the frame's bottom flange; the cell then lies about",
               "  4 mm above the glass and parallel to it.",
               "Check: on a frame offcut, the pod cannot rock when the screw is snug."],
        **base))
    return out


# ----------------------------------------------------------------- hole layouts
def _fig(w, h, title, sub):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(w, h), dpi=150)
    fig.text(0.03, 0.975, title, fontsize=13, fontweight="bold", color="#111827", va="top")
    fig.text(0.03, 0.94, sub, fontsize=8.5, color="#4B5563", va="top")
    fig.text(0.03, 0.015, "BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT", fontsize=7, color="#B45309")
    fig.text(0.97, 0.015, REPO, fontsize=7, color="#0F766E", ha="right", family="monospace")
    return fig, plt


def _table(fig, x, y, rows, head, dy=0.024, widths=(0.04, 0.09, 0.09, 0.07)):
    INK = "#111827"
    xs = [x]
    for w_ in widths:
        xs.append(xs[-1] + w_)
    for j, h_ in enumerate(head):
        fig.text(xs[j], y, h_, fontsize=7.6, fontweight="bold", color=INK, va="top")
    for i, r in enumerate(rows):
        for j, c in enumerate(r):
            fig.text(xs[j], y - (i + 1) * dy, str(c), fontsize=7.6, color=INK, va="top")


def layouts():
    from matplotlib.patches import Rectangle, Circle
    INK, MUT, AC = "#111827", "#4B5563", "#0F766E"
    res = []

    # ---- chassis plate, top view, origin at the plate's left front corner
    x0, y0 = -(D["in_x"] - P["plate_edge"]), -(D["in_y"] - P["plate_edge"])
    pw_, pl_ = -2 * x0, -2 * y0
    fig, plt = _fig(12, 7.4, "Chassis plate: hole and slot positions",
                    "Seen from above. Every figure in mm from the plate's left end (across) and front edge (in). "
                    "All holes 3.4 mm. Taken from the model.")
    ax = fig.add_axes([0.03, 0.08, 0.56, 0.82]); ax.set_aspect("equal"); ax.set_axis_off()
    nn = P["plate_notch"]
    from matplotlib.patches import Polygon
    poly = [(nn, 0), (pw_ - nn, 0), (pw_ - nn, nn), (pw_, nn), (pw_, pl_ - nn), (pw_ - nn, pl_ - nn), (pw_ - nn, pl_),
            (nn, pl_), (nn, pl_ - nn), (0, pl_ - nn), (0, nn), (nn, nn)]
    ax.add_patch(Polygon(poly, closed=True, fc="#EEF2FF", ec=INK, lw=1.1))
    # footprints of the parts, faint, so the reader sees what each hole is for
    for key, lab in (("dump_res", "resistor"), ("fuse", "fuse"), ("battery", "cell holder"), ("meas", "measurement"),
                     ("isolation", "isolation")):
        s = P[key]; x, y = P[key + "_xy"]
        ax.add_patch(Rectangle((x - s[0] / 2 - x0, y - s[1] / 2 - y0), s[0], s[1], fc="none", ec="#A5B4FC", lw=0.8, ls="--"))
        ax.text(x - x0, y - y0 + s[1] / 2 - 3, lab, ha="center", va="top", fontsize=6.5, color="#6366F1")
    fx_, fy_ = P["fets_xy"]
    ax.add_patch(Rectangle((fx_ - 20 - x0, fy_ - 8 - y0), 40, 10, fc="none", ec="#A5B4FC", lw=0.8, ls="--"))
    ax.text(fx_ - x0, fy_ - 8 - y0 + 12, "MOSFET bar", ha="center", fontsize=6.5, color="#6366F1")
    for x in P["cap_x"]:
        ax.add_patch(Rectangle((x - 17.5 - x0, P["cap_y"] - 31 - y0), 35, 62, fc="none", ec="#93C5FD", lw=0.8, ls=":"))
    ax.text(P["cap_x"][1] - x0, P["cap_y"] - y0, "capacitors\nlie here", ha="center", va="center", fontsize=6.5, color="#3B82F6")
    # slots
    r = P["cap_d"] / 2
    for xs_ in (P["cap_x"][0] - r - 1.25, P["cap_x"][-1] + r + 1.25):
        for ys in P["tie_y"]:
            ax.add_patch(Rectangle((xs_ - 1.25 - x0, ys - 3 - y0), 2.5, 6, fc="white", ec=INK, lw=0.9))
    rows = []
    for i, (hx, hy, hd, what) in enumerate(D["plate_holes"], 1):
        X, Y = hx - x0, hy - y0
        ax.add_patch(Circle((X, Y), hd / 2 + 0.6, fc="white", ec=INK, lw=0.9))
        ax.text(X + 3.2, Y + 3.2, str(i), fontsize=6.6, color=AC, fontweight="bold")
        rows.append((i, f"{X:.1f}", f"{Y:.1f}", what))
    ax.set_xlim(-6, pw_ + 6); ax.set_ylim(-17, pl_ + 6)
    ax.annotate("", xy=(0, -5), xytext=(pw_, -5), arrowprops=dict(arrowstyle="<->", color=MUT, lw=0.6))
    ax.text(pw_ / 2, -7.5, f"{pw_:.0f}", ha="center", va="top", fontsize=7.5, color=MUT)
    ax.text(-3, pl_ / 2, f"{pl_:.0f}", ha="right", va="center", fontsize=7.5, color=MUT, rotation=90)
    ax.text(pw_ / 2, pl_ + 2, "back edge", ha="center", va="bottom", fontsize=7, color=MUT)
    ax.text(pw_ / 2, -12, "front edge (user side)", ha="center", va="top", fontsize=7, color=MUT)
    fig.text(0.61, 0.89, "Holes (3.4 mm)", fontsize=9, fontweight="bold", color=INK, va="top")
    _table(fig, 0.61, 0.855, [(a, b, c, d) for a, b, c, d in rows], ("No.", "across", "in", "what goes through"),
           dy=0.031, widths=(0.04, 0.06, 0.06, 0.2))
    fig.text(0.61, 0.855 - 0.031 * (len(rows) + 1.6), "Slots 2.5 x 6 at 1.25 (notch) and 114.75 across,\n"
             "19 and 57 in: the two capacitor ties pass down through them.", fontsize=7.6, color=INK, va="top")
    fig.savefig(OUT / "plate-holes.png", facecolor="white"); plt.close(fig); res.append(OUT / "plate-holes.png")

    # ---- lid, top view, origin at the lid's left front corner (outside)
    fig, plt = _fig(11, 7.2, "Lid: cut-out and hole positions",
                    "Seen from above. Figures in mm from the lid's left end (across) and front face (in), to hole centres.")
    ax = fig.add_axes([0.04, 0.08, 0.92, 0.82]); ax.set_aspect("equal"); ax.set_axis_off()
    ax.add_patch(Rectangle((0, 0), L, W, fc="#F3F4F6", ec=INK, lw=1.1))
    cx, cy = P["controller_xy"]
    ox, oy = P["display_open"]; wx, wy = P["window"]
    ax.add_patch(Rectangle((cx - wx / 2 + L / 2, cy - wy / 2 + W / 2), wx, wy, fc="none", ec="#0284C7", lw=0.9, ls="--"))
    ax.add_patch(Rectangle((cx - ox / 2 + L / 2, cy - oy / 2 + W / 2), ox, oy, fc="white", ec=INK, lw=1.1))
    ax.text(cx + L / 2, cy + W / 2, f"display opening\n{ox:.0f} x {oy:.0f}, centred\n{cx + L / 2:.0f} across, {cy + W / 2:.0f} in",
            ha="center", va="center", fontsize=8, color=INK)
    ax.text(cx + L / 2, cy - wy / 2 + W / 2 - 1.5, f"window {wx:.0f} x {wy:.0f} bonded on top (dashed)",
            ha="center", va="top", fontsize=7.5, color="#0284C7")
    dl = []
    for k, (hx, hy) in enumerate(sorted(D["hood_screws"]), 1):
        X, Y = hx + L / 2, hy + W / 2
        ax.add_patch(Circle((X, Y), 1.7, fc="white", ec=INK, lw=0.9))
        right = X > cx + L / 2
        ax.text(X + (3.5 if right else -3.5), Y, f"D{k}", ha="left" if right else "right", va="center", fontsize=7.5,
                color=AC, fontweight="bold")
        dl.append(f"D{k} at {X:.1f}, {Y:.1f}")
    ax.text(6, 22, "Display screw holes, 3.4 mm:\n" + "\n".join(dl), ha="left", va="top", fontsize=7.4, color=AC, linespacing=1.4)
    ix_, iy_ = P["isolator_xy"]
    X, Y = ix_ + L / 2, iy_ + W / 2
    ax.add_patch(Circle((X, Y), P["isolator_r"] - 3, fc="white", ec=INK, lw=1.1))
    ax.text(X, Y - P["isolator_r"] - 2, f"DC isolator: 24 hole at {X:.0f}, {Y:.0f}", ha="center", va="top", fontsize=7.5, color=INK)
    for dx in (-P["isolator_screw_dx"], P["isolator_screw_dx"]):
        ax.add_patch(Circle((X + dx, Y), 2.2, fc="white", ec=INK, lw=0.9))
    ax.text(X, Y + P["isolator_r"] - 1, f"4.4 at {X - P['isolator_screw_dx']:.0f} and {X + P['isolator_screw_dx']:.0f}, {Y:.0f}",
            ha="center", va="bottom", fontsize=7.2, color=AC)
    for (px, py) in D["pillars"]:
        ax.add_patch(Circle((px + L / 2, py + W / 2), P["pillar_r"], fc="#E5E7EB", ec=MUT, lw=0.6))
    ax.text(L - 14, 4, "lid screw pillars (bought case): do not drill", ha="right", va="bottom", fontsize=7, color=MUT)
    ax.text(L / 2, -3, "front face (user side)", ha="center", va="top", fontsize=7.5, color=MUT)
    ax.text(-3, W / 2, "left end (sensor gland, USB-C)", ha="right", va="center", fontsize=7.5, color=MUT, rotation=90)
    ax.text(L + 3, W / 2, "right end (test leads)", ha="left", va="center", fontsize=7.5, color=MUT, rotation=90)
    ax.set_xlim(-12, L + 12); ax.set_ylim(-10, W + 4)
    fig.savefig(OUT / "lid-holes.png", facecolor="white"); plt.close(fig); res.append(OUT / "lid-holes.png")

    # ---- case: both ends and the floor
    fig, plt = _fig(12, 7.6, "Enclosure body: hole positions in the ends and the floor",
                    "Ends seen from outside; floor seen from above, as you look into the open body. "
                    "Figures in mm from the outside faces, to hole centres.")
    zs = P["z_split"]
    # right end, seen from outside (+X): front face on the left of the view
    axr = fig.add_axes([0.03, 0.56, 0.44, 0.34]); axr.set_aspect("equal"); axr.set_axis_off()
    axr.add_patch(Rectangle((0, 0), W, zs, fc="#F3F4F6", ec=INK, lw=1.1))
    for y in (-P["gland_y"], P["gland_y"]):
        Y = y + W / 2
        axr.add_patch(Circle((Y, P["gland_z"]), 8.1, fc="white", ec=INK, lw=1))
        axr.add_patch(Circle((Y, P["gland_z"]), P["gland_lead_r"] + 2, fc="none", ec=MUT, lw=0.6, ls="--"))
        axr.text(Y, P["gland_z"] - 13, f"16.2 at {Y:.0f}", ha="center", va="top", fontsize=7.2, color=AC)
    axr.text(W / 2, zs + 2, f"Right end (test lead glands), {P['gland_z']:.0f} up", ha="center", va="bottom", fontsize=8.5,
             fontweight="bold", color=INK)
    axr.text(1, -2, "front face", ha="left", va="top", fontsize=7, color=MUT)
    axr.text(W - 1, -2, "back", ha="right", va="top", fontsize=7, color=MUT)
    axr.set_xlim(-4, W + 4); axr.set_ylim(-8, zs + 10)
    # left end, seen from outside (-X): back on the left of the view
    axl = fig.add_axes([0.52, 0.56, 0.44, 0.34]); axl.set_aspect("equal"); axl.set_axis_off()
    axl.add_patch(Rectangle((0, 0), W, zs, fc="#F3F4F6", ec=INK, lw=1.1))
    for (y, z, d, lab) in ((P["gland_sensor_y"], P["gland_z"], 12.2, "M12 gland"), (P["usb_y"], P["usb_z"], 16.2, "USB-C")):
        Y = W / 2 - y   # back on the left as seen from outside the left end
        axl.add_patch(Circle((Y, z), d / 2, fc="white", ec=INK, lw=1))
        above = lab.startswith("M12")
        axl.text(Y, z + d / 2 + 3 if above else z - d / 2 - 3, f"{lab}: {d:.1f}\n{y + W / 2:.0f} from front, {z:.0f} up",
                 ha="center", va="bottom" if above else "top", fontsize=7.2, color=AC)
    axl.text(W / 2, zs + 2, "Left end (sensor gland, USB-C socket)", ha="center", va="bottom", fontsize=8.5,
             fontweight="bold", color=INK)
    axl.text(1, -2, "back", ha="left", va="top", fontsize=7, color=MUT)
    axl.text(W - 1, -2, "front face", ha="right", va="top", fontsize=7, color=MUT)
    axl.set_xlim(-4, W + 4); axl.set_ylim(-8, zs + 10)
    # floor
    axf = fig.add_axes([0.03, 0.07, 0.62, 0.42]); axf.set_aspect("equal"); axf.set_axis_off()
    axf.add_patch(Rectangle((0, 0), L, W, fc="#F3F4F6", ec=INK, lw=1.1))
    axf.add_patch(Rectangle((P["wall"], P["wall"]), L - 2 * P["wall"], W - 2 * P["wall"], fc="none", ec=MUT, lw=0.5, ls=":"))
    for i, (fx, fy) in enumerate(P["plate_feet"], 1):
        X, Y = fx + L / 2, fy + W / 2
        axf.add_patch(Circle((X, Y), 3.0, fc="white", ec=INK, lw=1))
        axf.text(X + (5 if X < L - 30 else -5), Y, f"F{i}", fontsize=7.5, color=AC, fontweight="bold", va="center",
                 ha="left" if X < L - 30 else "right")
    for (px, py) in D["pillars"]:
        axf.add_patch(Circle((px + L / 2, py + W / 2), P["pillar_r"], fc="#E5E7EB", ec=MUT, lw=0.6))
    axf.text(L / 2, W + 2, "Floor, seen from above", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=INK)
    axf.text(L / 2, -2, "front face", ha="center", va="top", fontsize=7, color=MUT)
    axf.text(-2, W / 2, "left end", ha="right", va="center", fontsize=7, color=MUT, rotation=90)
    axf.set_xlim(-8, L + 4); axf.set_ylim(-8, W + 10)
    rows = [(f"F{i}", f"{fx + L / 2:.0f}", f"{fy + W / 2:.1f}".rstrip("0").rstrip(".")) for i, (fx, fy) in enumerate(P["plate_feet"], 1)]
    fig.text(0.68, 0.46, "Floor holes: 3.4 mm, countersunk\nfrom below for M3 screws", fontsize=8.5, fontweight="bold",
             color=INK, va="top")
    _table(fig, 0.68, 0.39, rows, ("Hole", "from left end", "from front"), dy=0.032, widths=(0.06, 0.1, 0.1))
    fig.savefig(OUT / "case-holes.png", facecolor="white"); plt.close(fig); res.append(OUT / "case-holes.png")
    return res


# ----------------------------------------------------------------- joints
def frame_section():
    """A short length of a typical module frame, in the pod's own frame, for joint 8."""
    from build123d import Box, Pos
    y0 = P["pod"][1] / 2 + P["clip_spine"]
    top = P["pod"][2] / 2
    h = 35.0
    fr = (Pos(0, y0 + 0.75, top - h / 2) * Box(60, 1.5, h)
          + Pos(0, y0 + 9, top - 0.75) * Box(60, 18, 1.5)
          + Pos(0, y0 + 10, top - h + 0.75) * Box(60, 20, 1.5))
    glass = Pos(0, y0 + 40, top - 4) * Box(60, 60, 4)
    return fr, glass


def joints(only=None):
    out = []
    pz0, pz1 = D["plate_bot"], D["plate_top"]
    cx, cy = P["controller_xy"]

    def J(n, parts, title, sub, **kw):
        if only and n not in only:
            return
        out.append(bv.joint(parts, OUT / f"joint-{n:02d}.png", f"Joint {n}: {title}", subtitle=sub, **kw))

    # 1 test lead gland through the right end, cut on the gland's centre line
    b_ = (L / 2 - 52, L / 2 + 26, -48, 4, 0, P["gland_z"])
    J(1, [part("End wall of the body", win(C["body"], *b_), COL["body"]),
          part("M16 gland (seal outside)", win(C["glands"], *b_), COL["glands"]),
          part("Locknut inside", win(C["gland_nuts"], *b_), "#475569"),
          part("Fuse holder (2 mm clear)", win(C["fuse"], *b_), COL["fuse"]),
          part("Chassis plate", win(C["plate"], *b_), COL["plate"]),
          part("Test lead", win(C["leads"], *b_), "#991B1B")],
      "test lead gland through the right end (cut level with the glands)",
      "Seen from above. The gland's seal is outside, its locknut inside, 2 mm clear of the fuse holder",
      elev=70, azim=-90, size=(8, 6))
    # 2 plate standoff, cut through its centre
    fx, fy = P["plate_feet"][3]
    b_ = (fx - 22, fx + 22, fy, fy + 14, -4, 22)
    J(2, [part("Case floor", win(C["body"], *b_), COL["body"]),
          part("Nylon standoff, 5 mm", win(C["plate_standoffs"], *b_), COL["standoff"]),
          part("M3 screws: countersunk below, pan head above", win(C["plate_screws"], *b_), COL["bolt"]),
          part("Chassis plate", win(C["plate"], *b_), COL["plate"]),
          part("Capacitor", win(C["caps"], *b_), COL["caps"])],
      "chassis plate on a standoff (cut through the standoff)",
      "Seen from the front. Countersunk screw flush under the floor; pan head on the plate; 5 mm gap under the plate",
      elev=10, azim=-80, size=(8, 6))
    # 3 capacitor tie through the right-hand slot, cut on the tie
    xs = P["cap_x"][-1] + P["cap_d"] / 2
    ty = P["tie_y"][0]
    b_ = (xs - 30, xs + 18, ty, ty + 25, 0, 50)
    J(3, [part("Chassis plate", win(C["plate"], *b_), COL["plate"]),
          part("Capacitor (bed of silicone under it)", win(C["caps"], *b_), COL["caps"]),
          part("Cable tie, round all three capacitors", win(C["cap_ties"], *b_), COL["ties"]),
          part("MOSFET bar", win(C["fet_bar"], *b_), COL["bar"]),
          part("Discharge resistor", win(C["dump_res"], *b_), COL["dump"]),
          part("Case floor", win(C["body"], *b_), COL["body"])],
      "capacitor tie through its plate slot (cut on the tie)",
      "Seen from the front. The tie passes down through the slot, under the plate and up the far side",
      elev=12, azim=-70, size=(8, 6))
    # 4 MOSFET on the bar, seen from the back
    fx_, fy_ = P["fets_xy"]
    b_ = (fx_ - 26, fx_ + 26, fy_ - 12, fy_ + 14, pz0 - 4, pz1 + 30)
    J(4, [part("MOSFET bar", win(C["fet_bar"], *b_), COL["bar"]),
          part("MOSFETs (2), on insulating pads", win(C["fets"], *b_), COL["fets"]),
          part("M3 screws with insulating bushings", win(C["fet_screws"], *b_), COL["bolt"]),
          part("Chassis plate", win(C["plate"], *b_), COL["plate"])],
      "MOSFETs on the bar, bar on the plate",
      "Seen from the back right. Each tab on an insulating pad; two M3 screws come up through the plate into the bar",
      elev=22, azim=55, size=(8, 6))
    # 5 display stack under the hood: cut through a hood screw
    sx, sy = D["hood_screws"][3]
    b_ = (sx - 20, sx + 14, sy, sy + 14, D["pcb_bot"] - 6, H + 20)
    J(5, [part("Lid", win(C["lid"], *b_), COL["lid"]),
          part("Window, bonded with gasket tape", win(C["window"], *b_), COL["window"]),
          part("Sun hood: side wall and screw tab", win(C["hood"], *b_), "#94A3B8"),
          part("M3 x 20 screw, sealing washer", win(C["hood_screws"], *b_), COL["bolt"]),
          part("Spacer, 7 mm", win(C["display_standoffs"], *b_), COL["standoff"]),
          part("Display board", win(C["controller"], *b_), COL["ctrl"]),
          part("Nut", win(C["display_nuts"], *b_), "#374151")],
      "hood, lid, spacer and display board on one screw (cut through it)",
      "Seen from the front. One screw holds the hood on top and the display board underneath",
      elev=10, azim=-80, size=(8, 6))
    # 6 DC isolator through the lid, cut on its centre line
    ix_, iy_ = P["isolator_xy"]
    b_ = (ix_ - 34, ix_ + 34, iy_, iy_ + 25, 24, H + 26)
    J(6, [part("Lid", win(C["lid"], *b_), COL["lid"]),
          part("DC isolator", win(C["isolator"], *b_), COL["isolator"]),
          part("Maker's fixing screws (2), into its flange", win(C["isolator_screws"], *b_), COL["bolt"])],
      "DC isolator through the lid (cut on its centre line)",
      "Seen from the front. The body hangs under the lid on its flange and lifts out with the lid",
      elev=10, azim=-80, size=(8, 6))
    # 7 left end: USB-C socket and sensor gland, cut through the socket
    b_ = (-L / 2 - 18, -L / 2 + 30, 8, 62, 0, 32)
    J(7, [part("Left end wall", win(C["body"], *b_), COL["body"]),
          part("USB-C socket and cap", win(C["usb"], *b_), COL["usb"]),
          part("Socket locknut", win(C["usb_nut"], *b_), "#475569"),
          part("M12 sensor gland", win(S("glands", "gland_nuts"), *b_), COL["glands"]),
          part("Cell holder", win(C["battery"], *b_), COL["battery"]),
          part("Chassis plate", win(C["plate"], *b_), COL["plate"])],
      "USB-C socket and sensor gland in the left end (cut level with them)",
      "Seen from above. Both are held by locknuts inside, clear of the cell holder",
      elev=70, azim=-90, size=(8, 6))
    # 8 sensor pod clip on a module frame, cut through the thumb screw
    fr, glass = frame_section()
    b_ = (0, 60, -BIG, BIG, -BIG, BIG)
    J(8, [part("Pod housing", win(POD["housing"], *b_), COL["housing"]),
          part("Reference cell", win(POD["cell"], *b_), COL["cell"]),
          part("Clip", win(POD["clip"], *b_), COL["clip"]),
          part("M6 thumb screw", win(POD["thumb"], *b_), COL["bolt"]),
          part("M4 screws into inserts", win(POD["clip_screws"], *b_), "#374151"),
          part("Module frame (site's module)", win(fr, *b_), COL["frame"]),
          part("Module glass", win(glass, *b_), "#CBD5E1")],
      "sensor pod clip on a module frame (cut through the thumb screw)",
      "Seen from the end. Top jaw on the frame edge; the thumb screw presses up under the frame's bottom flange",
      elev=8, azim=10, size=(8, 6))
    return out


# ----------------------------------------------------------------- assembly steps
def steps(only=None):
    from build123d import Pos
    M = made()
    out = []

    def st(n, done, new, title, sub, **kw):
        if only and n not in only:
            return
        out.append(bv.step(done, new, OUT / f"step-{n:02d}.png", f"Step {n}: {title}", subtitle=sub, **kw))

    def mv(p, e):
        return Part(p.name, p.shape, p.color, None, tuple(e), p.alpha)

    body, plate = M["body"], M["plate"]
    st(1, [body], [mv(part("Standoffs (5)", C["plate_standoffs"], COL["standoff"]), (0, 0, 60)),
                   mv(part("Countersunk M3 screws from below", win(C["plate_screws"], -BIG, BIG, -BIG, BIG, -BIG, D["floor"] + 4),
                           COL["bolt"]), (0, 0, -40))],
       "standoffs into the case floor", "Five M3 countersunk screws up through the floor, a dab of sealant on each; standoffs snug",
       elev=40, azim=-55, label_done=False)
    st(2, [body, part("Standoffs", C["plate_standoffs"], "#9CA3AF")],
       [mv(M["leadg"], (60, 0, 0)), mv(M["leftg"], (-60, 0, 0))],
       "glands and USB-C socket into the ends", "Seals and caps outside, locknuts inside, hand tight plus a quarter turn",
       elev=25, azim=-60, label_done=False)
    st(3, [plate], [mv(part("MOSFETs on pads, screwed to the bar", S("fets", "fet_screws"), COL["fets"]), (0, 40, 0)),
                    mv(part("MOSFET bar", C["fet_bar"], COL["bar"]), (0, 0, 50))],
       "MOSFETs onto the bar, bar onto the plate", "Insulating pad and bushing on each tab; two M3 screws up through the plate into the bar",
       elev=30, azim=40, label_done=False)
    bar = part("MOSFET bar", S("fet_bar", "fets", "fet_screws"), COL["fets"])
    st(4, [plate, bar], [mv(M["dump"], (0, -20, 50)), mv(M["fuse"], (0, 0, 60)), mv(M["battery"], (0, 0, 50))],
       "discharge resistor, fuse holder and cell holder", "Each on two M3 screws with nuts under the plate. No cell in the holder, no fuse in the holder",
       elev=35, azim=-55, label_done=False)
    on1 = [plate, bar, part("Resistor, fuse, cell holders", S("dump_res", "fuse", "battery"), "#9CA3AF")]
    st(5, on1, [mv(M["meas"], (0, 0, 60)), mv(M["iso"], (0, 0, 60))],
       "measurement and isolation boards", "Each on four 6 mm nylon standoffs, M3 screws from under the plate",
       elev=35, azim=-55, label_done=False)
    on2 = on1 + [part("Boards", S("meas", "isolation", "board_standoffs"), "#9CA3AF")]
    st(6, on2, [mv(part("Load capacitors (3)", C["caps"], COL["caps"]), (0, 0, 60)),
                mv(part("Cable ties (2)", C["cap_ties"], COL["ties"]), (0, 0, 110))],
       "capacitors and their ties", "Bed of silicone under each; pins to the front; two ties down through the slots, round all three, pulled tight",
       elev=35, azim=-55, label_done=False)
    plate_all = part("Chassis plate with everything on it",
                     S("plate", "fet_bar", "fets", "fet_screws", "dump_res", "fuse", "battery", "meas", "isolation",
                       "board_standoffs", "caps", "cap_ties", "plate_fixings"), COL["plate"])
    st(7, [body, M["leadg"], M["leftg"], part("Standoffs", C["plate_standoffs"], "#9CA3AF")], [mv(plate_all, (0, 0, 110))],
       "plate into the case", "Lower it past the corner pillars onto the standoffs; five M3 pan-head screws. Then wire it (wiring diagram)",
       elev=35, azim=-55, label_done=False)
    lid = M["lid"]
    lid_up = Pos(0, 0, 0)
    st(8, [lid], [mv(M["window"], (0, 0, 50))], "window onto the lid",
       "Clean both faces with isopropyl alcohol; press the gasket tape down all round for 30 s",
       elev=40, azim=-55, label_done=False)
    iso_body = win(C["isolator"], -BIG, BIG, -BIG, BIG, -BIG, H - 0.01)
    iso_top = win(C["isolator"], -BIG, BIG, -BIG, BIG, H - 0.01, BIG)
    st(9, [lid, part("Window", C["window"], "#9CA3AF")],
       [mv(part("Isolator body and flange", iso_body, COL["isolator"]), (0, 0, -60)),
        mv(part("Maker's two screws", C["isolator_screws"], COL["bolt"]), (0, 0, 40)),
        mv(part("Knob and handle", iso_top, "#B45309"), (0, 0, 70))], "DC isolator into the lid",
       "Body from below, its flange against the lid; the maker's two screws from above; then the knob and handle",
       elev=20, azim=-55, label_done=False)
    st(10, [lid, part("Window and isolator", S("window", "isolator", "isolator_screws"), "#9CA3AF")],
       [mv(part("Sun hood and four screws", S("hood", "hood_screws"), COL["hood"]), (0, 0, 50)),
        mv(part("Display board, spacers and nuts", S("controller", "display_standoffs", "display_nuts"), COL["ctrl"]), (0, -75, -55))],
       "sun hood on top, display board underneath",
       "Four M3 x 20 screws with sealing washers down through hood tabs, lid and spacers; nuts under the board",
       elev=15, azim=-55, label_done=False)
    lid_all = part("Lid with window, isolator, hood and display board",
                   S("lid", "window", "isolator", "isolator_screws", "hood", "hood_screws", "controller",
                     "display_standoffs", "display_nuts"), "#93C5FD")
    st(11, [body, M["leadg"], M["leftg"], plate_all], [mv(lid_all, (0, 0, 110))], "close the case",
       "Connect the isolator and display leads with a service loop; gasket clean; lid screws evenly in a cross pattern",
       elev=25, azim=-55, label_done=False)
    st(12, [part("Pod housing", POD["housing"], COL["housing"])],
       [mv(part("Reference cell, bonded", POD["cell"], COL["cell"]), (0, 0, 40)),
        mv(part("Clip and two M4 screws", POD["clip"] + POD["clip_screws"] + POD["thumb"], COL["clip"]), (0, 45, 0)),
        mv(part("M12 cable gland", POD["pod_gland"], COL["glands"]), (-40, 0, 0))],
       "sensor pod", "Cell bonded on top with silicone; clip screwed to the inserts; cable through the gland",
       elev=25, azim=-130, label_done=False)
    return out


# ----------------------------------------------------------------- wiring
def wiring():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    fig = plt.figure(figsize=(12, 7.6), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 120); ax.set_ylim(0, 76); ax.set_axis_off()
    INK, MUT = "#111827", "#4B5563"
    ax.text(2, 74, "PVTrace prototype: block-level wiring", fontsize=13, fontweight="bold", color=INK, va="top")
    ax.text(2, 70.6, "Bought modules and hand-wired perfboard at block level; no circuit board is laid out. "
            "Stranded copper; ferrules on every screw terminal.", fontsize=8.5, color=MUT, va="top")
    ax.text(2, 1.5, "BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT", fontsize=7, color="#B45309")
    ax.text(118, 1.5, REPO, fontsize=7, color="#0F766E", ha="right", family="monospace")
    # the two sides and the barrier
    ax.add_patch(FancyBboxPatch((2, 16), 68, 48, boxstyle="round,pad=0.4", fc="#FEF2F2", ec="#FCA5A5", lw=1, ls="--", zorder=0))
    ax.text(3.5, 62.8, "PV side: live at module voltage, up to 100 V DC and 20 A", fontsize=8, color="#991B1B", va="top")
    ax.add_patch(FancyBboxPatch((82, 16), 36, 48, boxstyle="round,pad=0.4", fc="#F0FDFA", ec="#5EEAD4", lw=1, ls="--", zorder=0))
    ax.text(83.5, 62.8, "Controller side: 3.7 V cell, 5 V", fontsize=8, color="#115E59", va="top")
    ax.plot([76, 76], [16, 64], color="#DB2777", lw=2.4, ls=(0, (6, 3)), zorder=0)
    ax.text(76, 65.4, "isolation barrier", ha="center", fontsize=7.6, color="#DB2777", fontweight="bold")

    def blk(x, y, w, h, title, sub, color):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3", fc="white", ec=color, lw=1.8, zorder=2))
        ax.text(x + w / 2, y + h - 1.2, title, ha="center", va="top", fontsize=8.4, fontweight="bold", color=INK, zorder=3)
        ax.text(x + w / 2, y + 1.2, sub, ha="center", va="bottom", fontsize=6.8, color=MUT, linespacing=1.3, zorder=3)

    def wire(pts, color, lw=2.0):
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", zorder=1)

    def lab(x, y, text, color, ha="center", va="bottom"):
        ax.text(x, y, text, fontsize=6.8, color=color, ha=ha, va=va, zorder=4)
    RED, BLK, BLU, GRY = "#B91C1C", "#111827", "#1D4ED8", "#6B7280"
    blk(4, 49, 12, 10, "Test leads", "MC4, 4 mm²,\nM16 glands", "#991B1B")
    blk(21, 49, 10, 10, "DC fuse", "20 A gPV,\nholder", "#DC2626")
    blk(36, 49, 11, 10, "DC isolator", "2-pole,\nin the lid", "#F59E0B")
    blk(53, 49, 15, 10, "Measurement", "shunt, divider, ADC,\ngate supply", "#16A34A")
    blk(19, 23, 13, 10, "Discharge\nresistor", "22 ohm 50 W", "#B45309")
    blk(37, 23, 12, 10, "MOSFET bar", "load and dump\nMOSFETs", "#7C3AED")
    blk(53, 23, 15, 10, "Load capacitors", "3 x 2200 µF 160 V,\n10 k bleed", "#1D4ED8")
    blk(72, 42, 8, 14, "Isolation", "digital\nisolator,\n1 W DC-DC", "#DB2777")
    blk(86, 46, 14, 12, "Display board", "ESP32, TFT,\nmicroSD, ADC\nfor the pod", "#0F766E")
    blk(104, 46, 12, 12, "Sensor pod", "reference cell,\nprobe; 3 m cable,\nM12 gland", "#0EA5E9")
    blk(86, 22, 14, 12, "Cell, charger", "18650, USB-C\ncharger, 5 V boost", "#C2410C")
    blk(104, 23, 12, 9, "USB-C socket", "IP65, cap", "#374151")
    # PV + path along the top row
    wire([(16, 54), (21, 54)], RED); lab(18.5, 54.6, "4 mm²", RED)
    wire([(31, 54), (36, 54)], RED); lab(33.5, 54.6, "4 mm²", RED)
    wire([(47, 54), (53, 54)], RED); lab(50, 54.6, "4 mm²", RED)
    wire([(64, 49), (64, 33)], RED); lab(63.4, 43, "cap +,\n4 mm²", RED, "right", "center")
    # PV - path
    wire([(53, 28), (49, 28)], BLK); lab(51, 28.6, "cap -", BLK)
    wire([(44, 33), (44, 49)], BLK); lab(44.6, 39.5, "PV -,\n4 mm²", BLK, "left", "center")
    wire([(10, 49), (10, 44), (39, 44), (39, 49)], BLK); lab(24.5, 44.6, "- lead to isolator pole 2, 4 mm²", BLK)
    # dump path and gate drive
    wire([(32, 28), (37, 28)], RED); lab(34.5, 28.6, "2.5 mm²", RED)
    wire([(55, 49), (55, 38), (47, 38), (47, 33)], GRY, 1.2); lab(51, 36.4, "gate drive", GRY, "center", "top")
    # across the barrier
    wire([(68, 53), (72, 53)], BLU, 1.2)
    wire([(80, 53), (86, 53)], BLU, 1.2); lab(83, 53.6, "SPI", BLU)
    wire([(86, 28), (78.5, 28), (78.5, 42)], RED, 1.2); lab(82.2, 28.6, "5 V", RED)
    wire([(93, 34), (93, 46)], RED, 1.2); lab(93.6, 40, "5 V, 0.5 mm²", RED, "left", "center")
    wire([(104, 52), (100, 52)], BLU, 1.2); lab(102, 52.6, "0.25", BLU)
    wire([(104, 27.5), (100, 27.5)], RED, 1.2); lab(102, 28.1, "charge", RED)
    ax.text(3, 10.2, "Safety: no fuse and no cell in their holders, and the isolator open, until the stop points in section 6 of the plan "
            "are passed. Treat the capacitors as charged until the display reads below 30 V.",
            fontsize=7.4, color="#B45309", fontweight="bold")
    ax.text(3, 6.6, "Red: power. Black: PV return. Blue: signal. Grey: gate drive. "
            "The USB-C socket, cell, display board and sensor pod are on the controller side only.", fontsize=7.2, color=MUT)
    out = OUT / "wiring.png"
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white"); plt.close(fig)
    return out


if __name__ == "__main__":
    args = sys.argv[1:] or ["overview", "sheets", "layouts", "joints", "steps", "wiring"]
    fns = {"overview": overview, "sheets": sheets, "layouts": layouts, "joints": joints, "steps": steps, "wiring": wiring}
    i = 0
    while i < len(args):
        w = args[i]
        nums = []
        while i + 1 < len(args) and args[i + 1].isdigit():
            nums.append(int(args[i + 1])); i += 1
        r = fns[w](nums) if nums else fns[w]()
        print(w, "->", r)
        i += 1
