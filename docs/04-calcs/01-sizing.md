---
doc_id: PVT-CAL-001
title: PVTrace sizing calculations
project: PVTrace
doc_type: Calculation note
version: "0.1"
status: Draft
date: '2026-09-25'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: First TRL 3 sizing note (sweep model, range, resolution, error budget, STC uncertainty, discharge, heat, battery, mass, cost) for the 6.6 mF isolated design in PVT-DDR-001
---

# PVTrace sizing calculations

On paper, PVTrace meets nine of its seventeen requirements (R1, R2, R4, R5, R10, R11, R12, R14, R15). Four are **not met**: R3 (sweep time) at worst-case capacitor tolerance, R13 (display readability in sun, with heat at risk), R16 (insulation screening, out of scope) and R17 (cost against the $150 budget in `project.yaml`). R7 and R8 are **at risk** because they rest on the reference cell calibration, and R6 and R9 cannot be verified until hardware exists.

Three TRL 2 figures change. With the third capacitor (6.6 mF, PVT-DDR-001 decision 3) the high-current module sweeps in 20.5 ms at nominal capacitance but only 16.4 ms at the -20 % tolerance of electrolytic capacitors, so R3 is still not met in the worst case. The stored energy at 100 V rises from 22 J to 33 J. Battery life falls from about 16 h to 10.3 h once the isolation barrier (decision 4) and a 5 V boost are counted; R14 is still met. The module current at 99 % of Voc is up to 2.5 A, so the load switch must stay closed a few milliseconds past the end of the sweep to open below 0.5 A (R11).

Every number here is printed by `docs/04-calcs/sizing.py` (run from the repo root: `python docs/04-calcs/sizing.py`), which also writes `docs/04-calcs/results.csv`. The script reads the case dimensions from `cad/src/model.py` and the costs from `bom/bom.csv`. All values are first-principles estimates for a paper design; nothing is measured.

## 1. Assumptions

Table 1. Inputs. All are assumptions for a paper design.

| Input | Value | Basis |
| --- | --- | --- |
| Module cases | 36-cell 100 W (22.0 V, 6.0 A); 108 half-cell 410 W (37.5 V, 13.9 A; MPP 31.4 V, 13.06 A); 144 half-cell 450 W reference (49.5 V, 11.6 A; MPP 41.5 V, 10.85 A); 2 x 60-cell 250 W in series (75.2 V, 8.9 A); rating limit, the reference curve scaled to 100 V and 20 A | Datasheet-class values, PVT-REQ-001 |
| Module model | Single-diode model, ideality 1.2 per cell, series and shunt resistance solved from Isc, Voc, MPP and zero dP/dV at MPP | Standard five-parameter fit |
| Load capacitance | 3 x 2200 µF 160 V = 6.6 mF, ±20 % | Decision 3, PVT-DDR-001; typical electrolytic tolerance |
| Loop resistance | 56.6 mΩ: leads 8.6, MC4 contacts 2.0, fuse 5.0, isolator 2.0, shunt 4.0, MOSFET 10.0, capacitor ESR 20.0, wiring 5.0 mΩ | Copper at 20 °C; typical part values |
| Sampling | 25,000 V-I pairs per second, voltage and current converted one after the other (20 µs apart) | Half the rate of a 100 kS/s two-channel ADC |
| Front end | 1 MΩ and 39 kΩ divider (0.1 %, 25 ppm/°C), 4 mΩ shunt (50 ppm/°C), gain 50, 4.096 V reference (50 ppm/°C), 12-bit ADC with ±1 LSB INL, 30 °C between calibration and use | Typical parts in `bom/bom.csv` line 4 |
| Voc temperature coefficient | -0.30 %/°C; coldest cell -10 °C | Typical crystalline silicon |
| STC terms | Pmax coefficient -0.35 %/°C; module temperature ±2 °C; spectral and angle mismatch ±2 %; reference cell ±3 to ±5 % | PVT-PRC-001; decision 6 |
| Discharge | 22 Ω active dump, 10 kΩ passive bleed; one sweep every 5 s at most | PVT-PRC-001 |
| Power | Controller and lit TFT 0.60 W; isolated side 0.25 W; 5 V boost 90 %; 3,000 mAh 18650 at 3.6 V, 90 % usable; 20 s of controller time per sweep | TRL 2 estimate plus isolation |
| Heat | 9 W/(m² K) from the case outside; 1,000 W/m² on the lid; solar absorptance 0.30 (light grey) or 0.90 (dark); 45 °C ambient | Still air, natural convection plus radiation |

## 2. Sweep (R3, R4)

Table 2 gives the sweep for each case. The sweep time is the time for the capacitor to rise from 0 V to 99 % of Voc, integrated as t = ∫ C dV / I(V) along the fitted curve, with the loop resistance and the bleed and divider currents included. It scales in proportion to the load capacitance.

Table 2. Sweep with 6.6 mF (single-diode model)

| Case | Sweep, nominal (ms) | Sweep, -20 % C (ms) | Sweep, 4.4 mF (ms) | V-I pairs, nominal | Energy stored (J) | First sample (V) | Samples per volt near Isc, -20 % C |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36-cell 100 W | 28.9 | 23.1 | 19.3 | 722 | 1.6 | 0.34 | 22.0 |
| 108 half-cell 410 W (high current) | 20.5 | 16.4 | 13.7 | 513 | 4.5 | 0.79 | 9.5 |
| 144 half-cell 450 W (reference) | 32.2 | 25.8 | 21.5 | 805 | 7.9 | 0.66 | 11.4 |
| 2 x 60-cell 250 W (high voltage) | 67.5 | 54.0 | 45.0 | 1,687 | 18.3 | 0.50 | 14.8 |
| Rating limit, 100 V, 20 A | 37.7 | 30.1 | 25.1 | 942 | 32.3 | 1.13 | 6.6 |

- **R3 is not met at worst-case tolerance.** The shortest sweep is 20.5 ms at nominal capacitance but 16.4 ms if the three capacitors are 20 % low. Holding 20 ms at -20 % needs 8.0 mF rated (6.4 mF actual), which is a fourth capacitor. The longest sweep, the high-voltage case with +20 % capacitance, is about 81 ms, well inside 200 ms. The 4.4 mF column reproduces the TRL 2 estimates (13, 21 and 43 ms) within 2 ms, which checks the TRL 2 scaling.
- **R4 is met.** The fewest pairs are 410 (high-current case, -20 % capacitance), against 200.
- **Isc.** Loop resistance holds the module at 0.34 to 1.13 V at the first sample, 1 to 2 % of Voc, so firmware extrapolates Isc from the first samples. Pre-charging the bank negative is not needed.
- **Module capacitance.** With a capacitive load dV/dt = I / C_load, so the module's own capacitance C_mod causes a current error of about C_mod / C_load, independent of the sweep time. An error of 0.5 % or less needs C_mod of 26 µF or less at the lowest load capacitance. The capacitance of TOPCon and HJT modules at MPP is not verified in this note; the 20 ms bound in R3 remains a working figure until a source or a measurement confirms it.
- **Sample skew.** Converting V and I 20 µs apart gives up to 0.13 % error in Pmax at nominal capacitance (0.16 % at -20 %), in the high-current case. Firmware removes it by interpolating each voltage to the time of its current sample.

## 3. Range, resolution and accuracy (R1, R2, R5, R6)

**Range (R1, R2).** Cold-weather Voc at a -10 °C cell temperature is 24.3 V, 41.4 V, 54.7 V and 83.1 V for the four cases, all below 100 V. Two 450 W reference modules in series reach 99.0 V at STC and 109.4 V at -10 °C, so the 100 V check refuses them; the manual must say so. At 100 V the capacitors have a 1.60 times voltage margin and the MOSFETs 1.50 times. At 20 A the shunt dissipates 1.6 W against its 3 W rating, and the load MOSFET conducts 0.15 J per sweep. Both are met by design review.

**Resolution.** The divider gives a voltage full scale of 109.1 V (26.6 mV per count); the shunt and amplifier give 20.48 A full scale (5.00 mA per count).

**Accuracy (R5).** After a two-point calibration, drift over 30 °C leaves ±0.17 % of reading ±0.024 % of full scale on voltage and ±0.21 % of reading ±0.026 % of full scale on current, inside ±1 % ±0.1 %. The amplifier offset before calibration is worth 6.25 mA, so the zero must be calibrated. R5 is met on paper; it depends on calibration against a meter and on the component grades in `bom/bom.csv` line 4.

**Repeatability (R6).** Quantization at the reference MPP is 0.079 % of Pmax per sample and the instrument contributes ±0.27 % to Pmax, so the ±1 % target will be set by irradiance drift between sweeps. R6 cannot be verified at TRL 3.

## 4. Irradiance and STC uncertainty (R7, R8)

Table 3. STC Pmax uncertainty (root sum square)

| Term | Value |
| --- | --- |
| Reference cell calibration | ±3 to ±5 % |
| Spectral and angle mismatch | ±2 % |
| Module temperature, ±2 °C at -0.35 %/°C | ±0.7 % |
| Instrument, V and I | ±0.27 % |
| Total | ±3.7 to ±5.4 % |

R8 (±5 %) is met only if the reference cell calibration is within ±4.5 %; R7 (±5 % irradiance) needs ±4.6 %. Both are **at risk** until the once-calibrated reference cell (decision 6) shows its uncertainty. CalRig (reference ±0.2 °C from 10 to 40 °C) can check the temperature probe in that range but not at module operating temperatures of 60 °C and more, and not the reference cell.

## 5. Discharge and heat (R11, R13)

**Discharge (R11, met).** The active path has a 145 ms time constant (174 ms at +20 % capacitance): 100 V falls below 30 V in 0.21 s and below 1 V in 0.80 s, against 2 s. The passive bleed has a 66 s time constant (79 s at +20 %): 100 V falls below 60 V in 40 s, against 60 s. Peak dump power is 455 W and peak dump current 4.5 A for milliseconds; the bleed draws 10 mA (1.0 W) at 100 V, which firmware subtracts from the current reading. At 99 % of Voc the module still delivers up to 2.51 A (rating limit case), more than the 0.5 A at which R11 allows the circuit to open. Firmware must keep the load switch closed until the current falls below 0.5 A, at most 6 ms more with +20 % capacitance. With that rule R11 is met.

**Stored energy.** 33 J at 100 V (22 J with 4.4 mF). At one sweep every 5 s the dump resistor averages 1.6 W for the reference module and 6.6 W at the 100 V limit.

**Heat (R13, at risk).** The case has 0.113 m² of outside area and a 0.0286 m² lid, so it sheds 1.02 W/K. In full sun at 45 °C ambient:

Table 4. Inside temperature, lumped model

| Case color | Reference module, one sweep per 5 s | 100 V limit, one sweep per 5 s |
| --- | --- | --- |
| Light grey (absorptance 0.30) | 11.0 W, about 56 °C | 16.0 W, about 61 °C |
| Dark (absorptance 0.90) | 28.2 W, about 73 °C | 33.2 W, about 78 °C |

Solar gain on the lid dominates. Even a light case reaches about 56 °C inside, above the usual 45 °C charging limit of a Li-ion cell and close to the limits of commodity display boards. The design therefore needs a light-colored case, a charger with a temperature cut-off (added to `bom/bom.csv` line 10), and the advice to keep the tracer in shade between sweeps. A sun hood over the display is proposed in PVT-DDR-001 as an open item. Display readability in direct sun is **not met** with the adopted TFT (decision 5).

## 6. Battery (R14)

The controller and display draw 0.60 W and the isolated side 0.25 W at 5 V, or 0.94 W from the cell through the boost. A 3,000 mAh cell with 90 % usable (9.7 Wh) gives **10.3 h**, about 1,853 sweeps at 20 s each. R14 (8 h or 200 sweeps) is met. The TRL 2 figure of 16 h left out the isolation and the boost.

## 7. Mass, size and cost (R12, R17)

Table 5. Mass estimate

| Item | Mass (g) |
| --- | --- |
| Enclosure body and lid, ABS 3 mm, with bumpers and glands | 402 |
| Load capacitors, 3 x 75 g | 225 |
| Test leads, 2 x 1 m 4 mm² with MC4 | 162 |
| Sensor pod with 3 m cable | 150 |
| DC isolator | 120 |
| Battery, holder, charger | 72 |
| Hardware and consumables | 50 |
| Controller and display | 45 |
| Dump and bleed resistors | 45 |
| Measurement board; MOSFETs and bar; fuse and holder | 40 each |
| Window and gasket; isolation board | 10 each |
| **Total** | **1,410** |

R12 is met: 1.41 kg against 1.5 kg. The case grows from 200 x 120 x 75 mm to 220 x 130 x 80 mm to fit the third capacitor and the isolation board with no clashes (the model checks this). Over the bumpers it is 234 x 144 x 80 mm, 244 mm over the glands and 98 mm to the top of the isolator knob, inside 250 x 150 x 100 mm.

The priced BOM totals **$163.00**. Against the $150 in `project.yaml` that is $13 over, so **R17 is not met**. Against the $165 recommended in the TRL 2 review (proposed, awaiting Amish; `budget_usd` is unchanged) the margin is $2. The increase is the third capacitor ($6) and the isolation barrier ($8), less $1 of rounding in the TRL 2 total.

## 8. Results

Table 6. Requirement status (from `docs/04-calcs/results.csv`)

| ID | Value | Target | Status |
| --- | --- | --- | --- |
| R1 | 0 to 100 V; high-voltage case 83 V at -10 °C; capacitors 160 V, MOSFETs 150 V | 0 to 100 V, below 120 V | Met (design review) |
| R2 | 0 to 20.48 A full scale; shunt 1.6 W of 3 W at 20 A | 0 to 20 A | Met (design review) |
| R3 | 20.5 ms high-current case at 6.6 mF nominal (16.4 ms at -20 %); 32 ms reference; up to 81 ms | 20 to 200 ms | **Not met** (worst-case tolerance) |
| R4 | 410 pairs minimum | 200 or more | Met |
| R5 | V ±0.17 % ±0.024 % FS; I ±0.21 % ±0.026 % FS | ±1 % of reading ±0.1 % FS | Met on paper (needs calibration) |
| R6 | Instrument noise 0.08 % per sample | Pmax ±1 % over 3 sweeps | Not verifiable at TRL 3 |
| R7 | Irradiance ±3.6 to ±5.4 %; temperature ±2 °C budget | ±5 %, ±2 °C | At risk |
| R8 | ±3.7 to ±5.4 % (needs reference cell within ±4.5 %) | ±5 % or better | At risk |
| R9 | About 7 or more samples per volt; rules drafted | Flags within 5 s | Not verifiable at TRL 3 |
| R10 | A, B, C, reject thresholds adopted for TRL 3; editable table | Partner-editable grades | Met (design review) |
| R11 | 30 V in 0.21 s; 60 V passive in 40 s; opens below 0.5 A after up to 6 ms more | 30 V in 2 s; 60 V in 60 s; open below 0.5 A | Met |
| R12 | 1.41 kg; 234 x 144 x 80 mm over bumpers | 1.5 kg; 250 x 150 x 100 mm | Met |
| R13 | Inside about 56 °C (light case) to 73 °C (dark) at 45 °C in sun; TFT not sun-readable; IP54 case | 0 to 45 °C, sun, IP54, readable | **Not met** (display); at risk (heat) |
| R14 | 10.3 h, about 1,853 sweeps | 8 h or 200 sweeps | Met |
| R15 | CSV fields defined in PVT-PRC-001; no firmware at TRL 3 | CSV per sweep, USB or Wi-Fi export | Met (design review) |
| R16 | No insulation test in this instrument | Detect insulation faults | **Not met** (out of scope) |
| R17 | $163 in parts | $150 or less (proposed $165) | **Not met** at $150; met at proposed $165 |

> **Safety:** These calculations cover a live DC instrument at up to 100 V and 20 A that stores up to 33 J. The discharge times assume both the active and passive paths are fitted and working; never rely on one alone, and treat the capacitors as charged until the display reads below 30 V. The heat results show the Li-ion cell can exceed its charging limit in sun; charge only in shade with the isolator open.
