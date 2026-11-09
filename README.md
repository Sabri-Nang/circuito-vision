# Circuito Vision

MVP de una aplicación en Gradio que recibe una fotografía de una protoboard,
cables y un microcontrolador, y devuelve un esquema eléctrico **orientativo**.

## Estado actual

El proyecto está en la **Fase 1: MVP Core** y se puede ejecutar localmente.
El flujo completo disponible es:

1. Abrir una interfaz web local con Gradio.
2. Subir una imagen o capturarla con la webcam.
3. Analizar señales visuales básicas.
4. Mostrar un esquema generado y un resumen textual.

El resultado sirve para validar la idea de producto y la experiencia de uso.
Todavía no reconstruye un circuito eléctrico real ni garantiza que el cableado
de la fotografía sea correcto.

## ¿Qué modelos utiliza?

### Modelo usado actualmente

La aplicación utiliza ahora un **pipeline híbrido**:

1. YOLO ejecuta detección de objetos cuando está instalado el extra `yolo`.
2. Las heurísticas de [vision.py](src/circuito_vision/vision.py) funcionan como
   respaldo y producen señales visuales básicas.

El adaptador de YOLO está en [yolo_detector.py](src/circuito_vision/yolo_detector.py)
y carga por defecto `yolo26n.pt`, un modelo oficial pequeño de Ultralytics. El
archivo de pesos se descarga automáticamente durante la primera inferencia y
no se sube al repositorio. La configuración de Ultralytics se guarda en la
carpeta local `.ultralytics/` para evitar depender de permisos de
`AppData\\Roaming` en Windows.

Las heurísticas deterministas basadas en NumPy y Pillow hacen lo siguiente:

- **Protoboard:** calcula la proporción de píxeles claros. Si supera un umbral,
  agrega una detección orientativa de protoboard.
- **Controlador:** calcula la proporción de píxeles oscuros. Si supera un
  umbral, agrega una posible detección de microcontrolador.
- **Cables:** calcula la proporción de píxeles saturados, es decir, con una
  diferencia alta entre el canal de color más claro y el más oscuro.
- **Esquema:** [diagram.py](src/circuito_vision/diagram.py) dibuja cajas y una
  conexión visual inferida a partir de esas detecciones.

Las detecciones YOLO muestran la confianza producida por el modelo. Las
confianzas de protoboard, controlador y cables generadas por las heurísticas son
valores fijos orientativos, no probabilidades aprendidas por una red neuronal.

Para utilizar un modelo propio entrenado con componentes eléctricos:

```powershell
$env:CIRCUITO_YOLO_MODEL = "models/circuito_yolo.pt"
uv run circuito-vision
```

Las etiquetas `arduino`, `controller`, `microcontroller`, `breadboard`,
`protoboard`, `wire`, `cable` y `jumper` se convierten en componentes del
dominio. Las demás etiquetas se muestran como detecciones YOLO genéricas.

El esqueleto del dataset y el validador están en
[datasets/circuito](datasets/circuito/README.md). Allí se documentan las
clases, el formato de bounding boxes y el comando de entrenamiento.

La primera fuente PCB ya fue importada localmente con 117 imágenes de train y
13 de validación. Por tamaño, las imágenes y etiquetas están excluidas de Git;
el proceso de descarga e importación queda documentado en
[SOURCES.md](datasets/circuito/SOURCES.md).

### Tecnologías que todavía no están integradas

- **YOLO:** sería apropiado para detectar Arduino, sensores, resistencias,
  LEDs y otros componentes mediante un dataset etiquetado.
- **MediaPipe:** podría ayudar a estimar geometría, puntos de referencia y
  trayectorias de cables.
- **Teachable Machine:** podría servir para una primera clasificación sencilla
  de tipos de montaje, pero no reconstruye por sí sola las conexiones.
- **Memo Akten:** no es un modelo o dependencia de inferencia del proyecto; se
  mantiene como referencia conceptual para interacción y visualización.

La siguiente evolución debería incorporar detección de objetos con YOLO y una
segunda etapa geométrica para cables. Aun así, para producir un netlist fiable
serían necesarias fotos controladas, varias vistas o información adicional de
los pines y conexiones ocultas.

## Cómo funciona

```text
Foto subida por el usuario
          |
          v
      ui.py / Gradio
          |
          v
 vision.py: NumPy + Pillow
          |
          v
 CircuitAnalysis / domain.py
          |
          +--> resumen textual
          |
          v
 diagram.py: imagen del esquema orientativo
```

Componentes principales:

- [ui.py](src/circuito_vision/ui.py): interfaz Gradio y manejo de eventos.
- [vision.py](src/circuito_vision/vision.py): análisis visual desacoplado de la
  interfaz.
- [domain.py](src/circuito_vision/domain.py): entidades y resultado de dominio.
- [diagram.py](src/circuito_vision/diagram.py): renderizado de la imagen final.
- [main.py](src/circuito_vision/main.py): punto de entrada de la aplicación.

## Ejecutar la aplicación

Requisitos:

- Windows, macOS o Linux.
- Python 3.12.
- `uv` instalado.

Desde la raíz del repositorio:

```powershell
uv venv --python 3.12
uv sync --extra dev --extra yolo
uv run circuito-vision
```

También se puede usar:

```powershell
uv run python -m circuito_vision.main
```

Gradio mostrará una URL local en la terminal, normalmente:

```text
http://127.0.0.1:7860
```

Abrí esa dirección en el navegador, cargá una foto y presioná **Generar
esquema**. Para detener la aplicación, presioná `Ctrl+C` en la terminal.

## Inicializar desde cero con `uv`

Si se parte de una carpeta vacía:

```powershell
uv init --python 3.12
uv venv --python 3.12
uv add "gradio>=5.49.0,<6.0.0" "numpy>=2.1.0,<3.0.0" "pillow>=11.0.0,<12.0.0"
uv add --dev "pytest>=8.3.0,<9.0.0" "ruff>=0.8.0,<1.0.0"
uv sync
```

## Verificación local

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## Roadmap

### Fase 1: MVP Core — estado actual

- [x] Proyecto Python 3.12 con `src/` layout.
- [x] Interfaz Gradio para upload y webcam.
- [x] Analizador visual desacoplado.
- [x] Resultado gráfico y resumen textual.
- [x] Manejo de errores de entrada.
- [x] Pruebas unitarias básicas.

### Fase 2: Refinamiento & Testing

- [ ] Crear dataset etiquetado de fotos de protoboards.
- [x] Integrar YOLO como detector opcional con fallback.
- [ ] Sustituir el modelo genérico por pesos entrenados para componentes.
- [ ] Usar MediaPipe u otro método geométrico para seguir cables.
- [ ] Agregar pruebas con imágenes reales y casos de mala iluminación.
- [ ] Medir precisión por componente y falsos positivos.
- [ ] Considerar un modelo multimodal como segunda opinión.

### Fase 3: Scaling & Production-Ready

- [ ] Separar API de inferencia y frontend si el uso crece.
- [ ] Incorporar procesamiento asíncrono y límites de tamaño.
- [ ] Versionar modelos y registrar métricas de inferencia.
- [ ] Agregar CI/CD, Docker y despliegue.
- [ ] Exportar a SVG, Mermaid, KiCad o Fritzing cuando exista un netlist
      confiable.

## Estructura de directorios

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
│       ├── vision.py              # Heurísticas del analizador actual
│       └── diagram.py             # Render del esquema orientativo
└── tests/
    └── test_vision.py             # Pruebas unitarias iniciales
```

## Límites conocidos

- El output es un esquema visual, no un plano eléctrico certificado.
- Una foto 2D puede ocultar conexiones, pines y cruces de cables.
- El MVP no valida continuidad, polaridad, voltajes ni cortocircuitos.
- Una detección de “Arduino posible” no identifica un modelo concreto ni sus
  pines.
- Las confianzas actuales son aproximaciones de producto y no métricas de un
  modelo entrenado.
