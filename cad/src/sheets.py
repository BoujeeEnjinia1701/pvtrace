"""PVTrace general arrangement drawing PVT-DWG-001 (Rev P3).

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
          rev="P3", author="Amish Chadha", date="2026-10-01", concept=True,
          material="Case IP54 ABS, light grey; window and chassis plate PC; hood PETG. See bom/bom.csv, PVT-CAL-001",
          revisions=[("P1", "Preliminary GA, 6.6 mF and isolation barrier (PVT-DDR-001)", "2026-09-25", "AC"),
                     ("P2", "Display sun hood added (PVT-DDR-002)", "2026-09-25", "AC"),
                     ("P3", "Constructable design: plate, fixings, USB-C (PVT-DDR-003)", "2026-10-01", "AC")])
s.add_ortho(views, ["front", "top", "right"])
s.add_svg(views["iso"], 276, 40, 140, 76, label="Isometric view", sublabel="Not to scale")
s.add_notes("Key dimensions and interfaces (mm)", [
    f"Case {P['case_l']:.0f} x {P['case_w']:.0f} x {P['case_h']:.0f}; 234 x 144 over bumpers",
    f"Wall {P['wall']:.0f}; parting line Z {P['z_split']:.0f}; knob and hood top Z 98",
    f"+X end: 2 x M16 glands at Y +/-{P['gland_y']:.0f}, Z {P['gland_z']:.0f}, test leads 4 mm2",
    f"-X end: M12 sensor gland Y {P['gland_sensor_y']:.0f}; USB-C socket Y {P['usb_y']:.0f}",
    "Chassis plate PC 1.5 on five 5 mm standoffs",
    f"Load: {P['n_caps']} x 2200 uF 160 V, 6.6 mF, 2 cable ties",
    "Isolation board between measurement side and controller",
    f"Window {P['window'][0]:.0f} x {P['window'][1]:.0f} bonded over {P['display_open'][0]:.0f} x {P['display_open'][1]:.0f} opening",
    "Display board on 4 spacers; hood screws hold both",
    "Rating 100 V DC, 20 A; 20 A gPV fuse; 2-pole DC isolator",
    "Stored energy up to 33 J; dump 22 ohm, bleed 10 kohm",
    "Mass about 1.49 kg with leads and pod (PVT-CAL-001)",
    "Making sketches PVT-DWG-101 to 108",
    "PRELIMINARY, NOT FOR FABRICATION",
], x=276, y=128, width=140)
s.save(ROOT / "cad/drawings/PVT-DWG-001")
shutil.rmtree(work, ignore_errors=True)
print("wrote cad/drawings/PVT-DWG-001.svg, .pdf, .png")
