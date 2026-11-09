"""Importa un dataset YOLO externo al esquema de Circuito Vision."""

import argparse
import hashlib
import shutil
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
CLASS_MAP = {
    "0": 3,  # Resistor -> resistor
    "1": 8,  # Capacitor -> capacitor
    "2": 9,  # Diode -> diode
    "3": 4,  # LED -> led
    "4": 10,  # IC -> ic
    "5": 11,  # Connector -> connector
    "6": 6,  # Switch/Button -> button
    "7": 12,  # Header -> header
    "8": 13,  # Crystal -> crystal
    "9": 14,  # Debug/TP -> debug_tp
}


def parse_args() -> argparse.Namespace:
    """Parsea los argumentos del importador."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument(
        "--target",
        type=Path,
        default=Path("datasets/circuito"),
    )
    return parser.parse_args()


def find_split_images(source: Path, split: str) -> list[Path]:
    """Encuentra imágenes de un split YOLO."""
    image_dir = source / "images" / split
    return sorted(
        path for path in image_dir.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES
    )


def import_split(source: Path, target: Path, split: str) -> int:
    """Importa un split y devuelve la cantidad de imágenes copiadas."""
    source_images = find_split_images(source, split)
    source_labels = source / "labels" / split
    target_images = target / "images" / split
    target_labels = target / "labels" / split
    target_images.mkdir(parents=True, exist_ok=True)
    target_labels.mkdir(parents=True, exist_ok=True)

    imported = 0
    for image_path in source_images:
        label_path = source_labels / f"{image_path.stem}.txt"
        if not label_path.exists():
            print(f"Omitida sin etiqueta: {image_path}")
            continue
        digest = hashlib.sha1(str(image_path).encode()).hexdigest()[:10]
        output_stem = f"pcb_{split}_{image_path.stem}_{digest}"
        output_image = target_images / f"{output_stem}{image_path.suffix.lower()}"
        shutil.copy2(image_path, output_image)
        output_label = target_labels / f"{output_stem}.txt"
        remap_labels(label_path, output_label)
        imported += 1
    return imported


def remap_labels(source: Path, target: Path) -> None:
    """Remapea IDs externos al esquema del proyecto."""
    lines: list[str] = []
    for line_number, line in enumerate(source.read_text().splitlines(), 1):
        fields = line.split()
        if len(fields) != 5 or fields[0] not in CLASS_MAP:
            raise ValueError(f"Etiqueta inválida en {source}:{line_number}")
        fields[0] = str(CLASS_MAP[fields[0]])
        lines.append(" ".join(fields))
    target.write_text("\n".join(lines) + ("\n" if lines else ""))


def main() -> int:
    """Ejecuta la importación de train y val."""
    args = parse_args()
    if not (args.source / "images").exists():
        raise SystemExit(f"No existe una estructura YOLO en {args.source}")
    counts = {
        split: import_split(args.source, args.target, split)
        for split in ("train", "val")
    }
    print(f"Importación completada: train={counts['train']}, val={counts['val']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
