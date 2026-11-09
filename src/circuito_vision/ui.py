"""Interfaz de usuario Gradio."""

import gradio as gr
from PIL import Image

from .diagram import render_diagram
from .vision import CircuitAnalyzer
from .yolo_detector import YoloDetector


def build_app() -> gr.Blocks:
    """Construye la interfaz Gradio sin iniciar el servidor."""
    analyzer = CircuitAnalyzer(yolo_detector=YoloDetector())

    def process_image(
        image: Image.Image | None,
    ) -> tuple[Image.Image | None, str, str]:
        if image is None:
            message = "Subí una foto de una protoboard o circuito para analizarla."
            return None, message, message
        try:
            analysis = analyzer.analyze(image)
            component_list = _component_list(analysis.summary)
            return render_diagram(image, analysis), component_list, analysis.summary
        except (TypeError, ValueError, OSError) as error:
            message = f"No se pudo analizar la imagen: {error}"
            return None, message, message

    with gr.Blocks(title="Circuito Vision") as app:
        gr.Markdown(
            """
            # Circuito Vision
            Subí una foto de un circuito físico y obtené un esquema eléctrico
            **orientativo**. El resultado no reemplaza la verificación manual.
            """
        )
        with gr.Row():
            with gr.Column():
                input_image = gr.Image(
                    label="Foto del circuito",
                    type="pil",
                    sources=["upload", "webcam"],
                )
                analyze_button = gr.Button("Generar esquema", variant="primary")
            with gr.Column():
                output_diagram = gr.Image(label="Esquema generado", type="pil")
                component_output = gr.Markdown(label="Componentes detectados")
                output_text = gr.Markdown(label="Análisis")

        analyze_button.click(
            process_image,
            inputs=input_image,
            outputs=[output_diagram, component_output, output_text],
        )
        gr.Markdown(
            "**Pipeline actual:** YOLO entrenado + heurísticas de respaldo. "
            "**Próximas mejoras:** más fotos etiquetadas, geometría de "
            "cables con MediaPipe y exportación a formatos de circuitos."
        )
    return app


def _component_list(summary: str) -> str:
    """Extrae y presenta primero la lista de componentes detectados."""
    marker = "\n\nObservaciones:"
    component_section = summary.split(marker, maxsplit=1)[0]
    return f"### Componentes detectados\n\n{component_section}"


def launch_app() -> None:
    """Inicia el servidor local de Gradio."""
    build_app().launch()
