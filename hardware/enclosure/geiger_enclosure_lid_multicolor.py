"""STEP generator for the print-oriented two-colour enclosure lid."""

from build123d import Compound

from enclosure_common import make_lid_print_orientation, make_logo_inlay


def gen_step():
    lid = make_lid_print_orientation()
    lid.label = "Lid body"
    return Compound(
        children=[lid, make_logo_inlay()],
        label="Two-colour recessed-logo lid",
    )
