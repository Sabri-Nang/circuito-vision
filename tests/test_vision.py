"""Pruebas unitarias del analizador visual."""

import numpy as np
from PIL import Image

from circuito_vision.domain import ObjectDetection
from circuito_vision.vision import CircuitAnalyzer


class FakeYoloDetector:
    """Detector controlado para probar la integración sin descargar pesos."""

    error = None

    def detect(self, image: Image.Image) -> tuple[ObjectDetection, ...]:
        return (ObjectDetection("arduino", 0.91, (1.0, 2.0, 10.0, 20.0)),)


class EmptyYoloDetector(FakeYoloDetector):
    """Detector que no encuentra objetos."""

    def detect(self, image: Image.Image) -> tuple[ObjectDetection, ...]:
        return ()


class ElectronicComponentDetector(FakeYoloDetector):
    """Detector controlado que devuelve un componente electrónico."""

    def detect(self, image: Image.Image) -> tuple[ObjectDetection, ...]:
        return (ObjectDetection("resistor", 0.87, (1.0, 2.0, 10.0, 20.0)),)


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


def test_analyzer_includes_yolo_component_detection() -> None:
    image = Image.fromarray(np.full((20, 20, 3), 220, dtype=np.uint8))

    result = CircuitAnalyzer(yolo_detector=FakeYoloDetector()).analyze(image)

    assert result.detections[0].label == "arduino"
    assert any("arduino" in component.label for component in result.components)


def test_yolo_without_detections_does_not_invent_components() -> None:
    image = Image.fromarray(np.full((20, 20, 3), 220, dtype=np.uint8))

    result = CircuitAnalyzer(yolo_detector=EmptyYoloDetector()).analyze(image)

    assert result.detections == ()
    assert result.components == ()
    assert "no encontr" in result.summary.lower()


def test_electronic_yolo_detection_is_listed_as_component() -> None:
    image = Image.fromarray(np.full((20, 20, 3), 220, dtype=np.uint8))

    result = CircuitAnalyzer(yolo_detector=ElectronicComponentDetector()).analyze(image)

    assert result.components[0].label == "resistor"
    assert "resistor" in result.summary.lower()
