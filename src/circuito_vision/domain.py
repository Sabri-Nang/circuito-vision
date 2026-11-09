"""Modelos de dominio independientes de Gradio y de la visión por computadora."""

from dataclasses import dataclass, field
from enum import StrEnum


class ComponentKind(StrEnum):
    """Tipos de componentes reconocibles por el MVP."""

    CONTROLLER = "controlador"
    BREADBOARD = "protoboard"
    WIRE = "cable"
    UNKNOWN = "elemento no identificado"


@dataclass(frozen=True, slots=True)
class DetectedComponent:
    """Componente detectado en una imagen."""

    kind: ComponentKind
    label: str
    confidence: float


@dataclass(frozen=True, slots=True)
class CircuitAnalysis:
    """Resultado de una interpretación visual orientativa."""

    components: tuple[DetectedComponent, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)
    warning: str = ""

    @property
    def summary(self) -> str:
        """Devuelve un resumen legible para la interfaz."""
        if not self.components:
            return "No se detectaron componentes con suficiente confianza."

        lines = ["Componentes detectados:"]
        lines.extend(
            f"- {component.label} ({component.confidence:.0%})"
            for component in self.components
        )
        if self.notes:
            lines.append("\nObservaciones:")
            lines.extend(f"- {note}" for note in self.notes)
        if self.warning:
            lines.append(f"\nAviso: {self.warning}")
        return "\n".join(lines)
