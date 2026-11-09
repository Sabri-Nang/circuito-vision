"""Renderizado de evidencia visual, sin conexiones inventadas."""

from PIL import Image, ImageDraw, ImageFont

from .domain import CircuitAnalysis


def render_diagram(image: Image.Image, analysis: CircuitAnalysis) -> Image.Image:
    """Muestra la foto y las cajas reales detectadas por YOLO."""
    source = image.convert("RGB")
    source.thumbnail((760, 620))
    canvas = Image.new("RGB", (1180, 700), "white")
    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.load_default(size=24)
    body_font = ImageFont.load_default(size=18)
    small_font = ImageFont.load_default(size=15)

    draw.text((24, 20), "Mapa visual del circuito", fill="#16213e", font=title_font)
    draw.text(
        (24, 52),
        "Las cajas provienen de detecciones; no se dibujan conexiones inventadas.",
        fill="#8a3b12",
        font=small_font,
    )

    image_left, image_top = 24, 88
    canvas.paste(source, (image_left, image_top))
    image_width, image_height = source.size
    draw.rectangle(
        (
            image_left,
            image_top,
            image_left + image_width,
            image_top + image_height,
        ),
        outline="#64748b",
        width=2,
    )

    original_width, original_height = image.size
    scale_x = image_width / original_width
    scale_y = image_height / original_height
    colors = ["#dc2626", "#2563eb", "#16a34a", "#ca8a04"]
    for index, detection in enumerate(analysis.detections):
        left, top, right, bottom = detection.box
        box = (
            image_left + left * scale_x,
            image_top + top * scale_y,
            image_left + right * scale_x,
            image_top + bottom * scale_y,
        )
        color = colors[index % len(colors)]
        draw.rectangle(box, outline=color, width=3)
        draw.text(
            (box[0], max(image_top, box[1] - 20)),
            f"{detection.label} {detection.confidence:.0%}",
            fill=color,
            font=small_font,
        )

    panel_left = 820
    draw.rounded_rectangle(
        (panel_left, 88, 1150, 620),
        radius=14,
        fill="#f8fafc",
        outline="#cbd5e1",
        width=2,
    )
    draw.text((panel_left + 20, 115), "Observaciones", fill="#16213e", font=body_font)
    y = 155
    for note in analysis.notes:
        for line in _wrap(note, 35):
            draw.text(
                (panel_left + 20, y),
                f"• {line}",
                fill="#334155",
                font=small_font,
            )
            y += 22
        y += 8

    draw.text(
        (panel_left + 20, 490),
        "Próximo paso",
        fill="#16213e",
        font=body_font,
    )
    for offset, line in enumerate(
        _wrap("Entrenar pesos propios y seguir cables para producir un netlist.", 35)
    ):
        draw.text(
            (panel_left + 20, 530 + offset * 22),
            line,
            fill="#475569",
            font=small_font,
        )
    return canvas


def _wrap(text: str, width: int) -> list[str]:
    """Divide texto simple para el panel de la imagen."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines
