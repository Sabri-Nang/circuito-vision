"""Renderizado del esquema orientativo del circuito."""

from PIL import Image, ImageDraw, ImageFont

from .domain import CircuitAnalysis, ComponentKind


def render_diagram(analysis: CircuitAnalysis) -> Image.Image:
    """Crea una imagen PNG con los componentes reconocidos y sus enlaces."""
    canvas = Image.new("RGB", (1100, 650), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=22)
    small_font = ImageFont.load_default(size=17)

    draw.text((40, 30), "Esquema eléctrico orientativo", fill="#16213e", font=font)
    draw.text(
        (40, 70),
        "Generado a partir de una fotografía; revisar antes de cablear.",
        fill="#8a3b12",
        font=small_font,
    )

    detected = {component.kind for component in analysis.components}
    boxes = []
    if ComponentKind.CONTROLLER in detected:
        boxes.append(("Controlador", (90, 230, 350, 390), "#dbeafe"))
    if ComponentKind.BREADBOARD in detected:
        boxes.append(("Protoboard", (740, 205, 1010, 415), "#dcfce7"))
    if ComponentKind.WIRE in detected:
        boxes.append(("Cables", (430, 275, 650, 345), "#fef3c7"))

    if not boxes:
        boxes.append(("Sin componentes claros", (370, 250, 730, 370), "#f3f4f6"))

    for label, (left, top, right, bottom), color in boxes:
        draw.rounded_rectangle(
            (left, top, right, bottom),
            radius=18,
            fill=color,
            outline="#334155",
            width=3,
        )
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        draw.text(
            ((left + right - text_width) / 2, (top + bottom - text_height) / 2),
            label,
            fill="#172033",
            font=font,
        )

    if len(boxes) > 1:
        draw.line((350, 310, 740, 310), fill="#dc2626", width=5)
        draw.polygon(((730, 300), (750, 310), (730, 320)), fill="#dc2626")
        draw.text((475, 240), "conexión inferida", fill="#991b1b", font=small_font)

    draw.text(
        (40, 575),
        "MVP: conexión visual inferida, no netlist ni validación de voltajes.",
        fill="#475569",
        font=small_font,
    )
    return canvas
