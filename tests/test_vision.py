"""Pruebas unitarias del analizador visual."""

import numpy as np
from PIL import Image

from circuito_vision.vision import CircuitAnalyzer


def test_analyzer_returns_warning_for_any_valid_image() -> None:
    image = Image.fromarray(np.full((20, 20, 3), 220, dtype=np.uint8))

    result = CircuitAnalyzer().analyze(image)

    assert result.warning
    assert result.components


def test_analyzer_rejects_missing_image() -> None:
    try:
        CircuitAnalyzer().analyze(None)  # type: ignore[arg-type]
    except ValueError as error:
        assert "imagen" in str(error)
    else:
        raise AssertionError("Se esperaba un ValueError")
