---
doc_id: PVT-PRB-001
title: PVTrace problem statement
project: PVTrace
doc_type: Problem statement
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
  change: Problem with cited evidence, users, context, constraints, prior work and co-design checklist for TRL 2
---

# PVTrace problem statement

Installers and reuse programs judge solar modules by eye or by a single open-circuit voltage reading, which misses the faults an IV curve shows at once: a shaded or cracked substring, a failed bypass diode, high series resistance from corroded connections, or plain power loss. The instrument that shows these, a field IV curve tracer, is priced for utility-scale commissioning crews, so small installers, repair shops and second-life panel programs go without. A single-module commercial kit such as the Seaward PV210 lists at $3,799 ([Transcat](https://www.transcat.com/seaward-pv210-solar-kit-389a912)).

## Why it matters now

- **Volume.** Global PV capacity rose to nearly 3 TW at the end of 2025, with about 698 GW installed in that year alone ([IEA PVPS Snapshot 2026](https://iea-pvps.org/snapshot-reports/snapshot-2026/)). Panel waste could reach 78 million tonnes by 2050 ([IRENA and IEA PVPS, 2016](https://www.irena.org/publications/2016/Jun/End-of-life-management-Solar-Photovoltaic-Panels)).
- **Early removal.** About 70 % of modules are decommissioned before the end of their 25 to 30 year design life ([Huang and Long, *Nature Communications*, 2026](https://www.nature.com/articles/s41467-026-69171-z)), so many removed modules still work.
- **Slow degradation.** Across nearly 2,000 field measurements, the median power loss is about 0.5 % per year ([Jordan and Kurtz, 2013](https://onlinelibrary.wiley.com/doi/abs/10.1002/pip.1182)); a 10-year-old module in good condition typically keeps most of its rated power.
- **Unknown quality in second-hand trade.** Refurbished modules exported to secondary markets show 10 to 20 % power degradation and inconsistent quality, and most of the projected PV waste in Africa and the Middle East will come from imports ([Huang and Long, 2026](https://www.nature.com/articles/s41467-026-69171-z)). Australian researchers propose a resale certification with simple grades to build buyer confidence ([UniSA, 2025](https://unisa.edu.au/media-centre/Releases/2025/old-solar-panels-can-power-new-future/)); any such scheme needs a cheap, repeatable power measurement.

## Users and context

| User | Need | Context |
| --- | --- | --- |
| Second-life panel refurbisher or collector | Grade each module (A, B, C or reject) against its nameplate and record the result | Yard or warehouse, dozens to hundreds of modules a day, outdoor sun on a rack |
| Small installer or solar technician | Find why a rooftop or off-grid array underperforms: shading, a bad module, a hot connector | Rooftops and ground mounts, single modules or short strings, often in hot sun |
| Buyer of used panels (NGO, cooperative, household) | Check that a used module delivers what the seller claims before paying | Market stall or depot; little training |
| Trainer or TVET college | Teach how an IV curve reveals faults, with an instrument students can build | Classroom and outdoor bench |
| Researcher | Log curves over months for degradation studies at low cost | Outdoor test rack |

Typical modules under test are 36-cell (about 22 V open circuit) to 144 half-cell (about 50 V, 12 to 14 A short circuit). Two older modules in series reach about 75 V.

## Prior work

- **IV Swinger 2** by Chris Satterlee is an open-source tracer of about $50 in parts. It uses load capacitors switched by relays or SSRs and drained through a bleed resistor, and runs from a laptop over USB ([GitHub](https://github.com/csatt/IV_Swinger); [firmware comments](https://raw.githubusercontent.com/csatt/IV_Swinger/master/Arduino/IV_Swinger2/IV_Swinger2.ino)). PVTrace keeps the capacitive load and adds standalone field use, irradiance and temperature sensing, STC translation and grading.
- **Cáceres et al. (2020)** built a capacitive-load tracer for 0 to 100 V and 0 to 12 A for under 200 EUR in materials, aimed at training and research centers that cannot afford commercial tracers ([*Energies*](https://doi.org/10.3390/en13174320)).
- **González et al. (2021)** describe an open IoT tracer on a Raspberry Pi with a programmable electronic load, noting that commercial systems are "generally expensive and closed for modifications" ([*Sensors*](https://doi.org/10.3390/s21227650)).
- **Commercial tracers** cover strings to 1,000 V or more and are priced for professional crews ([Transcat listing](https://www.transcat.com/seaward-pv210-solar-kit-389a912)). Industry guidance is that curves converted to standard test conditions (STC) should be taken at 700 W/m² or more, per IEC 61829 ([Seaward](https://www.seaward.com/gb/support/solar/faqs/29495-curve-tracing-faq-s/)).

The gap PVTrace addresses is a handheld, battery-powered, open tracer that works without a laptop, measures irradiance and module temperature, translates to STC and applies a transparent grading rule.

## Constraints

- Garage-buildable prototype, about $150 USD in parts (`project.yaml` budget).
- Off-the-shelf parts and hand tools; no custom machining.
- Voltage kept below 120 V DC, the extra-low-voltage limit for ripple-free DC in IEC 61140 ([summary](https://en.wikipedia.org/wiki/Extra-low_voltage)). Full strings at 600 to 1,500 V are out of scope.
- Works in full sun at up to 45 °C ambient, with no mains power.
- Open data: every sweep saved as a plain CSV that anyone can reprocess.

## Out of scope

- Strings above 100 V open circuit and any work on live grid-connected arrays without isolation by the system owner.
- Insulation resistance, earth continuity and wet leakage tests (IEC 62446-1 commissioning tests beyond the IV curve).
- Electroluminescence or thermal imaging, which show cracks directly; PVTrace infers them from the curve only.
- Certifying modules for sale; PVTrace grades are indicative until a scheme owner adopts them.

## Co-design checklist

- [ ] Identify a second-life panel partner (refurbisher, recycler or reuse program) to agree grade thresholds and throughput.
- [ ] Interview two or more small installers on which faults they meet most and how they find them today.
- [ ] Confirm the module types in the partner's stock (cell count, Voc, Isc) to fix the voltage and current ranges.
- [ ] Agree what a buyer needs to see on a printed or phone grade label.
- [ ] Check local rules for handling and reselling used modules (for example, WEEE in the EU).

## Open questions

- Which grade thresholds would a buyer or scheme trust, and must they match an emerging standard?
- Is a reference cell calibrated once against a pyranometer good enough, or does each unit need its own calibration?
- How many sweeps per module make a reliable grade under passing clouds?

> **Safety:** PV modules produce voltage whenever light falls on them and cannot be switched off. Short-circuit current flows as soon as the terminals are bridged, and a DC arc does not self-extinguish like an AC arc. Never break a DC circuit under load, and never connect the tracer to a string above its rating.
