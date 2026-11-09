"""Adaptador opcional para inferencia con Ultralytics YOLO."""

import os
from pathlib import Path
from typing import Any

from PIL import Image

from .domain import ObjectDetection


class YoloDetector:
    """Ejecuta YOLO bajo demanda y tolera instalaciones incompletas.

    ``model_path`` puede ser un nombre oficial, como ``yolo26n.pt``, o una ruta
    a pesos entrenados con clases de circuitos. Ultralytics descarga los pesos
    oficiales la primera vez que se utilizan.
    """

    def __init__(
        self,
        model_path: str | None = None,
        confidence: float = 0.25,
    ) -> None:
        self.model_path = model_path or os.getenv("CIRCUITO_YOLO_MODEL", "yolo26n.pt")
        self.confidence = confidence
        self._model: Any | None = None
        self._error: str | None = None

    @property
    def available(self) -> bool:
        """Indica si el adaptador puede importar Ultralytics."""
        try:
            from ultralytics import YOLO  # noqa: F401
        except ImportError:
            return False
        return True

    @property
    def error(self) -> str | None:
        """Devuelve el último error no fatal del detector."""
        return self._error

    def detect(self, image: Image.Image) -> tuple[ObjectDetection, ...]:
        """Detecta objetos en una imagen PIL sin detener la aplicación."""
        try:
            model = self._load_model()
            results = model.predict(source=image, conf=self.confidence, verbose=False)
            return self._parse_results(results)
        except (ImportError, OSError, RuntimeError, TypeError, ValueError) as error:
            self._error = f"YOLO no pudo ejecutarse: {error}"
            return ()

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model

        from ultralytics import YOLO

        model_path = Path(self.model_path)
        if model_path.suffix == ".pt" and model_path.parent != Path("."):
            if not model_path.exists():
                raise FileNotFoundError(f"No existe el modelo YOLO: {model_path}")
        self._model = YOLO(self.model_path)
        return self._model

    def _parse_results(self, results: list[Any]) -> tuple[ObjectDetection, ...]:
        detections: list[ObjectDetection] = []
        for result in results:
            names = result.names
            boxes = result.boxes
            for index in range(len(boxes)):
                class_id = int(boxes.cls[index].item())
                confidence = float(boxes.conf[index].item())
                coordinates = tuple(
                    float(value) for value in boxes.xyxy[index].tolist()
                )
                detections.append(
                    ObjectDetection(
                        label=str(names[class_id]),
                        confidence=confidence,
                        box=coordinates,
                    )
                )
        return tuple(detections)
