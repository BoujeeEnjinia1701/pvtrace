# PVTrace

![TRL 2](https://img.shields.io/badge/TRL-2%20of%209-0F766E) ![Hardware: CERN-OHL-S-2.0](https://img.shields.io/badge/hardware-CERN--OHL--S--2.0-111827) ![Software: MIT](https://img.shields.io/badge/software-MIT-111827)

**Area:** CleanTech · **TRL:** 2 of 9 (concept formulated) · **Prototype budget:** about $150 USD · **Difficulty:** 3 of 5

A handheld solar panel IV curve tracer that sweeps a panel's current and voltage in the field, flags shading, cracked cells and degraded strings, and helps grade second-life panels.

## Concept rationale

An affordable tracer makes panel reuse and small-installer maintenance evidence-based.

## Burning platform

Millions of solar panels are reaching end of first life, and many could be reused if they could be graded cheaply.

## Where it could be used

### By industry

| Industry | Use |
| --- | --- |
| _To be developed_ | |

### By country or region

| Country or region | Why it matters there |
| --- | --- |
| _To be developed_ | |

## What sparked the idea

It came out of a September 2026 review of Design Molecule's applied research areas against the open projects already in the lab. It extends the lab's clean tech and circular work.

## Problem

Installers and reuse programs judge panels by eye or by a single voltage reading, missing faults that an IV curve shows at once. Commercial tracers cost thousands.

## Concept

A handheld solar panel IV curve tracer that sweeps a panel's current and voltage in the field, flags shading, cracked cells and degraded strings, and helps grade second-life panels.

Full design precis: [docs/02-concept.md](docs/02-concept.md)

## Key components

- Capacitive or electronic load sweep circuit
- Voltage and current sensing
- Irradiance and temperature sensors
- Microcontroller with display and logging
- MC4 leads and fuse
- Rugged enclosure

The working bill of materials is in [bom/bom.csv](bom/bom.csv).

## Safety

> Solar panels produce dangerous DC voltage in daylight. Rate leads and switching for the string voltage and never break a DC circuit under load.

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
