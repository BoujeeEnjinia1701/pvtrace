---
doc_id: PVT-DEC-001
title: PVTrace design decisions register
project: PVTrace
doc_type: Design decisions register
version: "0.1"
status: Draft
date: '2026-10-01'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
  - version: "0.1"
    date: '2026-10-01'
    author: Amish Chadha
    change: Register opened with the open decisions from the review note, the decision records and the build plan work; budget treated as a value-engineering target
---

# PVTrace design decisions register

Every design decision still to be made, and every decision made, in one place. Each decision is argued in full in its decision record under `docs/decisions/`; this register is the index Amish works from. The build plan (`docs/05-build-plan.md`) describes the design as it stands and does not list open decisions.

## Open decisions

| # | Decision needed | Options | Recommendation | Affects in the build | Source |
| --- | --- | --- | --- | --- | --- |
| 1 | Design for construction (PVT-DDR-003 C1 to C11): chassis plate, fixings, window, hood tabs, display mounting, USB-C socket, sensor pod clip and the moves that clear the case pillars and gland nuts | Accept as made; or change any item | Accept: each change keeps what the tracer does | The whole build plan follows it | PVT-DDR-003, Table 1 |
| 2 | Which side of the isolation barrier reads the sensor pod | (a) controller side through its own 16-bit ADC (+$3, as modelled); (b) PV side through a second ADC on the measurement board | (a): the pod is handled and clipped to a frame that may be earthed | Pod wiring (build plan section 3.4.1, wire 10); BOM line 3 | PVT-DDR-003, A1 |
| 3 | R12 mass margin of about 14 g on estimated masses (1.49 kg against 1.5 kg) | (a) accept and weigh the prototype at TRL 4; (b) find mass now | (a) | None now; first check "Mass and size" | PVT-DDR-003, A2 |
| 4 | R3 sweep time at worst-case capacitor tolerance (16.4 ms against 20 ms for the high-current module) | (a) a fourth capacitor (8.8 mF, about +$6; the case layout would need checking); (b) select or measure capacitors so the bank is at least 6.4 mF; (c) relax the 20 ms bound once the capacitance of TOPCon and HJT cells is known | None yet | Capacitor bank and plate layout if (a) | PVT-DDR-001 item 11; PVT-DDR-002 Table 2 |
| 5 | First co-design partner | A second-life panel refurbisher or recycler, or a TVET solar course | None stated | None in the build | PVT-DDR-001 item 10; PVT-DDR-002 Table 2 |
| 6 | Appearance model differences from the engineering model: radiused case corners, wrap-around corner boots, keypad and status LEDs, side grips, USB-C flap, labels, lead routing, pod fillets | Accept each as the look to aim for; or bring the renders back to the engineering model | Accept the case shape items; drop the keypad and LEDs unless a BOM line is added, since the display board is a touch screen | Renders only; a keypad would add a BOM line and lid holes | `docs/REVIEW.md`, 2026-09-26 session, items 1 to 4 |

## To confirm when parts are bought

| # | What to confirm | Why it matters | Source |
| --- | --- | --- | --- |
| 1 | The case model: outside size, flat floor, corner pillar positions and size, lid depth of at least 25 mm inside | Sets the plate size and notches, the floor holes and the room for the display and isolator | PVT-DDR-003 C5, C6 |
| 2 | The display board's size (86 x 50 mm), hole centres (79 x 43 mm) and screen height above the board | Sets the four lid holes and the 7 mm spacer length | PVT-DDR-003 C4 |
| 3 | The DC isolator's panel cut-out, flange and screw pattern, and depth below the lid (47 mm or less) | Sets the lid holes and the 2.5 mm clearance above the measurement board | PVT-DDR-003 C8, C9 |
| 4 | The discharge resistor's free-air (unmounted) rating is at least 7 W; if not, mount it on a small aluminium heat spreader | The resistor now sits on a plastic plate; average dump power is 6.6 W at 100 V and one sweep every 5 s | PVT-DDR-003 Table 2; PVT-CAL-001 section 5 |
| 5 | The fuse holder's base is 44 x 20 mm or less and its DC rating covers 100 V | It sits between the discharge resistor, a corner pillar and the gland nuts with 0.5 to 2 mm to spare | PVT-DDR-003 C1, C6 |
| 6 | The isolation barrier parts' working voltage and test rating | The barrier must withstand module voltage with margin; checked by the 500 V insulation test | `docs/REVIEW.md`, TRL 3 safety concerns |
| 7 | The USB-C socket has an M16 thread, IP65 or better with a tethered cap | Sets the left end hole and keeps IP54 | PVT-DDR-003 C10 |
| 8 | The modules to be tested have frames 30 to 40 mm deep with a bottom flange | The pod clip grips the frame between its top jaw and thumb screw | PVT-DDR-003 C11 |

## Value engineering

Value-engineering target: USD 165 (a hypothetical control target, not a limit). Estimated cost of the constructable design: USD 178 (USD 13 over the target). Main cost drivers and savings worth trying:

- The largest lines are the display board with its ADC module (USD 21), the three load capacitors (USD 18), the DC isolator (USD 16), the measurement board parts (USD 16), the test leads (USD 16) and the sensor pod (USD 16).
- Making the design constructable added USD 14: the chassis plate (USD 3), the USB-C socket (USD 5), the pod ADC module (USD 3), the pod clip and gland (USD 1) and fixings (USD 2).
- Savings worth trying: a fused two-pole DC isolator in one body in place of the separate fuse holder and isolator (about USD 5 to 8, if one fits the lid); test leads made from one 2 m pair of PV cable with crimped MC4 connectors (about USD 4); buying the ESP32 board and ADC module as one bundle (about USD 2).

## Decisions made

| Date | Decision | Decided by | Record |
| --- | --- | --- | --- |
| 2026-09-25 | TRL 2 review items 1 to 8: capacitive load; 100 V, 20 A rating; 6.6 mF; isolation option B; 2.8 in TFT plus phone export; once-calibrated reference cell; ESP32 controller; grade thresholds A 90 %, B 80 %, C 70 % | Amish: "i accept all your recommendations, go with them across all repos." | PVT-DDR-001, PVT-DDR-002 |
| 2026-09-25 | `budget_usd` set to 165 (item 9); display sun hood and light grey case (item 12); 220 x 130 x 80 mm case (item 13); pitch and problem unchanged | Amish, same instruction | PVT-DDR-002 |
| 2026-09-26 | PVTrace chosen for the first batch of product renders | Amish | `docs/REVIEW.md`, 2026-09-26 session |
| 2026-10-01 | `budget_usd` is a value-engineering target, not a limit | Amish: "the budgets are a hypothethical control target to ensure we are thinking along a value engineering lens. its ok to ensure wording reflects that the hypothesis budget was x - the real cost being accrued is y" | `.kit/STANDARDS.md` section 18; this register |
| 2026-10-01 | Design changed so it can be built (PVT-DDR-003 C1 to C11), under Amish's 2026-09-30 instruction: "If you are realising that the design cannot be built as per concept - fix the design assumptions to match and be physically feasible as you draw the illustrations." Open for his review (open decision 1) | Made under Amish's instruction | PVT-DDR-003 |
