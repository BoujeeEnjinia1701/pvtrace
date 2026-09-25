# Review note: PVTrace

## Session 2026-09-25: /populate to a strong TRL 2

### What was done

- `docs/01-problem.md` (PVT-PRB-001 v0.2): problem with cited evidence, users and context, prior work (IV Swinger 2, Cáceres et al. 2020, González et al. 2021, commercial tracers), constraints, out of scope, co-design checklist, open questions, safety.
- `docs/03-requirements.md` (PVT-REQ-001 v0.2): 17 measurable requirements (R1 to R17) with targets, verification and a concept status column, plus assumptions.
- `docs/02-concept.md` (PVT-PRC-001 v0.2): how it works, 13 numbered components, sweep time and energy table, resolution, discharge, battery, STC uncertainty, mass and cost estimates, draft fault and grading rules, proposed design choices, links to CellCheck and CalRig, safety, open questions.
- `cad/src/concept_media.py`: massing model of the handheld tracer (case, lid, controller and display, measurement board, capacitors, MOSFET bar, dump resistor, fuse, isolator, cell, MC4 leads, sensor pod). A grey 1,722 x 1,134 mm module on a 30° stand, with its own leads, is the context part for scale instead of the 1.75 m person, because the tracer is handheld.
- `media/`: hero, blueprint sheet (PNG, PDF, SVG), exploded view with callouts 1 to 12, cutaway, sweep flow diagram, `model.glb` and `viewer.html`. The script removes the temporary `_views` folders.
- `bom/bom.csv` (13 lines, indicative prices, numbered to match the exploded view) and `bom/bom-notes.md`.
- `README.md`: hero and links line; concept rationale, burning platform, industry and region tables and trigger expanded with cited sources; concept, key components and safety updated.
- `docs/pdf/`: branded PDFs of the three controlled documents.

### Key results (estimates, to be checked at TRL 3)

| Quantity | Estimate | Requirement |
| --- | --- | --- |
| Range | 0 to 100 V, 0 to 20 A | R1, R2 met by design |
| Sweep time, 4.4 mF load | about 13 ms (410 W high-current) to 43 ms (2 x 250 W in series) | **R3 not met** for high-current, lower-voltage modules |
| V-I pairs per sweep | about 325 to 1,070 | R4 met |
| Stored energy per sweep | 1.1 to 12.4 J typical; 22 J at the 100 V limit | |
| Discharge | below 30 V in about 0.12 s active; below 60 V in about 23 s passive | R11 met |
| STC Pmax uncertainty | about ±5 to 6 % | R8 at risk |
| Mass | about 1.35 kg | R12 met |
| Battery life | about 16 h | R14 met |
| Parts cost | about $149 | R17 met, margin about $1 |

Requirements not met or at risk:

- **R3 (sweep 20 ms or longer) not met** for high-current modules (about 13 ms). A third capacitor would fix it (item 3 below) but breaks the budget.
- **R13 sunlight readability not met** with a commodity TFT (unverified; the display type is item 5).
- **R16 insulation screening not met**; it is out of scope for this instrument, and second-life resale also needs an insulation test.
- **R8 at risk** until the reference cell calibration route (item 6) is chosen; R5 to R7 and R9 are unverified.

### Proposed, awaiting Amish

1. **Load type.** Capacitive (recommended), electronic MOSFET load, or relay-switched resistor bank.
2. **Rating.** 100 V, 20 A (recommended; stays below the 120 V DC extra-low-voltage limit), 60 V, 15 A single-module only, or high-voltage strings (not recommended).
3. **Load capacitance.** 4.4 mF (baseline, fits budget, misses R3) or 6.6 mF (recommended, about +$6).
4. **Galvanic isolation** of the controller and USB from the PV side. Option A procedural lockout (baseline), option B digital isolator and isolated DC-DC (recommended, about +$8).
5. **Display.** 2.8 in TFT plus phone export (recommended), phone only, or transflective display (about +$10).
6. **Irradiance reference.** Reference cell calibrated once against a pyranometer (recommended), silicon pyranometer, or known-good module.
7. **Controller.** ESP32 display board (recommended) or RP2040 with a separate display.
8. **Grade thresholds.** A 90 % or more of nameplate, B 80 to 90 %, C 70 to 80 %, reject below 70 % or with a visible safety defect; to be agreed with a partner.
9. **Budget.** Items 3 and 4 together take parts to about $163. Proposed: raise `budget_usd` from 150 to 165, awaiting Amish. No change made to `project.yaml`.
10. **First partner** for co-design: a second-life panel refurbisher or recycler, or a TVET solar course.
11. `pitch` and `problem` in `project.yaml` were left unchanged; the evidence supports them.

### Safety concerns

- Live DC at up to 100 V and 20 A from a source that cannot be switched off; sustained DC arcs if a connector is pulled under load. The design only opens the circuit near zero current and uses a DC-rated isolator and fuse.
- Up to 22 J stored in the load capacitors; active and passive discharge are both required.
- Without isolation (item 4), the controller ground is the PV negative, so a laptop on USB could be exposed to PV potential; option A relies on a firmware lockout.
- Li-ion cell inside a case that may sit in full sun.
- Mixed-brand MC4 connectors can overheat; heavy, sharp and possibly broken modules; rooftop work at height.

### Problems and notes

- The kit places the context part only in the hero, so the blueprint's orthographic views show the tracer with its leads and sensor pod and are small at the sheet scale; the isometric view shows the full scene.
- The cutaway excludes the leads and sensor pod so the section centers on the enclosure.
- The flow diagram's only numeric value is the energy per sweep for the reference module (5.4 J); the kit scales arrow widths from it, so the arrow after the capacitor is drawn wider.
- The legacy `cad/src/model.py` placeholder is untouched (TRL 3 work).
- The EU WEEE Directive text could not be fetched in this session. Its coverage of PV panels is cited from the EUR-Lex entry but was not re-read; check it at TRL 3. The Jordan and Kurtz figure was confirmed from the NREL research hub record.
- The web search budget ran out partway through research, so the Pakistan and Kenya used-panel markets were not added to the region table.

### Recommended next step

Review this note and the media, then decide items 2 to 4, 6 and 9. If approved, run `/advance-trl3` to check the sweep model with cell capacitance, the discharge and thermal loads, the error budget and the grading rules by calculation, and to produce the parametric model and drawing sheet.
