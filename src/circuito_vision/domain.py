"""Modelos de dominio independientes de Gradio y de la visión."""

from dataclasses import dataclass, field
from enum import StrEnum


class ComponentKind(StrEnum):
    """Tipos de componentes reconocibles por el MVP."""

    CONTROLLER = "controlador"
    BREADBOARD = "protoboard"
    WIRE = "cable"
    POWER_SUPPLY = "fuente de alimentación"
    UNKNOWN = "elemento no identificado"


@dataclass(frozen=True, slots=True)
class DetectedComponent:
    """Componente detectado en una imagen."""

    kind: ComponentKind
    label: str
    confidence: float


@dataclass(frozen=True, slots=True)
class ObjectDetection:
    """Detección cruda producida por un detector de objetos."""

    label: str
    confidence: float
    box: tuple[float, float, float, float]
    detector: str = "YOLO"


@dataclass(frozen=True, slots=True)
class CircuitAnalysis:
    """Resultado de una interpretación visual orientativa."""

    components: tuple[DetectedComponent, ...] = field(default_factory=tuple)
    detections: tuple[ObjectDetection, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)
    warning: str = ""

    @property
    def summary(self) -> str:
        """Devuelve un resumen legible para la interfaz."""
        lines: list[str] = []
        if self.components:
            lines.append("Componentes detectados:")
            lines.extend(
                f"- {component.label} ({component.confidence:.0%})"
                for component in self.components
            )
        else:
            lines.append("No se detectaron componentes con suficiente confianza.")
        if self.notes:
            lines.append("\nObservaciones:")
            lines.extend(f"- {note}" for note in self.notes)
        if self.detections:
            lines.append("\nDetecciones YOLO:")
            lines.extend(
                f"- {detection.label} ({detection.confidence:.0%})"
                for detection in self.detections
            )
        if self.warning:
            lines.append(f"\nAviso: {self.warning}")
        return "\n".join(lines)
