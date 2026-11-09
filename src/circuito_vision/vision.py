"""Análisis visual del MVP con YOLO y fallback heurístico."""

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
    """Detecta objetos sin inventar conexiones eléctricas."""

    def __init__(self, yolo_detector: YoloDetector | None = None) -> None:
        self.yolo_detector = yolo_detector

    def analyze(self, image: Image.Image) -> CircuitAnalysis:
        """Analiza una imagen y conserva las detecciones observables."""
        if image is None:
            raise ValueError("Se necesita una imagen para iniciar el análisis.")

        rgb_image = image.convert("RGB")
        pixels = np.asarray(rgb_image, dtype=np.uint8)
        components: list[DetectedComponent] = []
        notes: list[str] = []
        detections: tuple[ObjectDetection, ...] = ()

        if self.yolo_detector is not None:
            detections = self.yolo_detector.detect(rgb_image)
            if self.yolo_detector.error:
                notes.append(self.yolo_detector.error)
                self._add_heuristic_components(components, pixels)
                notes.append("Se activó el fallback visual por el error de YOLO.")
            elif detections:
                self._add_component_detections(components, detections)
                self._add_heuristic_components(components, pixels)
                notes.append(
                    "Las cajas representan objetos detectados; todavía no son "
                    "conexiones eléctricas ni un netlist."
                )
            else:
                self._add_heuristic_components(components, pixels)
                notes.append(
                    "YOLO no encontró objetos sobre el umbral; se agregó un "
                    "inventario visual orientativo."
                )
        else:
            self._add_heuristic_components(components, pixels)
            notes.append("Se utilizó el analizador visual de respaldo.")

        if not components:
            notes.append("No hay componentes identificados para construir un esquema.")
        notes.append("La orientación y el encuadre influyen en la detección.")
        return CircuitAnalysis(
            components=tuple(components),
            detections=detections,
            notes=tuple(notes),
            warning=(
                "No se infieren flechas ni conexiones: detectar la topología exige "
                "seguir cables y mapear pines con un modelo entrenado para circuitos."
            ),
        )

    @classmethod
    def _add_heuristic_components(
        cls,
        components: list[DetectedComponent],
        pixels: np.ndarray,
    ) -> None:
        """Agrega señales de respaldo, sin presentarlas como conexiones reales."""
        if cls._looks_like_breadboard(pixels):
            components.append(
                DetectedComponent(ComponentKind.BREADBOARD, "Protoboard posible", 0.45)
            )
        if cls._looks_like_controller(pixels):
            components.append(
                DetectedComponent(
                    ComponentKind.CONTROLLER,
                    "Microcontrolador posible",
                    0.40,
                )
            )
        if cls._looks_like_wires(pixels):
            components.append(
                DetectedComponent(ComponentKind.WIRE, "Cables posibles", 0.42)
            )
        if cls._looks_like_led(pixels):
            components.append(
                DetectedComponent(ComponentKind.UNKNOWN, "LED posible", 0.35)
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
                display_label = "Protoboard"
            elif any(
                word in label for word in ("arduino", "controller", "microcontroller")
            ):
                kind = ComponentKind.CONTROLLER
                display_label = "Arduino / microcontrolador"
            elif any(word in label for word in ("wire", "cable", "jumper")):
                kind = ComponentKind.WIRE
                display_label = "Cables de conexión"
            elif "power_supply" in label or "power supply" in label:
                kind = ComponentKind.POWER_SUPPLY
                display_label = "Fuente de alimentación"
            elif any(
                word in label
                for word in (
                    "resistor",
                    "capacitor",
                    "diode",
                    "led",
                    "ic",
                    "connector",
                    "button",
                    "switch",
                    "header",
                    "crystal",
                    "debug",
                )
            ):
                kind = ComponentKind.UNKNOWN
                display_label = CircuitAnalyzer._human_component_label(label)
            else:
                continue
            components.append(
                DetectedComponent(kind, display_label, detection.confidence)
            )

    @staticmethod
    def _human_component_label(label: str) -> str:
        """Normaliza etiquetas YOLO para la lista visible del usuario."""
        names = {
            "resistor": "Resistencia",
            "capacitor": "Capacitor",
            "diode": "Diodo",
            "led": "LED",
            "button": "Botón",
            "switch": "Interruptor",
            "ic": "Circuito integrado",
            "connector": "Conector",
            "header": "Header de pines",
            "crystal": "Cristal oscilador",
        }
        return names.get(label, label)

    @staticmethod
    def _looks_like_breadboard(pixels: np.ndarray) -> bool:
        """Busca una proporción relevante de zonas claras."""
        bright = np.all(pixels > 175, axis=2)
        return float(bright.mean()) > 0.18

    @staticmethod
    def _looks_like_controller(pixels: np.ndarray) -> bool:
        """Busca superficies oscuras con contraste."""
        dark = np.all(pixels < 90, axis=2)
        return float(dark.mean()) > 0.025

    @staticmethod
    def _looks_like_wires(pixels: np.ndarray) -> bool:
        """Busca píxeles saturados que pueden corresponder a cables."""
        maximum = pixels.max(axis=2).astype(np.int16)
        minimum = pixels.min(axis=2).astype(np.int16)
        saturated = (maximum - minimum) > 70
        return float(saturated.mean()) > 0.04

    @staticmethod
    def _looks_like_led(pixels: np.ndarray) -> bool:
        """Detecta una señal débil de LEDs por colores intensos."""
        red = (pixels[:, :, 0] > 170) & (pixels[:, :, 1] < 130)
        green = (pixels[:, :, 1] > 150) & (pixels[:, :, 0] < 150)
        return float((red | green).mean()) > 0.003
