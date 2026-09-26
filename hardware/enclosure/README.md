# Printable enclosure

This directory contains the current compact v7 print files:

- `cajoe_geiger_esp_v7_base.stl`
- `cajoe_geiger_esp_v7_lid.stl`

The lid is currently supplied as a single-colour STL model. Editable STEP
source files are intentionally not published.

## Reference geometry

- Enclosure outside dimensions: approximately 160 × 75 × 35 mm
- Geiger PCB: approximately 126 × 63 mm
- Geiger PCB mounting-hole pitch: approximately 101.2 × 56.8 mm
- Base mounting holes: 3.3 mm diameter
- ESP8266 board: approximately 58 × 25 mm
- ESP8266 mounting-hole pitch: 43 × 21 mm
- ESP8266 mounting holes: 3.8 mm diameter
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
