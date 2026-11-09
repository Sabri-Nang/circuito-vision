"""Analizador visual base y heurísticas del MVP."""

import numpy as np
from PIL import Image

from .domain import CircuitAnalysis, ComponentKind, DetectedComponent


class CircuitAnalyzer:
    """Detecta señales visuales simples sin afirmar conexiones eléctricas."""

    def analyze(self, image: Image.Image) -> CircuitAnalysis:
        """Analiza una imagen RGB y devuelve componentes orientativos."""
        if image is None:
            raise ValueError("Se necesita una imagen para iniciar el análisis.")

        rgb_image = image.convert("RGB")
        pixels = np.asarray(rgb_image, dtype=np.uint8)
        components: list[DetectedComponent] = []
        notes: list[str] = []

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

        if not components:
            notes.append(
                "La foto no presenta señales claras para las heurísticas del MVP."
            )
        notes.append("La orientación y el encuadre influyen en la detección.")
        return CircuitAnalysis(
            components=tuple(components),
            notes=tuple(notes),
            warning=(
                "El esquema es orientativo: no reemplaza una revisión eléctrica "
                "ni garantiza que las conexiones reales sean correctas."
            ),
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
