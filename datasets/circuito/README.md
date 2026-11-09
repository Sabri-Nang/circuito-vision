# Dataset Circuito Vision

Dataset YOLO para detectar componentes de circuitos físicos en fotografías.

## Clases iniciales

| ID | Clase |
|---:|---|
| 0 | `arduino` |
| 1 | `breadboard` |
| 2 | `wire` |
| 3 | `resistor` |
| 4 | `led` |
| 5 | `sensor` |
| 6 | `button` |
| 7 | `power_supply` |

## Estructura

```text
datasets/circuito/
├── data.yaml
├── README.md
├── images/
│   ├── train/       # 80% de las fotos
│   └── val/         # 20% de las fotos
└── labels/
    ├── train/       # Un .txt por imagen de train
    └── val/         # Un .txt por imagen de val
```

## Formato de una etiqueta

Cada línea del archivo `.txt` representa un objeto:

```text
class_id center_x center_y width height
```

Las coordenadas deben estar normalizadas entre `0` y `1`. Por ejemplo:

```text
0 0.50 0.42 0.40 0.30
2 0.31 0.60 0.45 0.04
```

La primera línea marca un Arduino y la segunda un cable. Las coordenadas son
`x_center`, `y_center`, `width` y `height`, todas relativas al tamaño de la
imagen.

## Recomendaciones de captura

- Usar fotos reales de los montajes que queremos reconocer.
- Variar iluminación, ángulo, distancia, fondo y orientación.
- Mantener visibles los componentes y evitar fotos excesivamente borrosas.
- Incluir montajes con cables cruzados y componentes parcialmente ocultos.
- Comenzar con al menos 100 imágenes por clase; más datos mejoran la cobertura.
- Separar fotos similares entre `train` y `val` para evitar una evaluación
  artificialmente optimista.

## Flujo de etiquetado

1. Colocar las fotos en `images/train` o `images/val`.
2. Crear un archivo `.txt` con el mismo nombre base en la carpeta `labels`.
3. Dibujar una caja por cada componente visible.
4. Ejecutar el validador desde la raíz:

```powershell
uv run python scripts/validate_yolo_dataset.py
```

5. Entrenar un modelo inicial:

```powershell
uv run yolo detect train `
  model=yolo26n.pt `
  data=datasets/circuito/data.yaml `
  epochs=50 `
  imgsz=640
```

El dataset actual es un **esqueleto vacío**: antes de entrenar hay que agregar
fotos y sus anotaciones.
