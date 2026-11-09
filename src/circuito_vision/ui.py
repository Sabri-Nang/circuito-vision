"""Interfaz de usuario Gradio."""

import gradio as gr
from PIL import Image

from .diagram import render_diagram
from .vision import CircuitAnalyzer


def build_app() -> gr.Blocks:
    """Construye la interfaz Gradio sin iniciar el servidor."""
    analyzer = CircuitAnalyzer()

    def process_image(image: Image.Image | None) -> tuple[Image.Image | None, str]:
        if image is None:
            return None, "Subí una foto de una protoboard o circuito para analizarla."
        try:
            analysis = analyzer.analyze(image)
            return render_diagram(analysis), analysis.summary
        except (TypeError, ValueError, OSError) as error:
            return None, f"No se pudo analizar la imagen: {error}"

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
                output_text = gr.Markdown(label="Análisis")

        analyze_button.click(
            process_image,
            inputs=input_image,
            outputs=[output_diagram, output_text],
        )
        gr.Markdown(
            "**Próximas mejoras:** detección de componentes con YOLO, geometría de "
            "cables con MediaPipe y exportación a formatos de circuitos."
        )
    return app


def launch_app() -> None:
    """Inicia el servidor local de Gradio."""
    build_app().launch()
