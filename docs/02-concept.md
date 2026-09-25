---
doc_id: PVT-PRC-001
title: PVTrace design precis
project: PVTrace
doc_type: Design precis
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
  change: Concept for TRL 2; how it works, components, first-order numbers, proposed choices, safety, open questions
---

# PVTrace design precis

## Summary

PVTrace is a handheld, battery-powered IV curve tracer for single PV modules and short strings up to 100 V and 20 A. It sweeps the module from short circuit to open circuit by letting it charge a 4.4 mF capacitor bank in about 13 to 43 ms, samples several hundred voltage and current pairs, reads irradiance from a reference cell and temperature from a probe on the module back, translates the curve to standard test conditions (STC) and shows fault flags and a second-life grade on its screen. Every sweep is saved as an open CSV file. Parts cost about $149 (indicative), within the $150 budget with almost no margin. The capacitive load follows proven open designs (IV Swinger 2; Cáceres et al., 2020, see PVT-PRB-001); what is new is a standalone field instrument with sensing, translation and a transparent grading rule.

![Figure 1. PVTrace in use: the tracer on the ground, test leads mated to the module's own MC4 leads and the sensor pod clipped to the lower frame edge.](../media/hero.png)

Figure 1. PVTrace in use (concept massing model; grey module and stand for scale).

## How it works

1. **Connect.** The user mates the two MC4 test leads to the module's leads with the DC isolator open, clips the sensor pod to the module's lower frame so the reference cell lies in the module plane, and presses the probe onto the module back.
2. **Check.** With the isolator closed and the load switch off, the controller reads open-circuit voltage through the divider. It refuses to continue if the polarity is reversed or Voc exceeds 100 V.
3. **Sweep.** The load MOSFET closes onto the discharged capacitor bank. The module first delivers close to its short-circuit current, then the capacitor voltage rises through the knee to Voc. The ADC samples voltage and current in pairs throughout. Because the capacitor stops drawing current at Voc, the MOSFET only ever opens at near zero current.
4. **Dump.** The load MOSFET opens and a second MOSFET discharges the bank through a 22 ohm aluminium-clad resistor in about 0.1 s. A permanent 10 kohm bleed resistor empties the bank if the controller fails.
5. **Analyze.** Firmware extracts Isc, Voc, Pmax, Vmp, Imp and fill factor, estimates series and shunt resistance from the slopes near Voc and Isc, and looks for steps that show bypass diode conduction.
6. **Translate and grade.** Using irradiance, module temperature and the datasheet coefficients the user selects, it translates the curve to STC with IEC 60891 procedure 1 and compares Pmax with nameplate to give a grade.
7. **Log.** The sweep, conditions, flags and grade go to microSD and can be exported by USB or to a phone over Wi-Fi.

![Figure 2. One sweep from module to grade, with estimated energy per sweep for the reference module.](../media/flow.png)

Figure 2. Measurement and energy flow for one sweep (estimates).

## Main components

Numbers match `bom/bom.csv` and the exploded view (Figure 3).

Table 1. Main components

| No. | Component | Role |
| --- | --- | --- |
| 1 | Enclosure body, IP54 ABS handheld case with rubber corner bumpers and three cable glands | Houses and protects the electronics |
| 2 | Enclosure lid with display window and gasket | Closes the case; window for the display |
| 3 | Controller and 2.8 in display board (ESP32 class, microSD) | Runs the sweep, analysis, grading, logging, Wi-Fi export |
| 4 | Measurement board: 4 milliohm shunt, current-sense amplifier (INA240 class), voltage divider, dual 12-bit ADC with precision reference | Measures V and I during the sweep |
| 5 | Load capacitors, 2 x 2200 µF 160 V electrolytic | The sweep load |
| 6 | Load and discharge MOSFETs (150 V class) with gate driver on an aluminium bar | Connects and empties the load |
| 7 | Discharge resistor, 22 ohm 50 W aluminium clad, plus 10 kohm 3 W passive bleed | Absorbs the stored energy |
| 8 | DC fuse, 20 A gPV 10 x 38 mm, in a DC-rated holder | Protects the leads and switch from a fault |
| 9 | DC isolator, 2-pole, rated 20 A at 250 V DC or more | Separates the instrument from the module when not sweeping |
| 10 | Li-ion 18650 protected cell, holder, USB-C charger and protection | Powers the controller and display |
| 11 | Test leads, 2 x 1 m, 4 mm² double-insulated PV cable with MC4 connectors | Connects to the module |
| 12 | Sensor pod: reference cell and shaded temperature probe, frame clip, 3 m cable | Measures irradiance and module temperature |
| 13 | Hardware and consumables (not modeled) | Screws, standoffs, wire, gaskets |

![Figure 3. Exploded view with BOM callouts.](../media/exploded.png)

Figure 3. Exploded view; callouts match Table 1.

![Figure 4. Section through the enclosure.](../media/cutaway.png)

Figure 4. Cutaway: capacitors (blue) and discharge resistor (brown) on the floor, MOSFET bar (purple), measurement board (green) under the isolator (amber), controller and display (teal) under the lid.

## First-order numbers

All values are estimates for review and will be checked at TRL 3.

Table 2. Sweep time and energy with a 4.4 mF load (single-diode model, time to 99 % of Voc)

| Case | Voc (V) | Isc (A) | Sweep time (ms) | Energy stored (J) |
| --- | --- | --- | --- | --- |
| 36-cell 100 W | 22.0 | 6.0 | 18 | 1.1 |
| 108 half-cell 410 W (high current) | 37.5 | 13.9 | 13 | 3.1 |
| 144 half-cell 450 W (reference) | 49.5 | 11.6 | 21 | 5.4 |
| 2 x 60-cell 250 W in series (high voltage) | 75.2 | 8.9 | 43 | 12.4 |
| Rating limit | 100 | 20 | about 29 (scaled) | 22 |

Assumptions: datasheet-class values; sweep time roughly scales as C x Voc / Isc; the model ignores cell capacitance and lead resistance.

- **Sweep time.** The high-current case sweeps in about 13 ms, below the 20 ms target in R3. A third capacitor (6.6 mF) would lift it to about 20 ms and the high-voltage case to about 64 ms, at about $6 and 50 g more; this is proposed below.
- **Samples.** At 25,000 pairs per second (half the ADC's rated rate), a sweep yields about 325 pairs (13 ms) to 1,070 pairs (43 ms), against R4's 200.
- **Resolution.** Voltage: divider to a 4.096 V reference gives about 110 V full scale and about 27 mV per count. Current: 4 milliohm shunt with a gain of 50 gives about 20.5 A full scale and about 5 mA per count. Shunt loss at 20 A is 1.6 W for tens of milliseconds.
- **Discharge.** 22 ohm with 4.4 mF gives a 97 ms time constant: 100 V falls below 30 V in about 0.12 s and below 1 V in about 0.45 s. Peak dump power is about 455 W for milliseconds; the average at one sweep every 5 s is at most 4.4 W, well within a 50 W resistor on its own bracket. The 10 kohm bleed (44 s time constant) takes 100 V below 60 V in about 23 s and draws 10 mA at 100 V, which firmware subtracts from the current reading.
- **Switch losses.** With about 10 milliohm on-resistance, conduction loss in the load MOSFET is well under 0.1 J per sweep.
- **Battery.** An ESP32 board with a lit 2.8 in TFT draws about 0.6 W on average (estimate); a 3,000 mAh 18650 (about 10.8 Wh) gives about 16 h of use.
- **STC uncertainty.** Reference cell ±3 to 5 %, spectral and angle mismatch about ±2 %, temperature ±2 °C (about ±0.7 % at -0.35 %/°C), V and I about ±1.4 % combined: root-sum-square about ±5 to 6 %. R8 (±5 %) is at risk until the reference cell is calibrated better.
- **Mass.** Case 380 g, capacitors 150 g, leads 160 g, sensor pod with cable 150 g, isolator 120 g, remaining parts about 390 g: about 1.35 kg.
- **Cost.** About $149 in parts (see `bom/bom.csv`), against the $150 budget.

## Fault flags and grading (draft rules)

Table 3. Draft fault rules

| Flag | Curve symptom | Draft rule |
| --- | --- | --- |
| Shading or bypass diode active | Step or plateau in the curve | Local minimum in dI/dV, or current drop of 10 % or more within 3 % of Voc, below Vmp |
| High series resistance | Shallow slope near Voc | Estimated Rs more than 1.5 times the model value for the module type |
| Low shunt resistance | Steep slope near Isc | Estimated Rsh below 10 times Vmp/Imp |
| Current deficit (soiling, degradation, cracks) | Isc low against irradiance | Isc at STC below 90 % of nameplate |
| Missing substring | Voc about one third low | Voc at STC below 70 % of nameplate |

Proposed grades from STC Pmax against nameplate: A 90 % or more, B 80 to 90 %, C 70 to 80 %, reject below 70 % or with any safety defect found by visual inspection (broken glass, burnt junction box, delaminated backsheet). Grades are indicative; they are not a certification.

## Key design choices (all proposed, awaiting Amish)

1. **Load type.** Options: capacitive load (recommended: simple, fast, low heat, proven in open designs), electronic MOSFET load (slower, more heat, more control), or a resistor bank with relays (bulky, coarse). 
2. **Voltage and current rating.** Options: 100 V, 20 A (recommended; single modules and two in series, below the 120 V DC extra-low-voltage limit); 60 V, 15 A (single modules only, cheaper parts); or 1,000 V strings (not garage-safe; out of scope).
3. **Load capacitance.** Options: 4.4 mF with two capacitors (baseline, fits the budget, misses R3 for high-current modules) or 6.6 mF with three (recommended if the budget moves; meets R3 for all cases in Table 2).
4. **Isolation of the controller from the PV side.** Options: A, no galvanic isolation; the measurement ground is the PV negative and USB charging is locked out while the isolator is closed (baseline, fits the budget); B, a digital isolator and isolated DC-DC converter between the measurement board and controller (about $8 more, safer when a laptop is plugged in). Recommendation: B, which needs the budget to rise to about $165.
5. **Display and interface.** Options: on-device 2.8 in TFT plus phone export (recommended), phone only over Wi-Fi (cheaper, no screen to read in sun), or a transflective or e-paper display (readable in sun, slower, about $10 more).
6. **Irradiance sensing.** Options: small reference cell measured at short circuit (recommended), a silicon pyranometer (more accurate, about $150 or more), or inferring irradiance from a known-good module.
7. **Controller.** ESP32 display board (recommended for cost and Wi-Fi), or an RP2040 with a separate display.
8. **Grade thresholds** as above, to be agreed with a second-life partner.

## Links to other lab projects

- **CellCheck** grades salvaged lithium cells for rebuilt packs; PVTrace applies the same measure, grade and log approach to modules. A shared grade-label and CSV format would help both.
- **CalRig** can check PVTrace's module temperature probe. It does not provide irradiance references, so the reference cell needs a separate calibration route.
- PVTrace does not use a SwapCell pack; a single 18650 cell is enough.

## Safety

> **Safety:** PV modules are live whenever light falls on them. The tracer handles up to 100 V DC and 20 A, which can cause burns and sustained DC arcs. Mate and unmate MC4 connectors only with the isolator open and never under load. Use brand-matched MC4 connectors from one maker; mixed brands can overheat.

> **Safety:** The load capacitors store up to 22 J at 100 V. Active and passive discharge paths are required; treat the capacitors as charged until the display reads below 30 V, and never open the case with the leads connected.

> **Safety:** The discharge resistor and MOSFET bar get hot under repeated sweeps; firmware limits the sweep rate to one every 5 s.

> **Safety:** The instrument contains a Li-ion cell. Use a protected cell, charge it only with the isolator open, on a non-flammable surface, within 0 to 45 °C, and never leave it charging unattended in a hot vehicle.

> **Safety:** Handling modules involves sharp frame edges, heavy glass (about 20 to 25 kg for large modules) and work at height on rooftops. Broken modules can cut and may still be live. Wear gloves and eye protection, and follow local rules for work at height.

> **Safety:** Do not connect PVTrace to a string of an installed grid-connected system unless the owner has isolated it from the inverter and the string Voc is below 100 V.

## Open questions

- [ ] Is 20 ms the right lower bound on sweep time for TOPCon and HJT modules, or is a longer sweep needed?
- [ ] How to capture true Isc: extrapolate from the first samples, or pre-charge the bank slightly negative?
- [ ] Which reference cell and calibration route give ±3 % or better at low cost?
- [ ] Can a commodity TFT be made readable in sun with a hood, or is a transflective display needed?
- [ ] What grade label format would buyers and a certification scheme accept?
- [ ] Should the firmware support two modules in parallel (current to 20 A at lower voltage) as well as in series?
