---
doc_id: PVT-DDR-002
title: PVTrace recommendations accepted
project: PVTrace
doc_type: Design decision record
version: "0.2"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Record Amish's acceptance of all recommendations and the changes made in the repo
- version: "0.2"
  date: '2026-10-02'
  author: Amish Chadha
  change: Items 10 and 11 decided by Amish on 2026-10-02 as recommended in PVT-DEC-001
---

# 0002: Recommendations accepted

- **Date:** 2026-09-25
- **Status:** accepted. Every item with a recommendation is decided by Amish, 2026-09-25: go with recommendation. Items 10 and 11, which had no recommendation, were given recommendations in the design decisions register (PVT-DEC-001, items 5 and 4) and decided by Amish on 2026-10-02: "i approve your recommendations for all 555 open decisions."

## Context

On 2026-09-25 Amish wrote: "i accept all your recommendations, go with them across all repos." This record lists every PVTrace item that the decision closes, what changed in the repo because of it, and what stays open. The items come from the TRL 2 review note (`docs/REVIEW.md`, /populate session) and PVT-DDR-001. Where a recommendation offered several options, the recommended option is the decision. TRL 4 remains on hold by Amish's instruction, so nothing here is built, bought or tested.

## Decision

Table 1. Items decided by Amish, 2026-09-25: go with recommendation

| # | Item | Decision | What changed in the repo |
| --- | --- | --- | --- |
| 1 | Load type | Capacitive load | Status wording only; already in PVT-PRC-001 |
| 2 | Rating | 100 V, 20 A, below the 120 V DC extra-low-voltage limit | Status wording only; R1, R2 unchanged |
| 3 | Load capacitance | 6.6 mF, three 2200 µF 160 V capacitors | Status wording only; already in `bom/bom.csv` line 5 and the model |
| 4 | Isolation | Option B: digital isolator and isolated DC-DC converter | Status wording only; already in `bom/bom.csv` line 14 and the model |
| 5 | Display | 2.8 in TFT plus phone export | Status wording only |
| 6 | Irradiance reference | Reference cell calibrated once against a pyranometer | Status wording only; the calibration itself is TRL 4 work, on hold |
| 7 | Controller | ESP32 display board | Status wording only |
| 8 | Grade thresholds | A 90 % or more of nameplate, B 80 to 90 %, C 70 to 80 %, reject below 70 % or with a visible safety defect, in a partner-editable table | R10 wording in PVT-REQ-001 v0.4 and PVT-CAL-001 v0.2 |
| 9 | Budget | Raise `budget_usd` from $150 to $165 | `project.yaml` budget_usd 150 to 165; README budget line; R17 in PVT-REQ-001 v0.4 changes from not met ($163 against $150) to met ($164 against $165, $1 margin); PVT-PRB-001 v0.4 constraint |
| TRL 2 note item 11 | `pitch` and `problem` | No change, as recommended | None |
| 12 | Heat and sun (R13) | Light grey case, charger with temperature cut-off and a display sun hood | New BOM line 15, printed PETG sun hood, 86 x 64 x 18 mm, $1.00; hood added to `cad/src/model.py` (no clashes; top at Z 98, level with the isolator knob, so the R12 envelope is unchanged); STEP and STL re-exported; PVT-DWG-001 Rev P1 to P2; concept media refreshed with callout 15; PVT-CAL-001 v0.2: parts $163 to $164, mass 1.41 kg to 1.43 kg. R13 display readability stays not met on paper until a field check (TRL 4, on hold) |
| 13 | Case size | 220 x 130 x 80 mm | Status wording only; already in the model and drawing |

### Items left open by this record

Table 2. Items left open by this record, both decided on 2026-10-02

| # | Item | Decision |
| --- | --- | --- |
| 10 | First co-design partner: a second-life panel refurbisher or recycler, or a TVET solar course | **Decided by Amish, 2026-10-02:** first candidate type to approach (not yet agreed), a second-life panel refurbisher or recycler that tests used modules in volume, with a TVET solar course as a good second partner for the teaching use (PVT-DEC-001, item 5) |
| 11 | R3 at worst-case capacitor tolerance (16.4 ms at -20 %): a fourth capacitor, selected capacitors of 6.4 mF or more, or relaxing the 20 ms bound | **Decided by Amish, 2026-10-02:** each capacitor is measured at build and a set is selected that gives at least 6.4 mF; the 20 ms bound is relaxed later only if TOPCon and HJT capacitance data justify it (PVT-DEC-001, item 4) |

### Cross-repo actions

None. CalRig's 10 to 40 °C range limit for the temperature probe (PVT-CAL-001 section 4) was a note, not a recommendation to change CalRig.

### On hold (TRL 4)

Reference cell calibration, the display readability field check, any purchase, build or bench test. These follow from the decisions above but are TRL 4 work and stay on hold by Amish's instruction.

## Consequences

- The budget is $165 and the priced BOM is $164, so R17 is met with a $1 margin. Any later addition, such as a fourth capacitor for item 11 (about +$6), would break it again.
- Requirements now stand at ten met, three not met (R3 at tolerance, R13 display readability, R16 out of scope), two at risk (R7, R8) and two not verifiable at TRL 3 (R6, R9).
- The sun hood adds about 15 g; mass is 1.43 kg against 1.5 kg (R12).
- `trl` and `trl_target` stay at 3.
