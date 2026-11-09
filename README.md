# Circuito Vision

MVP de una aplicación en Gradio que recibe una fotografía de una protoboard,
cables y un microcontrolador, y devuelve un esquema eléctrico **orientativo**.

> La primera versión no valida continuidad, polaridad, voltajes ni el netlist
> real del circuito. Su objetivo es probar el flujo de producto y preparar una
> arquitectura donde luego puedan incorporarse modelos de visión más capaces.

## 1. Qué resuelve el MVP

El usuario puede:

1. Abrir una interfaz web local.
2. Subir una imagen o capturarla con la webcam.
3. Solicitar un análisis visual.
4. Ver un diagrama generado y un resumen de señales detectadas.

El analizador actual usa heurísticas livianas sobre la imagen para detectar
señales compatibles con una protoboard, un controlador y cables. Las interfaces
de dominio están separadas del framework Gradio para que el analizador pueda
ser reemplazado por YOLO, MediaPipe o un modelo multimodal sin rediseñar la UI.

### Arquitectura

```text
Imagen del usuario
       |
       v
  ui.py / Gradio
       |
       v
  vision.py ------> CircuitAnalysis (domain.py)
       |                         |
       v                         v
  diagram.py             resumen para el usuario
       |
       v
  Imagen del esquema
```

## 2. Roadmap y milestones

### Fase 1: MVP Core — estado actual

- [x] Proyecto Python 3.12 con `src/` layout.
- [x] Interfaz Gradio para upload y webcam.
- [x] Analizador visual desacoplado de la interfaz.
- [x] Resultado gráfico y resumen textual.
- [x] Manejo de errores de entrada.
- [x] Pruebas unitarias básicas.

### Fase 2: Refinamiento & Testing

- [ ] Crear dataset etiquetado de fotos de protoboards.
- [ ] Sustituir heurísticas por detección de componentes con YOLO.
- [ ] Usar MediaPipe u otro método geométrico para seguir cables.
- [ ] Agregar pruebas con imágenes reales y casos de mala iluminación.
- [ ] Ejecutar `pytest` y `ruff` en cada cambio.
- [ ] Medir precisión por componente y tasa de falsos positivos.

### Fase 3: Scaling & Production-Ready

- [ ] Separar API de inferencia y frontend si el uso crece.
- [ ] Incorporar procesamiento asíncrono y límites de tamaño.
- [ ] Versionar modelos y registrar métricas de inferencia.
- [ ] Agregar CI/CD, Docker y despliegue.
- [ ] Exportar a SVG, Mermaid, KiCad o Fritzing cuando el modelo produzca un
      netlist confiable.
- [ ] Evaluar modelos multimodales y trabajos de Memo Akten como referencia
      conceptual para interacción y visualización, no como dependencia obligatoria.

## 3. Quickstart con `uv`

### Desde cero

```powershell
uv init --python 3.12
uv venv --python 3.12
uv add "gradio>=5.49.0,<6.0.0" "numpy>=2.1.0,<3.0.0" "pillow>=11.0.0,<12.0.0"
uv add --dev "pytest>=8.3.0,<9.0.0" "ruff>=0.8.0,<1.0.0"
uv sync
```

En este repositorio el `pyproject.toml` y el código ya están preparados, por lo
que normalmente alcanza con:

```powershell
uv venv --python 3.12
uv sync --extra dev
uv run circuito-vision
```

También se puede iniciar con:

```powershell
uv run python -m circuito_vision.main
```

Gradio mostrará una URL local en la terminal. Abrila en el navegador, cargá una
foto y presioná **Generar esquema**.

### Verificación local

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## 4. Estructura de directorios

```text
circuito_vision/
├── pyproject.toml                 # Metadata, dependencias y comandos
├── README.md                      # Documentación y roadmap
├── src/
│   └── circuito_vision/
│       ├── __init__.py            # Versión del paquete
│       ├── main.py                # Punto de entrada
│       ├── ui.py                  # Interfaz Gradio y eventos
│       ├── domain.py              # Entidades y resultado de dominio
│       ├── vision.py              # Analizador visual reemplazable
│       └── diagram.py             # Render del esquema orientativo
└── tests/
    └── test_vision.py             # Pruebas unitarias iniciales
```

## 5. Decisiones y límites conocidos

- El output es un esquema de comunicación visual, no un plano eléctrico
  certificado.
- Una foto 2D puede ocultar conexiones, pines y cruces de cables; para lograr
  un netlist real se necesitarán mejores datos de entrada o varias vistas.
- `uv` es el único gestor de paquetes y entorno utilizado por el proyecto.
- YOLO y MediaPipe se mantienen como extensiones futuras porque agregarlos al
  primer arranque aumentaría considerablemente el tamaño y la complejidad del
  MVP.
