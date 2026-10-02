---
doc_id: PVT-DDR-003
title: PVTrace design for construction
project: PVTrace
doc_type: Design decision record
version: "0.2"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-10-01'
  author: Amish Chadha
  change: Changes that make the concept physically buildable, with the reason for each; made under Amish's 2026-09-30 instruction to make the design physically buildable; open for his review
- version: "0.2"
  date: '2026-10-02'
  author: Amish Chadha
  change: Accepted by Amish on 2026-10-02, including the recommendations for A1 and A2
---

# 0003: Design for construction

- **Date:** 2026-10-01
- **Status:** accepted. Amish, 2026-10-02: "i approve your recommendations for all 555 open decisions." This covers every change in Tables 1 and 2, as made, and the recommendations for A1 and A2 in Table 3, which are now decided as recommended and recorded in the design decisions register (PVT-DEC-001).

## Context

On 2026-09-30 Amish asked for every repo to have an illustrated build plan and wrote: "If you are realising that the design cannot be built as per concept - fix the design assumptions to match and be physically feasible as you draw the illustrations." The TRL 3 model of PVT-DDR-001 and PVT-DDR-002 showed what PVTrace does, but it was a massing model: every internal part stood on the case floor with no fixing, the display board and window floated under and in the lid, the sun hood had nothing to screw into, and the cable glands sat outside the end walls with no holes or nuts. Checking the model with build123d, with the bought case's corner pillars and the glands' inside locknuts added, found the clashes listed below.

The changes keep what the instrument does: the same case, rating, load, isolation barrier, display, sun hood, sensor pod, leads and controls, in the same places. Nothing here changes the pitch. Every change is in `cad/src/model.py`, which now runs 183 constructability checks (`python cad/src/model.py --check`): no two parts overlap; every part touches what holds it; parts that must not touch keep their stated clearance; a screwdriver reaches every plate and hood screw from above; the lid lifts straight off with everything it carries; and the envelope stays inside R12. All 183 pass.

## Decision

*Table 1. Changes made to the model, the BOM and the calculations.*

| # | Problem in the concept | Change made | Why this way |
| --- | --- | --- | --- |
| C1 | The cable glands were drawn outside the end walls with no holes through the walls and no inside locknuts. With real M16 locknuts (about 22 mm across corners) the front lead gland's nut would have overlapped the fuse holder by 1 mm. | 16.2 mm holes for the two lead glands and 12.2 mm for the sensor gland, each with its locknut inside. The lead glands move from 20 to 18 mm each side of the centre line; the sensor gland moves from 35 to 45 mm toward the back. | Gives the 2 mm clearance from nut to fuse holder that a spanner needs, and leaves room on the left end for the USB-C socket (C10). |
| C2 | The window was the same size as the lid opening and sat in it with nothing to bond to. | A 72 x 54 x 3 mm polycarbonate window bonded on top of the lid with closed-cell adhesive gasket tape, over a smaller 62 x 46 mm opening. | A 4 to 5 mm bond land all round seals the opening (IP54) without machining a recess in a 3 mm lid. The opening still shows the whole 2.8 in display. |
| C3 | The sun hood had no fixing. The BOM named four M3 screws, but the hood's 2 mm walls cannot take a screw. | Four tabs, 7.5 x 10 x 3 mm, inside the side walls at the lid surface, each with a 3.4 mm hole. The hood is 4 mm wider inside (88 mm, 92 mm outside) so the screws clear the window, and the roof lip has two 7 mm holes so a screwdriver reaches the back screws. | The hood keeps its height (top at 98 mm, level with the isolator knob), its open front and its 20 mm roof lip. |
| C4 | The display board floated under the lid with no fixing, and its envelope (90 x 62 mm) did not match the ESP32-2432S028 class board (86 x 50 mm). | The board is modelled at its real size and hangs under the lid on four 7 mm spacers. The hood's four M3 x 20 screws pass through the hood tabs, the lid and the spacers and are nutted under the board. | One set of four screws holds the hood and the board, so the lid needs only four small holes near the window, sealed by washers under the screw heads. The display glass sits 1 mm below the lid. |
| C5 | Every internal part stood on the case floor with no fixing, and the boards had no standoffs. | A 1.5 mm polycarbonate chassis plate, 212 x 122 mm, on five 5 mm nylon standoffs held by countersunk M3 screws through the floor. Every internal part is screwed to the plate; the measurement and isolation boards stand on 6 mm nylon standoffs. New BOM line 16. | Only five holes in the IP54 floor; the plate is an insulator, so it adds no conductive path between the PV side and the controller side; and the whole electronics fit-out is built on the bench and lowered in as one unit. |
| C6 | A bought IP54 case of this size has its lid screws in four moulded corner pillars, which the concept did not show. The first capacitor overlapped the front left pillar. | Corner pillars added to the model. The capacitor bank moves 2 mm toward the left end and 6 mm toward the back; the plate has 10 x 10 mm corner notches; the fuse holder is specified at 44 mm long (was 46) and moves 2.5 mm toward the front. | Clears every pillar by at least 1 mm without changing the bank's place in the case. |
| C7 | The three capacitors (75 g each) lay on the floor with no hold-down. | A bed of neutral-cure silicone under each capacitor and two cable ties round the whole bank, passing down through 2.5 x 6 mm slots in the plate at both ends of the bank. Pins face the front, toward the discharge resistor. | Holds the bank without a printed cradle, which had no room beside the MOSFET bar; keeps the capacitor pins on the PV side, away from the USB-C socket. |
| C8 | The MOSFET bar, the DC isolator and the other parts had no fixings. | The MOSFET bar (25 x 10 mm aluminium flat bar, 40 mm long) is tapped M3 on its bottom and back faces; the MOSFETs sit on insulating pads with insulating bushings. The isolator is modelled with its maker's mounting flange under the lid and two screws from above. Resistor, fuse holder and cell holder each take two M3 screws through the plate. | Every fixing is one a maker can fit with hand tools; the MOSFET tabs, live at PV voltage, stay insulated from the bar. |
| C9 | Raised onto standoffs, the measurement board would have met the lead glands' locknuts and passed under the isolator body with no clearance check. | The board is turned 90 degrees (44 x 56 mm) and centred 76 mm right of centre, 2 mm toward the back. | Clears the locknuts by 1 mm, the MOSFET bar by 4 mm and the isolator body by 2.5 mm. |
| C10 | R14 calls for USB-C charging, but no port passed through the case, so the case would have to be opened to charge. | A panel-mount IP65 USB-C socket with a tethered cap and an M16 locknut in the left end, 87 mm from the front face and 34 mm up, wired to the charger on the controller side. New BOM line 17. | Charging with the case closed keeps the IP54 seal and the isolator open, as the safety notes require. The socket is on the controller side of the barrier, as the isolation design intends. |
| C11 | The sensor pod's frame clip was a solid block with no way to grip a module frame, and the pod had no cable entry. | A printed C-clip with a 42 mm opening and an M6 thumb screw in its lower jaw, for frames 30 to 40 mm deep, screwed to the housing by two M4 screws into heat-set inserts. An M12 cable gland on the housing's left end, a grommet for the probe lead. The reference cell is read by a 16-bit I2C ADC module on the controller side (BOM line 3). | The top jaw sits on the frame's top edge, so the cell lies about 4 mm above the glass and parallel to it. The concept did not say how the cell is read; see A1. |

*Table 2. Knock-on changes.*

| Item | Change | Reason |
| --- | --- | --- |
| Cost | BOM lines 1 to 4, 12, 13 and 15 respecified; lines 3, 12 and 13 repriced (+$6); new lines 16 (+$3) and 17 (+$5). Estimated cost USD 178, against the unchanged value-engineering target of USD 165 (`budget_usd`): USD 13 over the target. | Parts added for construction. |
| Mass | 1.49 kg (was 1.43 kg): chassis plate 45 g, USB-C socket 8 g, window corrected to 16 g, hood 17 g. R12 (1.5 kg) is still met, with about 14 g to spare [PVT-CAL-001 section 7]. | The plate is 1.5 mm, not 2 mm, to keep R12. |
| Drawing | PVT-DWG-001 Rev P3; making sketches PVT-DWG-101 to 108 added; concept blueprint PVT-DWG-010 Rev P4. | Follows the model. |
| Documents | PVT-CAL-001 v0.3 (mass, cost), PVT-REQ-001 v0.5 (R12, R17), PVT-PRC-001 v0.5 (components, key numbers). No requirement changed status except R17, now reported against the value-engineering target. | Follows the model. |
| Electrical and thermal | Unchanged: the sweep, discharge and heat calculations do not depend on how the parts are fixed. The discharge resistor now sits on a plastic plate rather than the floor; its free-air rating is to be confirmed when bought (design decisions register). | |

*Table 3. Items proposed, then accepted by Amish as recommended on 2026-10-02.*

| # | Question | Options | Recommendation |
| --- | --- | --- | --- |
| A1 | Which side of the isolation barrier reads the sensor pod. The pod is handled and clipped to a module frame that may be earthed. | (a) controller side, through its own 16-bit ADC module (+$3, as modelled); (b) PV side, through a second ADC on the measurement board, which would put the pod at PV potential. | (a): the pod stays at the safe, low-voltage side, as the USB port does. **Accepted 2026-10-02.** |
| A2 | The R12 mass margin is about 14 g on estimated masses. | (a) accept and weigh the prototype at TRL 4; (b) find mass now (for example a thinner pod housing or shorter leads). | (a). **Accepted 2026-10-02.** |

## Consequences

- `design_state: constructable` in `project.yaml`. The build plan PVT-BLD-001 shows every component and step in pictures generated from the model (`cad/src/build_plan_media.py`); open items are in the design decisions register PVT-DEC-001.
- With A1 and A2 accepted, the sensor pod is read on the controller side through its own 16-bit ADC, and the prototype is weighed at TRL 4 against R12.
- Requirement status: three not met (R3 at worst-case tolerance, R13 display readability, R16 out of scope), two at risk (R7, R8), two not verifiable at TRL 3 (R6, R9), nine met, and R17 reported as USD 13 over the value-engineering target.
- The photoreal renders (`media/render-*.png`), `media/card.png` and `media/social-preview.png` and the appearance model `cad/src/product_model.py` show the concept internals and the narrower hood. They need updating on Amish's Mac, where Blender is.
- The case, display board, isolator, fuse holder and USB-C socket are chosen at TRL 4; their sizes and fixing patterns must be checked then and the drawings moved to suit.
