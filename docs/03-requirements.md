---
doc_id: PVT-REQ-001
title: PVTrace requirements
project: PVTrace
doc_type: Requirements
version: "0.4"
status: Draft
date: '2026-09-25'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Initial scaffold
- version: "0.2"
  date: '2026-09-25'
  author: Amish Chadha
  change: First measurable requirements with concept status for TRL 2
- version: "0.3"
  date: '2026-09-25'
  author: Amish Chadha
  change: Status from PVT-CAL-001; decisions from PVT-DDR-001 (6.6 mF, isolation, grade thresholds); R10 and R17 wording; 33 J stored energy
- version: "0.4"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
---

# PVTrace requirements

These requirements are proposals for review, not yet agreed with users, and will be revised after co-design (see PVT-PRB-001). The status column gives the design's position against each target from the calculations in PVT-CAL-001 (TRL 3). Three requirements are **not met** on paper (R3 at worst-case capacitor tolerance, R13 display readability, R16 out of scope), two are at risk (R7, R8) and two cannot be verified until hardware exists (R6, R9). R17 is met since Amish set the budget at $165 on 2026-09-25. The design choices were decided by Amish on 2026-09-25 (go with recommendation; PVT-DDR-001 and PVT-DDR-002).

The **reference module** is a 144 half-cell module of about 450 W: open-circuit voltage (Voc) about 49.5 V, short-circuit current (Isc) about 11.6 A. The **high-current case** is a 108 half-cell 182 mm module of about 410 W (Voc about 37.5 V, Isc about 13.9 A). The **high-voltage case** is two older 60-cell 250 W modules in series (Voc about 75 V, Isc about 8.9 A).

Table 1. Requirements

| ID | Requirement | Target | Verification (TRL 3 or later) | Status (PVT-CAL-001) |
| --- | --- | --- | --- | --- |
| R1 | Voltage range | 0 to 100 V DC open circuit, including cold-weather Voc rise; hard limit below 120 V | Component ratings; calculation | Met by design review: high-voltage case 83 V at -10 °C; 160 V capacitors, 150 V MOSFETs. Two 450 W modules in series (109 V cold) are refused |
| R2 | Current range | 0 to 20 A short circuit | Shunt and switch ratings | Met by design review: 20.48 A full scale; shunt 1.6 W of 3 W |
| R3 | Sweep duration, to limit capacitive error in high-efficiency cells | 20 to 200 ms from Isc to Voc for any module in range | Sweep model; later bench sweep | **Not met** at worst-case tolerance: high-current case 20.5 ms at 6.6 mF nominal, 16.4 ms at -20 %; longest 81 ms |
| R4 | Curve resolution | 200 or more V-I pairs per sweep | Sample-rate calculation | Met: 410 pairs or more |
| R5 | Measurement accuracy after calibration | Voltage and current within ±1 % of reading ±0.1 % of full scale | Error budget; later check against a calibrated meter | Met on paper: about ±0.2 % of reading ±0.03 % of full scale after calibration |
| R6 | Repeatability | Pmax within ±1 % over 3 consecutive sweeps at stable irradiance (±1 % change) | Later field test | Not verifiable at TRL 3; instrument noise about 0.08 % per sample |
| R7 | Irradiance and temperature | Plane-of-array irradiance within ±5 % from a reference cell; module back temperature within ±2 °C | Calibration plan; CalRig for the temperature probe | At risk: needs a reference cell calibrated within ±4.6 % |
| R8 | STC translation | Pmax translated to STC per IEC 60891 with an expanded uncertainty of ±5 % or better at 700 W/m² or more | Uncertainty budget | At risk: ±3.7 to ±5.4 %; met if the reference cell is within ±4.5 % |
| R9 | Fault flags | Flag steps from bypass diode conduction (loss of one substring or more), raised series resistance, lowered shunt resistance and an Isc deficit against irradiance; shown within 5 s of the sweep | Rule definitions; later tests on modules with known faults | Not verifiable at TRL 3; about 7 or more samples per volt resolve a substring step |
| R10 | Second-life grading | Grade A, B, C or reject from STC Pmax against nameplate, with thresholds held in an editable table that a partner can change | Rule review with partner | Met by design review; thresholds decided by Amish (PVT-DDR-001 item 8); a partner can still tune the table |
| R11 | Safe connection and disconnection | Reverse polarity and over-voltage detected before the load connects; the circuit is never opened above 0.5 A; load capacitors below 30 V within 2 s after each sweep and below 60 V within 60 s if the controller fails | Circuit review; discharge calculation | Met: 0.21 s to 30 V; 40 s passive to 60 V; load switch held up to 6 ms past 99 % of Voc so it opens below 0.5 A |
| R12 | Handheld | Mass 1.5 kg or less including leads and sensor pod; enclosure 250 x 150 x 100 mm or less | Mass estimate; model | Met: 1.43 kg with the sun hood; 234 x 144 x 80 mm over bumpers, 98 mm to the knob and hood tops |
| R13 | Field conditions | Operate at 0 to 45 °C ambient in full sun; IP54 when closed; display readable in direct sun | Datasheets; heat model; later field check | IP54 met by design; **display readability not met** on paper: sun hood fitted (PVT-DDR-002), readability to be shown in a field check (TRL 4); heat at risk (about 56 °C inside a light case at 45 °C in sun) |
| R14 | Battery life | 8 h of field use or 200 sweeps per charge; USB-C charging | Power budget | Met: 10.3 h |
| R15 | Open data | Every sweep saved as CSV (raw V-I pairs, irradiance, temperature, time, module ID, flags, grade); export by USB or Wi-Fi to a phone | Design review (no firmware at TRL 3) | Met by design review |
| R16 | Second-life safety screening | Detect insulation faults (cracked backsheet, wet leakage) before a module is resold | Not in this instrument | **Not met**: out of scope; an insulation tester is needed alongside PVTrace |
| R17 | Cost | Parts for one prototype within `budget_usd` ($165, raised from $150 by Amish on 2026-09-25) | Priced BOM (`bom/bom.csv`) | Met: $164 with $1 margin |

## Assumptions

- Module curves are modeled with a single-diode model fitted to datasheet Voc, Isc, Vmp and Imp; sweep times are the time for a 6.6 mF load (±20 %) to reach 99 % of Voc, with 56.6 mΩ loop resistance (PVT-CAL-001).
- The ADC delivers at least 25,000 V-I pairs per second in practice (half the rated rate of a 100 kS/s two-channel converter, to allow for SPI and firmware overhead).
- The reference cell is calibrated once against a pyranometer or a module of known power under clear sky; its uncertainty (about ±3 to 5 %) dominates R8.
- The 20 ms lower bound in R3 is a working figure for high-efficiency (PERC, TOPCon, HJT) cells, whose capacitance distorts fast sweeps; it could not be checked against literature at TRL 3 and stays a working figure. PVT-CAL-001 shows the capacitive current error is about C_module / C_load, so it depends on the load capacitance more than on the sweep time.
- 700 W/m² follows IEC 61829 guidance for converting to STC ([Seaward](https://www.seaward.com/gb/support/solar/faqs/29495-curve-tracing-faq-s/)).

> **Safety:** The tracer connects directly to energized PV modules at up to 100 V DC and 20 A, and stores up to 33 J in its load capacitors. R11 exists to keep the user safe; it must not be relaxed to meet cost.
