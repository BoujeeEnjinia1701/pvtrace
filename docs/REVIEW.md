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

### Proposed at TRL 2

Items 1 to 9 and 11: Decided by Amish, 2026-09-25: go with recommendation (PVT-DDR-002). Item 10: still proposed, awaiting Amish.

1. **Load type.** Capacitive (recommended), electronic MOSFET load, or relay-switched resistor bank.
2. **Rating.** 100 V, 20 A (recommended; stays below the 120 V DC extra-low-voltage limit), 60 V, 15 A single-module only, or high-voltage strings (not recommended).
3. **Load capacitance.** 4.4 mF (baseline, fits budget, misses R3) or 6.6 mF (recommended, about +$6).
4. **Galvanic isolation** of the controller and USB from the PV side. Option A procedural lockout (baseline), option B digital isolator and isolated DC-DC (recommended, about +$8).
5. **Display.** 2.8 in TFT plus phone export (recommended), phone only, or transflective display (about +$10).
6. **Irradiance reference.** Reference cell calibrated once against a pyranometer (recommended), silicon pyranometer, or known-good module.
7. **Controller.** ESP32 display board (recommended) or RP2040 with a separate display.
8. **Grade thresholds.** A 90 % or more of nameplate, B 80 to 90 %, C 70 to 80 %, reject below 70 % or with a visible safety defect; to be agreed with a partner.
9. **Budget.** Items 3 and 4 together take parts to about $163. Proposed: raise `budget_usd` from 150 to 165. Decided by Amish, 2026-09-25: go with recommendation; `budget_usd` is now 165.
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

## Session 2026-09-25: TRL 3

### What was done

- `docs/decisions/0001-trl2-review-decisions.md` (PVT-DDR-001 v0.1): items 1 to 8 of the TRL 2 review were adopted for TRL 3 pending Amish's review; items 9 to 13 stayed open. (Since then Decided by Amish, 2026-09-25: go with recommendation for items 1 to 9, 12 and 13; see PVT-DDR-002.)
- `docs/04-calcs/01-sizing.md` (PVT-CAL-001 v0.1) with `docs/04-calcs/sizing.py` and `docs/04-calcs/results.csv`: single-diode sweep model with loop resistance and capacitor tolerance, range and cold Voc, resolution and error budget, STC uncertainty, discharge and opening current, heat in sun, battery, mass and cost. The script reads `cad/src/model.py` and `bom/bom.csv`.
- `cad/src/model.py`: parametric build123d model (case, lid and window, controller, measurement board, isolation board, three capacitors, MOSFET bar, dump resistor, fuse, isolator, battery, lead stubs, sensor pod) with an interference check (no clashes). Exports `cad/step/` and `cad/stl/` for the assembly, the enclosure and the sensor pod.
- `cad/src/sheets.py` and `cad/drawings/PVT-DWG-001` (SVG, PDF, PNG): general arrangement at Rev P1, marked "CONCEPT, NOT FOR FABRICATION" and "PRELIMINARY, NOT FOR FABRICATION". The concept blueprint keeps PVT-DWG-010, so DWG-001 was free.
- `bom/bom.csv`: 14 lines, all priced with supplier types; third capacitor, new line 14 (isolation barrier), light grey case, charger with temperature cut-off. `bom/bom-notes.md` updated.
- `cad/src/concept_media.py` now builds from `model.py`; all media refreshed (hero, blueprint Rev P2, exploded with callouts 1 to 12 and 14, cutaway, flow at 7.9 J, `model.glb`, `viewer.html`). No `_views` folders remain.
- PVT-PRB-001, PVT-PRC-001 and PVT-REQ-001 at v0.3; `README.md` and `project.yaml` (trl 3, trl_target 3, evidence list) updated. PDFs in `docs/pdf/`.

### Requirements (PVT-CAL-001)

Nine met, four not met, two at risk, two not verifiable at TRL 3.

| ID | Status | Value |
| --- | --- | --- |
| R3 | **Not met** (worst-case tolerance) | High-current module 20.5 ms at 6.6 mF nominal, 16.4 ms at -20 % |
| R13 | **Not met** (display readability); heat at risk | About 56 °C inside a light case, 73 °C dark, at 45 °C in sun |
| R16 | **Not met** (out of scope) | No insulation test |
| R17 | **Not met** at $150 | $163; met at the proposed $165 |
| R7, R8 | At risk | STC ±3.7 to ±5.4 %; needs a reference cell within ±4.5 % |
| R6, R9 | Not verifiable at TRL 3 | Instrument noise 0.08 %; about 7 or more samples per volt |
| R1, R2, R4, R5, R10, R11, R12, R14, R15 | Met (R1, R2, R10, R15 by design review; R5 on paper) | 410 pairs minimum; 0.21 s to 30 V, 40 s passive to 60 V; 1.41 kg; 10.3 h |

Corrections to TRL 2 figures: stored energy at 100 V is now 33 J (6.6 mF); battery life is 10.3 h, not 16 h, with the isolated side and boost counted; mass 1.41 kg, not 1.35 kg; the case grows to 220 x 130 x 80 mm; the module still delivers up to 2.5 A at 99 % of Voc, so the load switch must stay closed up to 6 ms longer to open below 0.5 A. The 4.4 mF sweep times from TRL 2 were reproduced within 2 ms.

### Decisions recorded

Decided by Amish, 2026-09-25: go with recommendation (was adopted for TRL 3 pending his review): capacitive load; 100 V, 20 A rating; 6.6 mF; isolation option B; 2.8 in TFT plus phone export; once-calibrated reference cell; ESP32 controller; grade thresholds A 90 %, B 80 %, C 70 %. Pitch and problem are unchanged, as the TRL 2 review recommended.

### Still awaiting Amish (as of the TRL 3 session)

- Budget: $165 recommended (PVT-DDR-001 item 9). Decided by Amish, 2026-09-25: go with recommendation; `budget_usd` now 165.
- First co-design partner: no preference stated (item 10). Still proposed, awaiting Amish.
- R3 at tolerance: fourth capacitor, capacitor selection, or relaxing the bound (item 11, no recommendation yet). Still proposed, awaiting Amish.
- Heat and sun: sun hood for the display (item 12). Decided by Amish, 2026-09-25: go with recommendation; hood added.
- Larger case, 220 x 130 x 80 mm (item 13). Decided by Amish, 2026-09-25: go with recommendation.

### Safety concerns

- 33 J stored at 100 V; both discharge paths are required, and the switch must not open a loaded DC circuit (hold until below 0.5 A).
- Inside temperature in sun can pass the Li-ion charging limit; charge only in shade with the isolator open; keep the temperature cut-off.
- Two 450 W modules in series reach about 109 V when cold; the 100 V check must refuse them and the manual must say so.
- The isolation barrier's working voltage and test rating must be confirmed from datasheets before any build.
- Unchanged from TRL 2: live DC that cannot be switched off, DC arcs, mixed MC4 brands, heavy and broken modules, work at height.

### Problems and notes

- Citations: the EU WEEE coverage of PV panels was verified with WebFetch against the directive text (Article 5(1), Annex I and II category 4) and the link updated. The 20 ms lower bound in R3 and the capacitance of TOPCon and HJT modules could not be checked (WebSearch exhausted), so R3's bound stays a working figure.
- CalRig covers the temperature probe only from 10 to 40 °C; PVTrace modules run at 60 °C or more. This is a range limit, not an interface conflict; CalRig was not edited.
- The kit's cutaway still cuts near the origin; the model is centered on the case, so the section passes through the capacitors. The leads and sensor pod stay excluded from the cutaway.
- The kit's concept sheet shows only the current revision row, so the blueprint shows Rev P2 without its P1 row.
- No TRL 4 material exists in the repo; none was created.

### Recommended next step

TRL 4 is on hold by Amish's instruction. Review PVT-DDR-001 and decide items 9 to 13, especially the budget and the R3 option. For the record only, TRL 4 would need a bench prototype, a lab test report (TST, `environment: lab`) covering sweep time against a known module, discharge, accuracy against a calibrated meter and isolation, and build log entries.

## Session 2026-09-25: recommendations accepted

### Decisions applied

Amish wrote on 2026-09-25: "i accept all your recommendations, go with them across all repos." Twelve PVTrace items are now "Decided by Amish, 2026-09-25: go with recommendation", recorded in `docs/decisions/0002-recommendations-accepted.md` (PVT-DDR-002 v0.1), with statuses updated in PVT-DDR-001 v0.2:

- Items 1 to 8 (capacitive load; 100 V, 20 A; 6.6 mF; isolation option B; TFT plus phone export; once-calibrated reference cell; ESP32; grade thresholds A 90 %, B 80 %, C 70 %) and item 13 (220 x 130 x 80 mm case): already in the design; status wording only.
- Item 9, budget: `budget_usd` in `project.yaml` from **150 to 165**. R17 from not met ($163 against $150) to **met** ($164 against $165, $1 margin).
- Item 12, heat and sun: printed PETG display sun hood added as `bom/bom.csv` line 15 ($1.00). Parts **$163 to $164**; mass **1.41 to 1.43 kg** (R12 still met); hood top at 98 mm, level with the isolator knob, so the envelope is unchanged. Model (`cad/src/model.py`, no clashes), STEP and STL, PVT-DWG-001 **Rev P1 to P2**, concept media (callout 15, blueprint PVT-DWG-010 Rev P3) and PVT-CAL-001 **v0.1 to v0.2** updated.
- TRL 2 note item 11: `pitch` and `problem` unchanged, as recommended.

Documents bumped: PVT-PRB-001 v0.4, PVT-PRC-001 v0.4, PVT-REQ-001 v0.4, PVT-CAL-001 v0.2, PVT-DDR-001 v0.2. README: budget line, concept paragraph, not-met list, and a rewritten "What sparked the idea" (the March 2024 Fighting Jays hailstorm in Fort Bend County, Texas, cited). The old personal-site domain in generated files was replaced with designmolecule.com by re-rendering all PDFs, the drawing and the media.

### Requirement status (PVT-CAL-001 v0.2)

- **Not met (3):** R3 sweep time at -20 % capacitor tolerance (16.4 ms against 20 ms); R13 display readability in sun (sun hood fitted; readability can only be shown in a field check), heat at risk (about 56 °C inside at 45 °C in sun); R16 insulation screening (out of scope).
- **At risk (2):** R7, R8 (reference cell calibration within ±4.5 %).
- **Not verifiable at TRL 3 (2):** R6, R9.
- **Met (10):** R1, R2, R4, R5, R10, R11, R12 (1.43 kg), R14 (10.3 h), R15, R17 ($164 of $165).

### Still awaiting Amish

- Item 10, first co-design partner: no preference stated.
- Item 11, R3 at worst-case tolerance: fourth capacitor (about +$6, which would break the $165 budget), capacitor selection, or relaxing the 20 ms bound. No recommendation was made.

### Cross-repo actions

None for PVTrace. The CalRig temperature range limit (10 to 40 °C) remains a note, not a requested change.

### TRL 4

TRL 4 remains on hold by Amish's instruction. `trl: 3` and `trl_target: 3` are unchanged. The reference cell calibration and the display readability field check follow from the decisions but are TRL 4 work and were not started.

## Session 2026-09-26: sources strengthened

- "What sparked the idea" (README): replaced the trade-press source Renewable Energy World (2024) with *Newsweek* (2024), which reports the March 15, 2024 hailstorm, the 350 MW Fighting Jays farm near Needville in Fort Bend County and the thousands of damaged panels. The VDE Americas (2025) analysis stays as the second source. The inspiration event is unchanged.
- No other weak sources were flagged; all region rows already carry citations. `docs/01-problem.md` did not cite the replaced source, so no controlled document changed.

## Session 2026-09-26: product appearance model and photoreal renders

Amish chose this repo for the first batch of product renders on 2026-09-26.

### What was done

- New `cad/src/product_model.py`: `product_parts()` returns 68 appearance parts (30 shell, 25 internal, 4 accessory, 9 context) with colour, material, BOM line, group and explode offset, plus `TITLE` and three `RENDER_VIEWS` (hero, exploded, in-use). It imports `PARAMS` and `build_parts()` from `cad/src/model.py`; `model.py` has no `derived()` function, so its envelopes are used directly. Every shape is valid and tessellates.
- Appearance detail added: filleted case and lid with a parting-line groove at Z 52; wrap-around rubber corner boots; ribbed rubber side grips; fluted M16 and M12 cable glands; a clear polycarbonate display window over a lit 2.8 in screen showing an IV curve, a power curve, a grade tile and the maximum power point; the printed sun hood with softened edges; a membrane keypad with a teal sweep key, two menu keys and green and amber status LEDs; lid screws; a raised "PVTrace" mark and a yellow "100 V DC" warning label; the DC isolator with base ring, ON/OFF ticks, grey knob and red handle; red and black PV test leads swept to the floor and ending in MC4 connectors; a USB-C port flap.
- Internals for the exploded view: controller board and display module, measurement board with shunt, isolation board, MOSFETs on an aluminium bar with fins, aluminium-clad discharge resistor, fuse holder with a 10 x 38 fuse, three blue capacitors with end discs, 18650 cell in its holder, isolator body. The sensor pod (item 12) is an accessory beside the case.
- Context for the "in-use" view only: the shared clay forearm and hand (grip pose) carrying the tracer by its -X end, fingers under the case floor and thumb round the front corner, beside a small framed 12-cell PV module lying face up; the module's own leads end in MC4 connectors mated to the tracer's leads. The hero view shows the tracer and its leads without context.
- README: hero image now points to `media/render-hero.png`, with an "Exploded render" link added; the orchestrator produces the render files.

### Differences from model.py (Proposed, awaiting Amish)

1. **Plan corner radius.** `model.py` has a square case; the appearance model rounds the vertical edges to R10 and adds top and bottom fillets. Recommendation: accept; real IP54 handheld cases have radiused corners and the main dimensions are unchanged.
2. **Corner bumpers.** `model.py` has 14 mm square bumpers centred on each vertical edge, 40 mm high. The appearance model uses wrap-around boots that stand the same 7 mm proud and reach 24 mm along each face. Recommendation: accept as the look to aim for when a case is chosen.
3. **Additions not in model.py:** keypad and status LEDs, side grips, USB-C flap, labels and the lead routing to the floor (model.py shows 60 mm straight stubs). Recommendation: accept as appearance only; the keypad and LEDs would need a line in the BOM (item 13 or a new line) if they survive to TRL 4.
4. **Sensor pod shape.** The pod keeps the `model.py` envelope, reference cell and clip size, with fillets and a slot in the clip. Recommendation: accept.

### Status

This is an appearance model only: no tolerances, no fabrication detail, nothing past TRL 3. `trl: 3` is unchanged, and TRL 4 remains on hold by Amish's instruction.
- The `in-use` view (clay hand carrying the tracer beside a module) is defined in RENDER_VIEWS but not published: the hand pose read poorly in the render. To revisit with a better carrying pose.
