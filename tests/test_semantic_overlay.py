"""Tests for the semantic overlay helper functions in the renderer."""

from tmviz.ui import theme
from tmviz.ui.renderer import (
    _integrity_color,
    _office_color,
    _parse_compiled_state,
    _ternary_symbol_color,
)


def test_parse_compiled_state_normal():
    assert _parse_compiled_state("generator__seed") == ("generator", "seed")
    assert _parse_compiled_state("arbiter__life") == ("arbiter", "life")
    assert _parse_compiled_state("critic__death") == ("critic", "death")


def test_parse_compiled_state_no_separator():
    assert _parse_compiled_state("q0") == ("q0", "")
    assert _parse_compiled_state("halt") == ("halt", "")


def test_ternary_symbol_colors():
    assert _ternary_symbol_color("+1", False) == theme.TERNARY_POS
    assert _ternary_symbol_color("-1", False) == theme.TERNARY_NEG
    assert _ternary_symbol_color("0", False) == theme.TERNARY_ZERO
    assert _ternary_symbol_color("_", False) == theme.TERNARY_BLANK


def test_ternary_symbol_head_colors():
    # head +1 and -1 are semantic; head 0 is cyan
    assert _ternary_symbol_color("+1", True) == theme.TERNARY_POS
    assert _ternary_symbol_color("-1", True) == theme.TERNARY_NEG
    assert _ternary_symbol_color("0", True) == theme.CYAN


def test_office_colors():
    assert _office_color("generator") == theme.OFFICE_GENERATOR
    assert _office_color("arbiter") == theme.OFFICE_ARBITER
    assert _office_color("critic") == theme.OFFICE_CRITIC
    assert _office_color("unknown") == theme.TEXT


def test_integrity_colors():
    assert _integrity_color("life") == theme.INTEGRITY_LIFE
    assert _integrity_color("seed") == theme.INTEGRITY_SEED
    assert _integrity_color("death") == theme.INTEGRITY_DEATH
    assert _integrity_color("") == theme.TEXT
