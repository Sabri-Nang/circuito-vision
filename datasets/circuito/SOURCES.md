# Fuentes del dataset

## PCB Component Detection Dataset and YOLO Model

- URL: <https://github.com/wangshnegqi/pcb-component-detection-dataset-yolo>
- Licencia de imágenes y anotaciones: CC BY 4.0.
- Formato: YOLO.
- Uso: componentes montados sobre placas PCB.
- Estado: descargado localmente en `datasets/sources/` e importable.
- Atribución: conservar la licencia y mencionar el repositorio original en
  cualquier distribución del dataset derivado.

Mapeo aplicado:

```text
Resistor       -> resistor
Capacitor      -> capacitor
Diode          -> diode
LED            -> led
IC             -> ic
Connector      -> connector
Switch/Button  -> button
Header         -> header
Crystal        -> crystal
Debug/TP       -> debug_tp
```

## ElectroCom61

- URL: <https://data.mendeley.com/datasets/6scy6h8sjz/1>
- DOI: `10.17632/6scy6h8sjz.1`.
- Licencia: CC BY 4.0.
- Tamaño publicado: 2.071 imágenes y 61 clases.
- Estado: fuente identificada; pendiente de descargar el archivo distribuido
  por Mendeley y adaptar sus nombres de clase.

## Criterio de uso

Estas fuentes contienen componentes electrónicos y placas, pero no garantizan
que todas las imágenes representen una protoboard conectada como la que recibe
la aplicación. Para mejorar el caso de uso principal habrá que agregar luego
imágenes específicas de protoboards y circuitos completos.
