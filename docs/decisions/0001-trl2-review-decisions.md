---
doc_id: PVT-DDR-001
title: PVTrace TRL 2 review decisions
project: PVTrace
doc_type: Design decision record
version: "0.1"
status: Draft
date: '2026-09-25'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Record the TRL 2 review recommendations adopted for TRL 3 work under Amish's 2026-09-25 instruction, and the items that remain open
---

# 0001: TRL 2 review decisions

- **Date:** 2026-09-25
- **Status:** proposed. The recommendations in items 1 to 8 are adopted for TRL 3 work pending Amish's review; items 9 to 13 remain proposed, awaiting Amish.

## Context

The TRL 2 review note (`docs/REVIEW.md`, session of 2026-09-25, /populate) listed eleven items as "Proposed, awaiting Amish", most with a recommendation. On 2026-09-25 Amish asked for this batch of repos to be taken through the usual process with the instruction "you know the drill, nothing gets past TRL 3". He has not reviewed the PVTrace items one by one. Under that instruction, every item with a recommendation is adopted as recommended for TRL 3 work and stays open for his review. Items with no recommendation, and the budget figure, stay open. TRL 4 is on hold by Amish's instruction.

## Options considered

The options for each item are in `docs/REVIEW.md` (2026-09-25, /populate) and PVT-PRC-001 v0.2. They are not repeated here.

## Decision

Table 1. Items adopted for TRL 3 work

| # | Item | Status | Where it now lives |
| --- | --- | --- | --- |
| 1 | Load type: capacitive load | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review | PVT-PRC-001 v0.3 |
| 2 | Rating: 100 V, 20 A, single modules and two in series, below the 120 V DC extra-low-voltage limit | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review | PVT-PRC-001 v0.3, PVT-REQ-001 R1, R2 |
| 3 | Load capacitance: 6.6 mF with three 2200 µF 160 V capacitors | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review | `bom/bom.csv` line 5, `cad/src/model.py`, PVT-CAL-001 |
| 4 | Isolation: option B, a digital isolator and isolated DC-DC converter between the measurement side and the controller | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review | `bom/bom.csv` line 14, `cad/src/model.py`, PVT-PRC-001 v0.3 |
| 5 | Display: 2.8 in TFT plus phone export | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review | PVT-PRC-001 v0.3; R13 readability stays not met |
| 6 | Irradiance reference: small reference cell calibrated once against a pyranometer | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review | PVT-PRC-001 v0.3, PVT-CAL-001 section 4 |
| 7 | Controller: ESP32 display board | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review | `bom/bom.csv` line 3 |
| 8 | Grade thresholds: A 90 % or more of nameplate, B 80 to 90 %, C 70 to 80 %, reject below 70 % or with a visible safety defect; editable by a partner | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review; still to be agreed with a partner | PVT-PRC-001 v0.3, PVT-REQ-001 R10 |

The TRL 2 review recommended no change to `pitch` or `problem` in `project.yaml`, so neither changes.

### Items that remain open

Table 2. Open items

| # | Item | Status |
| --- | --- | --- |
| 9 | Budget: the TRL 2 review recommends raising `budget_usd` from $150 to $165 to cover items 3 and 4. The priced BOM is $163 | Proposed, awaiting Amish. `budget_usd` stays 150 in `project.yaml`; R17 is not met at $150 and met at $165 |
| 10 | First co-design partner: a second-life panel refurbisher or recycler, or a TVET solar course | Proposed, awaiting Amish. No preference stated |
| 11 | R3 at worst-case tolerance (16.4 ms at -20 % capacitance, PVT-CAL-001). Options: a fourth capacitor (8.8 mF, about +$6, case layout to be checked); select or measure capacitors so the bank is at least 6.4 mF; or relax the lower bound once the module capacitance of TOPCon and HJT cells is known | Proposed, awaiting Amish. No recommendation yet; new at TRL 3 |
| 12 | Heat in sun (R13): light grey case, charger with temperature cut-off and a display sun hood. The first two are in the TRL 3 BOM at no added cost; the hood is not | Proposed, awaiting Amish. Engineering proposal from PVT-CAL-001 |
| 13 | Case size grows to 220 x 130 x 80 mm to fit the third capacitor and the isolation board | Proposed, awaiting Amish. Follows from items 3 and 4; still inside R12 |

## Consequences

- The design now carries 6.6 mF and an isolation barrier; parts total $163, $13 over the $150 budget. R17 is not met until Amish decides item 9.
- The stored energy at 100 V rises to 33 J, and every safety note now uses that figure.
- R3 is met at nominal capacitance but not at -20 % tolerance, so it stays not met until item 11 is decided.
- Battery life falls to about 10 h with the isolated side powered, still above R14.
- The controller ground is no longer the PV negative, so a laptop on USB is not exposed to PV potential in normal use; the barrier's rating is a TRL 4 check.
