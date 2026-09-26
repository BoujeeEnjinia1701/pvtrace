"""PVTrace general arrangement drawing PVT-DWG-001 (Rev P1).

Run from the repo root:  python cad/src/sheets.py
Builds cad/drawings/PVT-DWG-001.svg, .pdf and .png from the parametric model.
The concept blueprint in media/ is PVT-DWG-010.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".kit"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawing import Sheet, project_views  # noqa: E402
from model import PARAMS as P, assemblies, build_parts  # noqa: E402

parts = build_parts()
asm = assemblies(parts)["pvtrace-assembly"]
work = ROOT / "cad/drawings/_views"
views = project_views(asm, work)

s = Sheet(project="PVTrace", title="General arrangement, handheld tracer", dwg_no="PVT-DWG-001",
          rev="P1", author="Amish Chadha", date="2026-09-25", concept=True,
          material="Case IP54 ABS, light grey; window 3 mm PC. See bom/bom.csv and PVT-CAL-001",
          revisions=[("P1", "Preliminary GA, 6.6 mF and isolation barrier (PVT-DDR-001)", "2026-09-25", "AC")])
s.add_ortho(views, ["front", "top", "right"])
s.add_svg(views["iso"], 276, 30, 140, 84, label="Isometric view", sublabel="Not to scale")
s.add_notes("Key dimensions and interfaces (mm)", [
    f"Case {P['case_l']:.0f} x {P['case_w']:.0f} x {P['case_h']:.0f}; 234 x 144 over bumpers",
    f"Wall {P['wall']:.0f}; parting line Z {P['z_split']:.0f}; knob top Z 98",
    f"+X end: 2 x M16 glands at Y +/-{P['gland_y']:.0f}, Z 30, test leads 4 mm2",
    "-X end: M12 gland, sensor pod cable 3 m",
    f"Load: {P['n_caps']} x 2200 uF 160 V, 6.6 mF, along Y on floor",
    "Isolation board between measurement side and controller",
    f"Display window {P['window'][0]:.0f} x {P['window'][1]:.0f} over controller",
    "Rating 100 V DC, 20 A; 20 A gPV fuse; 2-pole DC isolator",
    "Stored energy up to 33 J; dump 22 ohm, bleed 10 kohm",
    "Mass about 1.41 kg with leads and pod (PVT-CAL-001)",
    "Sensor pod 100 x 70 x 22 plus frame clip: see STEP",
    "PRELIMINARY, NOT FOR FABRICATION",
], x=276, y=128, width=140)
s.save(ROOT / "cad/drawings/PVT-DWG-001")
shutil.rmtree(work, ignore_errors=True)
print("wrote cad/drawings/PVT-DWG-001.svg, .pdf, .png")
