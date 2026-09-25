# Geiger + Wemos NodeMCU enclosure

This is a first parametric enclosure prototype for:

- CAJOE RadiationD v1.1 Geiger counter PCB, approximately 64 × 120 mm;
- black Wemos NodeMCU V3 (ESP8266, EAN 5904422300647), measured at
  **58 × 25 mm** with a **43 × 21 mm** mounting-hole pattern and 3.5 mm holes.

The enclosure was derived from photographs against a ruler and a 10 mm cutting
mat. Verify the values below before committing to a long print. All important
dimensions are grouped at the top of `enclosure_common.py`.

## Intended assembly

The temporary acrylic sheet and brass standoffs shown in the reference photos
are **not** part of the final assembly. Both PCBs mount directly to four 5 mm
high printed posts. The Wemos board is the version without long header pins.
Its antenna end points towards the rear wall and is kept clear of components.

The Geiger board's barrel-power connector is reached through the front opening.
There is intentionally no external USB opening. The ESP8266 is powered from the
Geiger PCB: connect regulated **5 V to VIN** and **GND to GND**. Never connect
5 V to `3V3` or directly to a GPIO. Keep the existing level protection between
the Geiger pulse output and `D1`/GPIO5. A locating lip holds the lid; a small
relief on the right-hand side provides a pry point.

External size: approximately **118 × 138 × 35 mm** with the lid fitted.

## Files

- `geiger_enclosure_base.step` and `.stl`: enclosure base in print orientation;
- `geiger_enclosure_base_18mm.3mf`: print-ready base with the corrected 18.0 mm
  barrel-jack position, while the original STL remains unchanged;
- `geiger_enclosure_lid.step` and `.stl`: lid with its visible face on the print
  bed and locating lip facing upward;
- `geiger_enclosure_lid_multicolor.step` and `.3mf`: the same lid plus a
  separately selectable black logo inlay for a multi-material slicer;
- `geiger_enclosure_fit_check.step`: closed assembly with conservative PCB and
  component-height envelopes;
- `geiger_enclosure_exploded.step`: exploded review assembly;
- `enclosure_common.py`: editable build123d source in millimetres.

## Before printing

Measure these four values on the physical hardware and update the corresponding
constants if they differ by more than 0.5 mm:

1. Geiger PCB width and length (`GEIGER_WIDTH`, `GEIGER_DEPTH`);
2. Geiger mounting-hole pitch (`GEIGER_HOLE_X`, `GEIGER_HOLE_Y`);
3. Wemos mounting-hole pitch (`NODE_HOLE_X`, `NODE_HOLE_Y`), currently set to
   the measured 21 × 43 mm;
4. centre distance from the front-left Geiger mounting hole to the barrel-jack
   centre (`GEIGER_DC_HOLE_TO_CONNECTOR_X`), measured at **18.0 mm**.

The CAD source, STEP review models and `geiger_enclosure_base_18mm.3mf` use the
measured 18.0 mm distance. The previously generated base STL is intentionally
left unchanged and still uses the earlier 16.0 mm estimate; use the corrected
3MF for the final base.

## Two-colour lid

Open `geiger_enclosure_lid_multicolor.3mf` in a multi-material slicer. Assign
the `Lid body` object to the main colour and `Black logo inlay` to black. In
Bambu Studio these two filament colours are already stored as white and black.
Keep the supplied orientation: the visible face is on the print bed, so the
logo starts in the first layer and is printed flush with the outside face. A
single-nozzle printer can produce the same result by configuring the slicer's
object-based filament changes.

Both 3MF files are Bambu-native project archives and were reopened with Bambu
Studio 2.8.2.61. Each contains one printable plate; the lid contains two mesh
parts so its logo remains independently colourable.

For a quick fit test, print only the first 8 mm of the base or use the slicer's
cut feature. The printed M3 holes are deliberately undersized pilot holes and
may be opened with a drill after the fit test. Avoid powering the board from
USB and `VIN` at the same time unless that specific board's power-path isolation
is verified.

This enclosure has no IP rating. Use PETG or ASA rather than PLA if it will be
placed in sun or a warm outdoor shelter. Keep the high-voltage Geiger PCB fully
enclosed and disconnect power before opening the case.

The recessed radiation symbol is generic. The uRADMonitor wordmark is included
for this community integration; confirm brand-use permission before selling or
commercially distributing a branded enclosure.
