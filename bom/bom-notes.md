# BOM notes

- Line numbers match the callouts in `media/exploded.png` and Table 1 of `docs/02-concept.md`. Line 13 (hardware and consumables) is not modeled.
- Costs are indicative single-unit prices in USD from typical online and distributor listings in September 2026. They are estimates, not quotes. Supplier types are given for every line; named distributors are examples, not selections.
- Total: $164.00 (checked by `docs/04-calcs/sizing.py`). Against the $165 in `project.yaml` (raised from $150 by Amish's decision of 2026-09-25, PVT-DDR-002) the margin is $1, so R17 is met.
- Changes at TRL 3 (PVT-DDR-001): a third load capacitor on line 5 (+$6), the isolation barrier as new line 14 (+$8), a light grey case on line 1 and a charger with a temperature cut-off on line 10 at no added cost.
- Open options that would change the total: a fourth load capacitor for R3 at tolerance (about +$6), a transflective display for R13 (about +$10).
- Change from PVT-DDR-002: printed PETG display sun hood as new line 15 (+$1, material only), callout 15 in the exploded view.
- Brand-matched MC4 connectors are specified on purpose. Cheaper mixed-brand connectors can overheat when mated with a module's own connectors.
- The PV module, stand and module leads shown in grey in the media are not part of the kit.
