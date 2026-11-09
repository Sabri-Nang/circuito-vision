"""Valida estructura y anotaciones de un dataset YOLO de detección."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "datasets" / "circuito"
CLASS_COUNT = 8
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def validate_split(split: str) -> list[str]:
    """Valida imágenes y etiquetas de un split y devuelve errores."""
    errors: list[str] = []
    image_dir = ROOT / "images" / split
    label_dir = ROOT / "labels" / split
    images = [
        path for path in image_dir.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES
    ]

    for image_path in images:
        label_path = label_dir / f"{image_path.stem}.txt"
        if not label_path.exists():
            errors.append(f"Falta etiqueta para {image_path}")
            continue
        for line_number, line in enumerate(label_path.read_text().splitlines(), 1):
            fields = line.split()
            if len(fields) != 5:
                errors.append(f"{label_path}:{line_number}: se esperan 5 valores")
                continue
            try:
                class_id, *coordinates = map(float, fields)
            except ValueError:
                errors.append(f"{label_path}:{line_number}: valores no numéricos")
                continue
            if not class_id.is_integer() or not 0 <= class_id < CLASS_COUNT:
                errors.append(f"{label_path}:{line_number}: clase fuera de rango")
            if any(not 0 <= value <= 1 for value in coordinates):
                errors.append(f"{label_path}:{line_number}: coordenada fuera de [0, 1]")
    return errors


def main() -> int:
    """Ejecuta la validación y devuelve un código de salida de shell."""
    errors: list[str] = []
    for required in (
        ROOT / "data.yaml",
        ROOT / "images" / "train",
        ROOT / "images" / "val",
        ROOT / "labels" / "train",
        ROOT / "labels" / "val",
    ):
        if not required.exists():
            errors.append(f"No existe {required}")
    if not errors:
        errors.extend(validate_split("train"))
        errors.extend(validate_split("val"))

    if errors:
        print("Dataset inválido:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"Dataset válido: {ROOT}")
    print("No se encontraron imágenes; agregá fotos y etiquetas antes de entrenar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
