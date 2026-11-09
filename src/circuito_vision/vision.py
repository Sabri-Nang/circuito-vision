"""Analizador visual base del MVP.

Este módulo no carga modelos entrenados: aplica reglas deterministas de brillo
y saturación sobre los píxeles de la imagen. La clase está aislada para poder
reemplazarla luego por un adaptador de YOLO, MediaPipe o un modelo multimodal.
"""

import numpy as np
from PIL import Image

from .domain import (
    CircuitAnalysis,
    ComponentKind,
    DetectedComponent,
    ObjectDetection,
)
from .yolo_detector import YoloDetector


class CircuitAnalyzer:
    """Detecta señales visuales simples sin afirmar conexiones eléctricas."""

    def __init__(self, yolo_detector: YoloDetector | None = None) -> None:
        self.yolo_detector = yolo_detector

    def analyze(self, image: Image.Image) -> CircuitAnalysis:
        """Analiza una imagen RGB y devuelve componentes orientativos."""
        if image is None:
            raise ValueError("Se necesita una imagen para iniciar el análisis.")

        rgb_image = image.convert("RGB")
        pixels = np.asarray(rgb_image, dtype=np.uint8)
        components: list[DetectedComponent] = []
        notes: list[str] = []
        detections: tuple[ObjectDetection, ...] = ()

        if self._looks_like_breadboard(pixels):
            components.append(
                DetectedComponent(ComponentKind.BREADBOARD, "Protoboard", 0.72)
            )
        if self._looks_like_controller(pixels):
            components.append(
                DetectedComponent(
                    ComponentKind.CONTROLLER,
                    "Microcontrolador compatible con Arduino (posible)",
                    0.58,
                )
            )
        if self._looks_like_wires(pixels):
            components.append(
                DetectedComponent(ComponentKind.WIRE, "Cables de conexión", 0.64)
            )

        if self.yolo_detector is not None:
            detections = self.yolo_detector.detect(rgb_image)
            self._add_component_detections(components, detections)
            if self.yolo_detector.error:
                notes.append(self.yolo_detector.error)
            elif detections:
                notes.append(
                    "YOLO detectó objetos genéricos; se requieren pesos propios "
                    "para reconocer componentes eléctricos con precisión."
                )
            else:
                notes.append("YOLO no encontró objetos sobre el umbral de confianza.")

        if not components:
            notes.append(
                "La foto no presenta señales claras para las heurísticas del MVP."
            )
        notes.append("La orientación y el encuadre influyen en la detección.")
        return CircuitAnalysis(
            components=tuple(components),
            detections=detections,
            notes=tuple(notes),
            warning=(
                "El esquema es orientativo: no reemplaza una revisión eléctrica "
                "ni garantiza que las conexiones reales sean correctas."
            ),
        )

    @staticmethod
    def _add_component_detections(
        components: list[DetectedComponent],
        detections: tuple[ObjectDetection, ...],
    ) -> None:
        """Convierte etiquetas de un modelo propio en componentes de dominio."""
        for detection in detections:
            label = detection.label.lower()
            if "breadboard" in label or "protoboard" in label:
                kind = ComponentKind.BREADBOARD
            elif any(
                word in label for word in ("arduino", "controller", "microcontroller")
            ):
                kind = ComponentKind.CONTROLLER
            elif any(word in label for word in ("wire", "cable", "jumper")):
                kind = ComponentKind.WIRE
            else:
                continue
            components.append(
                DetectedComponent(kind, detection.label, detection.confidence)
            )

    @staticmethod
    def _looks_like_breadboard(pixels: np.ndarray) -> bool:
        """Busca una proporción relevante de zonas claras y alargadas."""
        bright = np.all(pixels > 175, axis=2)
        return float(bright.mean()) > 0.18

    @staticmethod
    def _looks_like_controller(pixels: np.ndarray) -> bool:
        """Busca superficies oscuras con componentes de alto contraste."""
        dark = np.all(pixels < 90, axis=2)
        return float(dark.mean()) > 0.025

    @staticmethod
    def _looks_like_wires(pixels: np.ndarray) -> bool:
        """Busca píxeles saturados que suelen corresponder a jumpers."""
        maximum = pixels.max(axis=2).astype(np.int16)
        minimum = pixels.min(axis=2).astype(np.int16)
        saturated = (maximum - minimum) > 70
        return float(saturated.mean()) > 0.04
