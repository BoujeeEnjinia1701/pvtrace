# PVTrace

![TRL 2](https://img.shields.io/badge/TRL-2%20of%209-0F766E) ![Hardware: CERN-OHL-S-2.0](https://img.shields.io/badge/hardware-CERN--OHL--S--2.0-111827) ![Software: MIT](https://img.shields.io/badge/software-MIT-111827)

**Area:** CleanTech · **TRL:** 2 of 9 (concept formulated) · **Prototype budget:** about $150 USD · **Difficulty:** 3 of 5

A handheld solar panel IV curve tracer that sweeps a panel's current and voltage in the field, flags shading, cracked cells and degraded strings, and helps grade second-life panels.

![PVTrace concept](media/hero.png)

[Interactive 3D model](media/viewer.html) · [Concept blueprint (PDF)](media/concept-blueprint.pdf) · [Review note](docs/REVIEW.md)

## Concept rationale

An IV curve is the most informative single test of a solar module: one sweep from short circuit to open circuit shows its power, and the shape of the curve points to shading, a failed bypass diode, cracked cells, corroded connections or plain wear. PVTrace uses the simplest load that can trace that curve, a capacitor bank that the module charges in a few tens of milliseconds, as proven open designs such as [IV Swinger 2](https://github.com/csatt/IV_Swinger) and [Cáceres et al. (2020)](https://doi.org/10.3390/en13174320) have done. It adds what a field user needs: a handheld case with a screen, an irradiance reference cell and temperature probe, translation to standard test conditions and a transparent grading rule.

Keeping it open and garage-buildable matters because the people who most need to grade panels, small installers, repair shops and second-life programs in lower-income markets, are the least able to buy a commercial tracer. PVTrace stays below 100 V so it remains an extra-low-voltage instrument for single modules and short strings, uses about $150 of common parts, and writes every sweep to an open CSV file that anyone can check or reprocess.

## Burning platform

Solar is being installed faster than ever: global capacity rose to nearly 3 TW at the end of 2025, with about 698 GW added in that year ([IEA PVPS, 2026](https://iea-pvps.org/snapshot-reports/snapshot-2026/)). Panel waste could reach 78 million tonnes by 2050 ([IRENA and IEA PVPS, 2016](https://www.irena.org/publications/2016/Jun/End-of-life-management-Solar-Photovoltaic-Panels)), yet about 70 % of modules are taken down before the end of their 25 to 30 year design life ([Huang and Long, *Nature Communications*, 2026](https://www.nature.com/articles/s41467-026-69171-z)), and field data show a median power loss of only about 0.5 % a year ([Jordan and Kurtz, 2013](https://onlinelibrary.wiley.com/doi/abs/10.1002/pip.1182)). Many removed modules could work for years more.

The obstacle is trust. Refurbished modules exported to secondary markets show 10 to 20 % power loss and inconsistent quality ([Huang and Long, 2026](https://www.nature.com/articles/s41467-026-69171-z)), and a buyer cannot see that by eye. A commercial tracer that would show it costs thousands of dollars; a single-module kit lists at $3,799 ([Transcat](https://www.transcat.com/seaward-pv210-solar-kit-389a912)).

## Where it could be used

### By industry

| Industry | Use |
| --- | --- |
| Panel reuse and recycling | Grade removed modules as A, B, C or reject before resale or recycling, with a logged curve for each |
| Solar installation and maintenance | Find the underperforming module, bypass diode or connector in a small rooftop or off-grid array |
| Off-grid and mini-grid operators | Check modules on delivery and during annual maintenance in remote sites |
| Technical and vocational training | Teach how curve shape reveals faults, with an instrument students can build and repair |
| Research | Log low-cost outdoor curves over months for degradation studies |
| Used-panel trade and consumer protection | Let a buyer or inspector check a seller's power claim on the spot |

### By country or region

| Country or region | Why it matters there |
| --- | --- |
| Sub-Saharan Africa and the Middle East | Projected PV waste of about 1.6 and 1.7 million tonnes by 2050, over 90 % from imported modules, many of them second-hand ([Huang and Long, 2026](https://www.nature.com/articles/s41467-026-69171-z)). |
| India | Cumulative solar waste could reach up to 600 kilotonnes by 2030 ([CEEW, 2024](https://www.ceew.in/press-releases/robust-recycling-increasing-solar-waste-critical-indias-energy-security-ceew)); a large repair and resale trade can use cheap grading. |
| Australia | World-leading rooftop solar per person and about 280,000 tonnes of end-of-life panels by the end of 2025; researchers propose a resale certification with simple grades ([UniSA, 2025](https://unisa.edu.au/media-centre/Releases/2025/old-solar-panels-can-power-new-future/)). |
| United States | Up to 1 million tons of panel waste expected by 2030 and up to 10 million tons by 2050 ([US EPA](https://www.epa.gov/hw/end-life-solar-panels-regulations-and-management)); reuse programs need test data per module. |
| European Union | PV panels fall under the WEEE Directive ([Directive 2012/19/EU](https://eur-lex.europa.eu/eli/dir/2012/19/oj/eng)), so a logged test per module helps decide between reuse and recycling. |

## What sparked the idea

It came out of a September 2026 review of Design Molecule's applied research areas against the open projects already in the lab. It extends the lab's clean tech and circular work, alongside CellCheck, which grades salvaged battery cells. The trigger in the wider world is the growing trade in used modules and recent work showing that exported refurbished panels often underperform, while grading schemes are being proposed to rebuild buyer confidence ([Huang and Long, 2026](https://www.nature.com/articles/s41467-026-69171-z); [UniSA, 2025](https://unisa.edu.au/media-centre/Releases/2025/old-solar-panels-can-power-new-future/)).

## Problem

Installers and reuse programs judge panels by eye or by a single voltage reading, missing faults that an IV curve shows at once. Commercial tracers cost thousands of dollars.

Full problem statement: [docs/01-problem.md](docs/01-problem.md)

## Concept

A handheld tracer for single modules and short strings up to 100 V and 20 A. The module charges a 4.4 mF capacitor bank in about 13 to 43 ms (estimate) while the tracer samples several hundred voltage and current pairs. A reference cell and a probe on the module back give irradiance and temperature, so the curve can be translated to standard test conditions (IEC 60891). The tracer flags shading or bypass diode steps, high series resistance, low shunt resistance and current loss, grades second-life modules against nameplate, and saves every sweep as CSV. Estimated mass is about 1.35 kg and parts cost about $149.

Full design precis: [docs/02-concept.md](docs/02-concept.md) · Requirements: [docs/03-requirements.md](docs/03-requirements.md)

Not yet met on current estimates: the 20 ms minimum sweep time for high-current modules, sunlight readability of the display, and insulation screening of second-life modules (out of scope; use an insulation tester alongside). Details are in the [review note](docs/REVIEW.md).

## Key components

- Capacitive load: 2 x 2200 µF 160 V capacitors, load and discharge MOSFETs, 22 ohm 50 W dump resistor
- Measurement board: 4 milliohm shunt, current-sense amplifier, voltage divider, dual 12-bit ADC
- Reference cell and module temperature probe in a clip-on sensor pod
- ESP32 controller with 2.8 in display, microSD logging and Wi-Fi export
- 20 A DC fuse, 2-pole DC isolator and MC4 test leads
- Protected 18650 Li-ion cell with USB-C charging
- IP54 handheld case

The working bill of materials is in [bom/bom.csv](bom/bom.csv).

## Safety

> Solar panels produce dangerous DC voltage whenever light falls on them and cannot be switched off. Rate leads and switching for the full voltage and current, mate and unmate MC4 connectors only with the isolator open, and never break a DC circuit under load. PVTrace is limited to 100 V DC; never connect it to a longer string. The load capacitors store up to 22 J and must be discharged before the case is opened. The instrument contains a Li-ion cell; charge it on a non-flammable surface and not while connected to a module. Handle modules with gloves: frames are sharp and broken glass can cut.

## Repository layout

| Folder | Contents |
| --- | --- |
| `docs/` | Problem, concept, requirements, calculations and design decisions |
| `cad/src/` | build123d Python source, the source of truth for all geometry |
| `cad/step/`, `cad/stl/` | Exported models for FreeCAD, other CAD tools and printing |
| `cad/drawings/` | 2D sketches and dimensioned drawings |
| `bom/` | Bill of materials |
| `electronics/` | KiCad schematics and PCB layouts |
| `firmware/` | Microcontroller code |
| `media/` | Renders, perspectives and photos |
| `build-log/` | Dated prototyping notes |

## Documentation

Controlled documents follow the portfolio [documentation standard](.kit/STANDARDS.md). Each carries a document ID (PVT-PRC-001 for the precis), a version and a revision history. Branded PDFs are built with `python .kit/render.py` and attached to GitHub Releases when a document is tagged, for example `PVT-PRC-001/v1.0`.

## Licenses

- **Hardware** (CAD, drawings, BOM, electronics): [CERN-OHL-S v2](LICENSE)
- **Software** (firmware, scripts, notebooks): [MIT](LICENSE-SOFTWARE)

A project of the [Design Molecule](https://designmolecule.com) lab. Extending strong areas set.
