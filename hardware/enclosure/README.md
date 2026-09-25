# Printable enclosure

This directory intentionally contains only the final, print-ready STL files:

- `geiger_enclosure_compact_v2_base.stl`
- `geiger_enclosure_compact_v2_lid.stl`

Editable STEP files and slicer-specific 3MF files are intentionally not
published.

## Reference geometry

- Enclosure outside dimensions: approximately 168 × 76 × 32 mm
- Geiger PCB: approximately 126 × 63 mm
- Geiger PCB mounting holes: 120 × 57 mm, 3 mm diameter
- ESP8266 board: approximately 58 × 25 mm
- ESP8266 mounting holes: 43 × 21 mm, 3.5 mm diameter
- Barrel-power opening: 19 × 14 mm
- Barrel connector centre: 18 mm from the adjacent Geiger PCB mounting-hole centre

The ESP8266 is rotated 90 degrees and positioned inline with the Geiger PCB to
keep the enclosure compact. The lid uses a snap fit.

## Printing

- Print the base with its floor on the build plate.
- Print the lid with its outside face on the build plate when your printer can
  reproduce the raised lettering cleanly; otherwise rotate it to suit your
  preferred finish and support strategy.
- A 0.20 mm layer height and at least three walls are sensible starting points.
- PLA and PETG are both suitable for an indoor enclosure.
- Test the snap fit and barrel-connector clearance before final assembly.

Dimensions are based on one measured board revision. Confirm critical
clearances if your Geiger or ESP8266 board is a different clone or revision.
