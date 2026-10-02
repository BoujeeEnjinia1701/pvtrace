---
doc_id: PVT-DDR-001
title: PVTrace TRL 2 review decisions
project: PVTrace
doc_type: Design decision record
version: "0.3"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Record the TRL 2 review recommendations adopted for TRL 3 work under Amish's 2026-09-25 instruction, and the items that remain open
- version: "0.2"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
- version: "0.3"
  date: '2026-10-02'
  author: Amish Chadha
  change: Items 10 and 11 decided by Amish on 2026-10-02 (PVT-DEC-001, items 5 and 4)
---

# 0001: TRL 2 review decisions

- **Date:** 2026-09-25
- **Status:** items 1 to 9, 12 and 13 decided by Amish on 2026-09-25 (go with recommendation; see PVT-DDR-002). Items 10 and 11, which had no recommendation here, were decided by Amish on 2026-10-02 as recommended in the design decisions register (PVT-DEC-001, items 5 and 4).

## Context

The TRL 2 review note (`docs/REVIEW.md`, session of 2026-09-25, /populate) listed eleven items as "Proposed, awaiting Amish", most with a recommendation. On 2026-09-25 Amish asked for this batch of repos to be taken through the usual process with the instruction "you know the drill, nothing gets past TRL 3". He has not reviewed the PVTrace items one by one. Under that instruction, every item with a recommendation is adopted as recommended for TRL 3 work and stays open for his review. Items with no recommendation, and the budget figure, stay open. TRL 4 is on hold by Amish's instruction. Later on 2026-09-25 Amish wrote "i accept all your recommendations, go with them across all repos"; the statuses below were updated in v0.2 and the changes are recorded in PVT-DDR-002.

## Options considered

The options for each item are in `docs/REVIEW.md` (2026-09-25, /populate) and PVT-PRC-001 v0.2. They are not repeated here.

## Decision

Table 1. Items adopted for TRL 3 work

| # | Item | Status | Where it now lives |
| --- | --- | --- | --- |
| 1 | Load type: capacitive load | Decided by Amish, 2026-09-25: go with recommendation | PVT-PRC-001 v0.3 |
| 2 | Rating: 100 V, 20 A, single modules and two in series, below the 120 V DC extra-low-voltage limit | Decided by Amish, 2026-09-25: go with recommendation | PVT-PRC-001 v0.3, PVT-REQ-001 R1, R2 |
| 3 | Load capacitance: 6.6 mF with three 2200 µF 160 V capacitors | Decided by Amish, 2026-09-25: go with recommendation | `bom/bom.csv` line 5, `cad/src/model.py`, PVT-CAL-001 |
| 4 | Isolation: option B, a digital isolator and isolated DC-DC converter between the measurement side and the controller | Decided by Amish, 2026-09-25: go with recommendation | `bom/bom.csv` line 14, `cad/src/model.py`, PVT-PRC-001 v0.3 |
| 5 | Display: 2.8 in TFT plus phone export | Decided by Amish, 2026-09-25: go with recommendation | PVT-PRC-001 v0.3; R13 readability stays not met |
| 6 | Irradiance reference: small reference cell calibrated once against a pyranometer | Decided by Amish, 2026-09-25: go with recommendation | PVT-PRC-001 v0.3, PVT-CAL-001 section 4 |
| 7 | Controller: ESP32 display board | Decided by Amish, 2026-09-25: go with recommendation | `bom/bom.csv` line 3 |
| 8 | Grade thresholds: A 90 % or more of nameplate, B 80 to 90 %, C 70 to 80 %, reject below 70 % or with a visible safety defect; editable by a partner | Decided by Amish, 2026-09-25: go with recommendation; the partner may still tune the table | PVT-PRC-001 v0.3, PVT-REQ-001 R10 |

The TRL 2 review recommended no change to `pitch` or `problem` in `project.yaml`, so neither changes.

### Items that remain open

Table 2. Items open at v0.1 and their status now

| # | Item | Status |
| --- | --- | --- |
| 9 | Budget: the TRL 2 review recommends raising `budget_usd` from $150 to $165 to cover items 3 and 4. The priced BOM is $163 | Decided by Amish, 2026-09-25: go with recommendation. `budget_usd` is now 165 in `project.yaml`; R17 is met ($164 with the sun hood, PVT-DDR-002) |
| 10 | First co-design partner: a second-life panel refurbisher or recycler, or a TVET solar course | **Decided by Amish, 2026-10-02:** first candidate type to approach (not yet agreed), a second-life panel refurbisher or recycler that tests used modules in volume, with a TVET solar course as a good second partner for the teaching use (PVT-DEC-001, item 5) |
| 11 | R3 at worst-case tolerance (16.4 ms at -20 % capacitance, PVT-CAL-001). Options: a fourth capacitor (8.8 mF, about +$6, case layout to be checked); select or measure capacitors so the bank is at least 6.4 mF; or relax the lower bound once the module capacitance of TOPCon and HJT cells is known | **Decided by Amish, 2026-10-02:** each capacitor is measured at build and a set is selected that gives at least 6.4 mF; the 20 ms bound is relaxed later only if TOPCon and HJT capacitance data justify it (PVT-DEC-001, item 4) |
| 12 | Heat in sun (R13): light grey case, charger with temperature cut-off and a display sun hood. The first two are in the TRL 3 BOM at no added cost; the hood is not | Decided by Amish, 2026-09-25: go with recommendation. Printed sun hood added (`bom/bom.csv` line 15, `cad/src/model.py`, PVT-DWG-001 Rev P2) |
| 13 | Case size grows to 220 x 130 x 80 mm to fit the third capacitor and the isolation board | Decided by Amish, 2026-09-25: go with recommendation. Already in the model; still inside R12 |

## Consequences

- The design now carries 6.6 mF and an isolation barrier; parts totaled $163 at v0.1, $13 over the $150 budget. Amish raised the budget to $165 on 2026-09-25 (PVT-DDR-002); with the sun hood the parts total $164 and R17 is met.
- The stored energy at 100 V rises to 33 J, and every safety note now uses that figure.
- R3 is met at nominal capacitance but not at -20 % tolerance, so it stays not met until item 11 is decided.
- Battery life falls to about 10 h with the isolated side powered, still above R14.
- The controller ground is no longer the PV negative, so a laptop on USB is not exposed to PV potential in normal use; the barrier's rating is a TRL 4 check.
