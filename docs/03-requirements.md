---
doc_id: PVT-REQ-001
title: PVTrace requirements
project: PVTrace
doc_type: Requirements
version: "0.2"
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
---

# PVTrace requirements

These are first-pass requirements for the concept. Targets are proposals for review, not yet agreed with users, and will be checked by calculation at TRL 3 and revised after co-design (see PVT-PRB-001). The status column gives the concept's position against each target from the estimates in PVT-PRC-001. Three requirements are **not met** on current estimates (R3, R13 in part, R16) and several are unverified.

The **reference module** is a 144 half-cell module of about 450 W: open-circuit voltage (Voc) about 49.5 V, short-circuit current (Isc) about 11.6 A. The **high-current case** is a 108 half-cell 182 mm module of about 410 W (Voc about 37.5 V, Isc about 13.9 A). The **high-voltage case** is two older 60-cell 250 W modules in series (Voc about 75 V, Isc about 8.9 A).

Table 1. Requirements

| ID | Requirement | Target | Verification (TRL 3 or later) | Concept status |
| --- | --- | --- | --- | --- |
| R1 | Voltage range | 0 to 100 V DC open circuit, including cold-weather Voc rise; hard limit below 120 V | Component ratings; calculation | Met by design (160 V capacitors, 150 V MOSFETs) |
| R2 | Current range | 0 to 20 A short circuit | Shunt and switch ratings | Met by design |
| R3 | Sweep duration, to limit capacitive error in high-efficiency cells | 20 to 200 ms from Isc to Voc for any module in range | Sweep model; later bench sweep | **Not met**: about 13 ms for the high-current case; 21 ms reference; 43 ms high-voltage case (estimates) |
| R4 | Curve resolution | 200 or more V-I pairs per sweep | Sample-rate calculation | Met (estimate): about 325 to 1,070 pairs |
| R5 | Measurement accuracy after calibration | Voltage and current within ±1 % of reading ±0.1 % of full scale | Error budget; later check against a calibrated meter | Unverified |
| R6 | Repeatability | Pmax within ±1 % over 3 consecutive sweeps at stable irradiance (±1 % change) | Later field test | Unverified |
| R7 | Irradiance and temperature | Plane-of-array irradiance within ±5 % from a reference cell; module back temperature within ±2 °C | Calibration plan; CalRig for the temperature probe | Unverified; depends on reference-cell calibration |
| R8 | STC translation | Pmax translated to STC per IEC 60891 with an expanded uncertainty of ±5 % or better at 700 W/m² or more | Uncertainty budget | **At risk**: estimate about ±5 to 6 % with a once-calibrated reference cell |
| R9 | Fault flags | Flag steps from bypass diode conduction (loss of one substring or more), raised series resistance, lowered shunt resistance and an Isc deficit against irradiance; shown within 5 s of the sweep | Rule definitions; later tests on modules with known faults | Unverified; rules drafted in PVT-PRC-001 |
| R10 | Second-life grading | Grade A, B, C or reject from STC Pmax against nameplate, with thresholds that a partner can edit | Rule review with partner | Proposed thresholds awaiting Amish |
| R11 | Safe connection and disconnection | Reverse polarity and over-voltage detected before the load connects; the circuit is never opened above 0.5 A; load capacitors below 30 V within 2 s after each sweep and below 60 V within 60 s if the controller fails | Circuit review; discharge calculation | Met by design (estimates: about 0.1 s active to below 30 V; about 23 s passive to below 60 V) |
| R12 | Handheld | Mass 1.5 kg or less including leads and sensor pod; enclosure 250 x 150 x 100 mm or less | Mass estimate; model | Met (estimate): about 1.35 kg, 200 x 120 x 75 mm |
| R13 | Field conditions | Operate at 0 to 45 °C ambient in full sun; IP54 when closed; display readable in direct sun | Datasheets; later field check | IP54 and temperature met by design; **sunlight readability not met** with a commodity TFT (unverified) |
| R14 | Battery life | 8 h of field use or 200 sweeps per charge; USB-C charging | Power budget | Met (estimate): about 16 h |
| R15 | Open data | Every sweep saved as CSV (raw V-I pairs, irradiance, temperature, time, module ID, flags, grade); export by USB or Wi-Fi to a phone | Firmware sketch review at TRL 3 | Met by design |
| R16 | Second-life safety screening | Detect insulation faults (cracked backsheet, wet leakage) before a module is resold | Not in this instrument | **Not met**: out of scope; an insulation tester is needed alongside PVTrace |
| R17 | Cost | $150 or less in parts for one prototype | Priced BOM (`bom/bom.csv`) | Met with about $1 margin (about $149); galvanic isolation option would exceed it |

## Assumptions

- Module curves are modeled with a single-diode model fitted to datasheet Voc, Isc, Vmp and Imp; sweep times are the time to reach 99 % of Voc with a 4.4 mF load.
- The ADC delivers at least 25,000 V-I pairs per second in practice (half the rated rate of a 100 kS/s two-channel converter, to allow for SPI and firmware overhead).
- The reference cell is calibrated once against a pyranometer or a module of known power under clear sky; its uncertainty (about ±3 to 5 %) dominates R8.
- The 20 ms lower bound in R3 is a working figure for high-efficiency (PERC, TOPCon, HJT) cells, whose capacitance distorts fast sweeps; the bound will be checked against literature at TRL 3.
- 700 W/m² follows IEC 61829 guidance for converting to STC ([Seaward](https://www.seaward.com/gb/support/solar/faqs/29495-curve-tracing-faq-s/)).

> **Safety:** The tracer connects directly to energized PV modules at up to 100 V DC and 20 A, and stores up to 22 J in its load capacitors. R11 exists to keep the user safe; it must not be relaxed to meet cost.
