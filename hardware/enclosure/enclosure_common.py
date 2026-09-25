"""Parametric enclosure for a CAJOE RadiationD v1.1 and Wemos NodeMCU V3.

All dimensions are millimetres.  The values at the top are deliberately kept
together: the first prototype is based on photographs against a ruler and a
10 mm cutting mat, so the board and mounting-hole measurements are easy to
adjust after a physical test fit.
"""

from __future__ import annotations

from build123d import (
    Align,
    Box,
    Color,
    Compound,
    Cylinder,
    Location,
    Plane,
    Pos,
    RectangleRounded,
    Rot,
    Text,
    Vector,
    extrude,
)


# Enclosure -----------------------------------------------------------------
OUTER_WIDTH = 118.0
OUTER_DEPTH = 138.0
BASE_HEIGHT = 32.0
CORNER_RADIUS = 7.0
WALL = 2.4
FLOOR = 2.4

LID_PANEL = 3.0
LID_LIP_DEPTH = 3.0
LID_LIP_WALL = 1.8
LID_CLEARANCE = 0.30
LOGO_DEPTH = 0.65


# CAJOE RadiationD v1.1 -----------------------------------------------------
GEIGER_WIDTH = 64.0
GEIGER_DEPTH = 120.0
GEIGER_THICKNESS = 1.6
GEIGER_CENTER_X = -21.0
GEIGER_CENTER_Y = 0.0

# Estimated centre-to-centre pattern.  M3 pilot holes are intentionally small
# enough to be opened with a drill if the production board differs slightly.
GEIGER_HOLE_X = 56.0
GEIGER_HOLE_Y = 112.0
GEIGER_POST_HEIGHT = 5.0
GEIGER_POST_DIAMETER = 6.5
GEIGER_PILOT_DIAMETER = 2.7

# User-measured horizontal centre distance from the front-left mounting hole to
# the round barrel-connector centre.  Keeping the measurement explicit makes
# it possible to verify the wall opening without relying on a board-centre
# estimate.
GEIGER_FRONT_LEFT_HOLE_X = GEIGER_CENTER_X - GEIGER_HOLE_X / 2
GEIGER_DC_HOLE_TO_CONNECTOR_X = 18.0
GEIGER_DC_X = GEIGER_FRONT_LEFT_HOLE_X + GEIGER_DC_HOLE_TO_CONNECTOR_X
GEIGER_DC_OPENING_WIDTH = 18.0
GEIGER_DC_OPENING_HEIGHT = 15.5
GEIGER_DC_OPENING_CENTER_Z = 12.7


# Black Wemos NodeMCU V3, EAN 5904422300647 -------------------------------
# The PCB is mounted with its antenna end towards the rear wall. USB access is
# deliberately omitted because the installed board is powered from the Geiger
# PCB: regulated 5 V to VIN, and GND to GND.
NODE_WIDTH = 25.0
NODE_DEPTH = 58.0
NODE_THICKNESS = 1.6
NODE_CENTER_X = 36.0
NODE_CENTER_Y = 31.0

# User-measured centre-to-centre mounting pattern and hole diameter: 21 x 43
# mm and 3.5 mm. The PCB holes clear M3 screws; the smaller blind holes in the
# printed posts are intentional pilots for those screws.
NODE_HOLE_X = 21.0
NODE_HOLE_Y = 43.0
NODE_MOUNTING_HOLE_DIAMETER = 3.5
NODE_POST_HEIGHT = 5.0
NODE_POST_DIAMETER = 7.0
NODE_PILOT_DIAMETER = 2.7
NODE_ANTENNA_DEPTH = 11.0


# Visual-only board proxies --------------------------------------------------
GEIGER_COMPONENT_ENVELOPE_HEIGHT = 18.0
NODE_COMPONENT_ENVELOPE_HEIGHT = 6.0

FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_SYMBOLS = "/System/Library/Fonts/Apple Symbols.ttf"


def rounded_prism(width: float, depth: float, height: float, radius: float):
    """Return a rounded rectangular prism with its bottom on the XY plane."""

    profile = RectangleRounded(width, depth, radius)
    return extrude(profile, amount=height)


def _post(
    x: float,
    y: float,
    height: float,
    outer_diameter: float,
    pilot_diameter: float,
):
    """Create a floor-mounted post with a blind pilot hole."""

    body = Cylinder(
        outer_diameter / 2,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Pos(x, y, FLOOR))
    pilot = Cylinder(
        pilot_diameter / 2,
        max(0.1, height - 0.8),
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Pos(x, y, FLOOR + 0.8))
    return body - pilot


def geiger_post_locations() -> list[tuple[float, float]]:
    return [
        (GEIGER_CENTER_X + dx, GEIGER_CENTER_Y + dy)
        for dx in (-GEIGER_HOLE_X / 2, GEIGER_HOLE_X / 2)
        for dy in (-GEIGER_HOLE_Y / 2, GEIGER_HOLE_Y / 2)
    ]


def node_post_locations() -> list[tuple[float, float]]:
    return [
        (NODE_CENTER_X + dx, NODE_CENTER_Y + dy)
        for dx in (-NODE_HOLE_X / 2, NODE_HOLE_X / 2)
        for dy in (-NODE_HOLE_Y / 2, NODE_HOLE_Y / 2)
    ]


def make_base():
    """Create the enclosure base with integrated PCB supports and openings."""

    outer = rounded_prism(OUTER_WIDTH, OUTER_DEPTH, BASE_HEIGHT, CORNER_RADIUS)

    inner_width = OUTER_WIDTH - 2 * WALL
    inner_depth = OUTER_DEPTH - 2 * WALL
    inner_radius = max(0.5, CORNER_RADIUS - WALL)
    cavity = rounded_prism(
        inner_width,
        inner_depth,
        BASE_HEIGHT,
        inner_radius,
    ).moved(Pos(0, 0, FLOOR))
    base = outer - cavity

    for x, y in geiger_post_locations():
        base = base + _post(
            x,
            y,
            GEIGER_POST_HEIGHT,
            GEIGER_POST_DIAMETER,
            GEIGER_PILOT_DIAMETER,
        )

    for x, y in node_post_locations():
        base = base + _post(
            x,
            y,
            NODE_POST_HEIGHT,
            NODE_POST_DIAMETER,
            NODE_PILOT_DIAMETER,
        )

    # Front opening for the Geiger board's right-angle barrel connector.
    dc_cut = Box(
        GEIGER_DC_OPENING_WIDTH,
        WALL + 3.0,
        GEIGER_DC_OPENING_HEIGHT,
    ).moved(
        Pos(
            GEIGER_DC_X,
            -OUTER_DEPTH / 2,
            GEIGER_DC_OPENING_CENTER_Z,
        )
    )
    base = base - dc_cut

    # A small side relief makes the friction-fit lid easy to lift.
    pry_notch = Box(5.0, 16.0, 6.0).moved(
        Pos(OUTER_WIDTH / 2, 0, BASE_HEIGHT - 1.5)
    )
    base = base - pry_notch

    base.label = "Enclosure base"
    base.color = Color(0.13, 0.20, 0.25)
    return base


def _logo_geometry(amount: float, z_offset: float):
    """Create the uRADMonitor-style wordmark and radiation symbol."""

    word = extrude(
        Text("uRADMonitor", font_size=10.0, font_path=FONT_BOLD),
        amount=amount,
    ).moved(Pos(8.0, 0.0, z_offset))
    symbol = extrude(
        Text("☢", font_size=17.0, font_path=FONT_SYMBOLS),
        amount=amount,
    ).moved(Pos(-38.5, 0.0, z_offset))
    # The visible face is printed against the bed and the finished lid is then
    # flipped around X. Pre-mirroring around XZ keeps the mark readable on the
    # assembled enclosure instead of mirrored vertically.
    return (word + symbol).mirror(Plane.XZ)


def _logo_cutter():
    """Create the slightly oversized recess cutter for the lid."""

    return _logo_geometry(LOGO_DEPTH + 0.05, -0.01)


def make_logo_inlay():
    """Create a separate black body that fits the recessed lid logo."""

    black = Color(0.02, 0.02, 0.02)
    glyphs = []
    for index, glyph in enumerate(
        _logo_geometry(LOGO_DEPTH, 0.0).solids(), start=1
    ):
        glyph.label = f"Black logo inlay {index:02d}"
        glyph.color = black
        glyphs.append(glyph)

    logo = Compound(children=glyphs)
    logo.label = "Black logo inlay"
    logo.color = black
    return logo


def make_lid_print_orientation():
    """Create the lid with its visible face on Z=0 for support-free printing."""

    panel = rounded_prism(OUTER_WIDTH, OUTER_DEPTH, LID_PANEL, CORNER_RADIUS)

    inner_width = OUTER_WIDTH - 2 * WALL
    inner_depth = OUTER_DEPTH - 2 * WALL
    lip_outer_width = inner_width - 2 * LID_CLEARANCE
    lip_outer_depth = inner_depth - 2 * LID_CLEARANCE
    lip_outer_radius = max(0.5, CORNER_RADIUS - WALL - LID_CLEARANCE)
    lip_inner_width = lip_outer_width - 2 * LID_LIP_WALL
    lip_inner_depth = lip_outer_depth - 2 * LID_LIP_WALL
    lip_inner_radius = max(0.5, lip_outer_radius - LID_LIP_WALL)

    lip_outer = rounded_prism(
        lip_outer_width,
        lip_outer_depth,
        LID_LIP_DEPTH,
        lip_outer_radius,
    ).moved(Pos(0, 0, LID_PANEL))
    lip_inner = rounded_prism(
        lip_inner_width,
        lip_inner_depth,
        LID_LIP_DEPTH + 0.2,
        lip_inner_radius,
    ).moved(Pos(0, 0, LID_PANEL - 0.1))
    lip = lip_outer - lip_inner

    lid = panel + lip
    # Subtract each disconnected glyph independently so every recessed letter
    # is represented by its own predictable OpenCascade boolean operation.
    for glyph in _logo_cutter().solids():
        lid = lid - glyph
    lid.label = "Recessed-logo lid"
    lid.color = Color(0.15, 0.28, 0.34)
    return lid


def make_geiger_proxy():
    """Return a conservative board/component envelope for fit review."""

    board_bottom = FLOOR + GEIGER_POST_HEIGHT
    board = Box(
        GEIGER_WIDTH,
        GEIGER_DEPTH,
        GEIGER_THICKNESS,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Pos(GEIGER_CENTER_X, GEIGER_CENTER_Y, board_bottom))
    board.label = "CAJOE RadiationD v1.1 PCB envelope"
    board.color = Color(0.05, 0.30, 0.65)

    components = Box(
        GEIGER_WIDTH - 5.0,
        GEIGER_DEPTH - 5.0,
        GEIGER_COMPONENT_ENVELOPE_HEIGHT,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(
        Pos(
            GEIGER_CENTER_X,
            GEIGER_CENTER_Y,
            board_bottom + GEIGER_THICKNESS,
        )
    )
    components.label = "Geiger component clearance envelope"
    components.color = Color(0.35, 0.62, 0.90, 0.35)
    return Compound(children=[board, components], label="Geiger board proxy")


def make_node_proxy():
    """Return the measured Wemos PCB and conservative clearance envelopes."""

    board_bottom = FLOOR + NODE_POST_HEIGHT
    board = Box(
        NODE_WIDTH,
        NODE_DEPTH,
        NODE_THICKNESS,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Pos(NODE_CENTER_X, NODE_CENTER_Y, board_bottom))
    board.label = "Wemos NodeMCU V3 58 x 25 mm PCB envelope"
    board.color = Color(0.08, 0.12, 0.14)

    # Leave the rear antenna zone free from the conservative component body.
    component_depth = NODE_DEPTH - NODE_ANTENNA_DEPTH - 3.0
    components = Box(
        NODE_WIDTH - 3.0,
        component_depth,
        NODE_COMPONENT_ENVELOPE_HEIGHT,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(
        Pos(
            NODE_CENTER_X,
            NODE_CENTER_Y - NODE_ANTENNA_DEPTH / 2,
            board_bottom + NODE_THICKNESS,
        )
    )
    components.label = "Wemos component clearance envelope"
    components.color = Color(0.22, 0.28, 0.30, 0.45)

    antenna = Box(
        NODE_WIDTH - 3.0,
        NODE_ANTENNA_DEPTH,
        1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(
        Pos(
            NODE_CENTER_X,
            NODE_CENTER_Y + (NODE_DEPTH - NODE_ANTENNA_DEPTH) / 2,
            board_bottom + NODE_THICKNESS,
        )
    )
    antenna.label = "ESP8266 antenna keep-out zone"
    antenna.color = Color(0.82, 0.63, 0.18, 0.75)
    return Compound(
        children=[board, components, antenna],
        label="Wemos NodeMCU V3 board proxy",
    )


def lid_in_assembled_position(lid=None):
    """Flip the print-oriented lid and place it on the enclosure."""

    if lid is None:
        lid = make_lid_print_orientation()
    return lid.moved(Pos(0, 0, BASE_HEIGHT + LID_PANEL) * Rot(180, 0, 0))


def make_fit_check_assembly():
    """Return the closed case plus conservative internal clearance bodies."""

    base = make_base()
    lid = lid_in_assembled_position()
    lid.label = "Lid in assembled position"
    return Compound(
        children=[base, make_geiger_proxy(), make_node_proxy(), lid],
        label="Geiger and Wemos NodeMCU enclosure fit check",
    )


def make_exploded_assembly():
    """Return an exploded assembly suited to a visual review render."""

    base = make_base()
    geiger = make_geiger_proxy()
    node = make_node_proxy()
    lid = lid_in_assembled_position()
    lid = lid.moved(Pos(0, 0, 28.0))
    lid.label = "Exploded recessed-logo lid"
    return Compound(
        children=[base, geiger, node, lid],
        label="Geiger and Wemos NodeMCU enclosure exploded",
    )
