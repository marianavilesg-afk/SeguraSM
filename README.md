# SeguraSM 🚦

**Panel interactivo de análisis de los registros históricos de siniestros viales en Santa Marta, Colombia.**

SeguraSM permite explorar registros por periodo y tipo, consultar indicadores, visualizar gráficas y observar la ubicación de los registros que cuentan con coordenadas.

## Archivos del proyecto

```text
SeguraSM_App/
├── app.py
├── requirements.txt
├── README.md
└── SeguraSM_Resultados.xlsx   # agrega aquí el Excel generado en Google Colab
```

## Ejecutar en tu computador

1. Instala Python.
2. Abre una terminal dentro de esta carpeta.
3. Ejecuta:

   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

4. La aplicación se abrirá en el navegador. Si el Excel no está junto a `app.py`, cárgalo desde el panel lateral.

## Publicar en internet

1. Crea un repositorio nuevo en GitHub, por ejemplo `SeguraSM`.
2. Sube `app.py`, `requirements.txt`, `README.md` y el archivo `SeguraSM_Resultados.xlsx`.
3. En Streamlit Community Cloud, crea una nueva aplicación y selecciona ese repositorio, la rama `main` y el archivo principal `app.py`.
4. Pulsa **Deploy**. Streamlit generará un enlace para compartir la aplicación.

> El archivo de Excel debe contener la hoja de datos preparada en Colab, con fecha, latitud y longitud. La aplicación intenta identificar automáticamente la hoja adecuada. No subas bases que contengan nombres, teléfonos, placas u otros datos personales.

## Alcance y limitaciones

El tablero es descriptivo: resume únicamente los registros presentes en el archivo cargado. La cobertura temporal del conjunto usado en el proyecto es limitada (2019, del 1 de enero al 11 de agosto), por lo que no debe presentarse como una predicción de las condiciones actuales o futuras de seguridad vial.
