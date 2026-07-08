# Estimador COCOMO II

Aplicacion web independiente para registrar datos del modelo COCOMO II mediante un asistente por pasos, calcular esfuerzo, tiempo nominal, personal promedio, costo laboral, analisis de sensibilidad y exportar un reporte PDF con los resultados finales.

## Tecnologias utilizadas

- Python 3
- Flask
- Bootstrap 5
- HTML, CSS y JavaScript
- pytest
- WeasyPrint
- ReportLab como alternativa si WeasyPrint no esta disponible

## Requisitos

- Python 3.10 o superior recomendado
- pip

## Crear entorno virtual

```bash
python -m venv venv
```

En Windows:

```bash
venv\Scripts\activate
```

En Linux o macOS:

```bash
source venv/bin/activate
```

## Instalar dependencias

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
python app.py
```

La aplicacion queda disponible en:

```text
http://127.0.0.1:5000
```

## Ejecución mediante archivo BAT

Para ejecutar en Windows, se incluye el archivo:

```text
ejecutable/iniciar_estimador.bat
```

Para ejecutarlo:

1. Descomprima el archivo ZIP del proyecto.
2. Ingrese a la carpeta `ejecutable`.
3. Haga doble clic en `iniciar_estimador.bat`.
4. Espere a que se cree el entorno virtual `venv` y se instalen las dependencias.
5. El sistema se abrira automaticamente en el navegador.

Requisitos previos:

- Tener instalado Python 3.
- Python debe estar agregado al PATH del sistema.
- Tener conexion a internet la primera vez que se ejecuta, para instalar dependencias desde `requirements.txt`.

Si Python no esta agregado al PATH, instale Python 3 desde:

```text
https://www.python.org/downloads/
```

Durante la instalacion en Windows, marque la opcion `Add Python to PATH`. Luego cierre la consola y vuelva a ejecutar `ejecutable/iniciar_estimador.bat`.

La URL local del sistema es:

```text
http://127.0.0.1:5000
```

## Exportar reporte PDF

Desde la pantalla de resultados finales aparece el boton:

```text
Exportar reporte PDF
```

La ruta utilizada es:

```text
/exportar-reporte
```

El archivo descargado usa el nombre:

```text
reporte_cocomo_ii_nombre_del_proyecto_YYYY-MM-DD.pdf
```

El PDF incluye:

- Portada con nombre del proyecto, fecha y aplicacion.
- Datos generales del proyecto.
- Factores de escala.
- Multiplicadores de esfuerzo separados por categoria.
- Resultados principales: PM, TDEV, personal, salario y costo.
- Detalle de formulas.
- Analisis de sensibilidad por tamano y salario.
- Interpretacion dinamica y conclusion tecnica.

## Formulas implementadas

El exponente `E` se calcula con la suma de los cinco factores de escala:

```text
E = B + 0.01 x sum(Wj)
B = 0.91
```

El Factor de Ajuste de Esfuerzo `EAF` es el producto de los 17 multiplicadores de esfuerzo:

```text
EAF = EM1 x EM2 x ... x EM17
```

El esfuerzo en personas-mes se calcula con:

```text
PM = A x Size^E x EAF
A = 2.94
Size = KSLOC
```

Una persona-mes representa una unidad de esfuerzo: el trabajo aproximado que una persona realizaria durante un mes. Por ejemplo, `34.30 personas-mes` expresa esfuerzo total estimado, no duracion automatica ni cantidad de integrantes.

El exponente de tiempo `F` se calcula con:

```text
F = D + 0.2 x (E - B)
D = 0.28
B = 0.91
```

El tiempo nominal de desarrollo `TDEV` se calcula con:

```text
TDEV = C x PM^F
C = 3.67
```

El tiempo nominal representa la duracion estimada del desarrollo en meses segun el modelo. No es una fecha calendario fija ni contempla interrupciones externas.

El personal promedio se calcula con:

```text
Personal promedio = PM / TDEV
```

La aplicacion tambien muestra una recomendacion practica redondeada hacia arriba, pero conserva el valor tecnico exacto para los calculos.

El costo total laboral se calcula con:

```text
Costo total = PM x salario mensual promedio
```

El salario se interpreta como costo mensual por persona. El costo calculado considera unicamente esfuerzo del personal; no incluye infraestructura, licencias, servicios en la nube, capacitacion, mantenimiento ni otros costos indirectos.

## Analisis de sensibilidad

La aplicacion calcula escenarios sin modificar los datos originales del usuario.

Para tamano del proyecto:

- Optimista: KSLOC - 10 %
- Base: KSLOC actual
- Pesimista: KSLOC + 10 %

En cada escenario se recalculan PM, TDEV, personal promedio y costo total usando el mismo E, EAF y salario.

Para salario:

- Bajo: salario - 10 %
- Base: salario actual
- Alto: salario + 10 %

En estos escenarios se mantiene constante el tamano, PM, TDEV y personal; solo cambia el costo total. Los graficos se muestran con Chart.js usando datos calculados por Flask.

## Estructura del proyecto

```text
cocomo_estimator/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── ejecutable/
│   ├── iniciar_estimador.bat
│   └── instrucciones.txt
├── cocomo/
│   ├── __init__.py
│   ├── tables.py
│   ├── services.py
│   ├── report_service.py
│   ├── routes.py
│   └── validators.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── step_size.html
│   ├── step_scale.html
│   ├── step_product.html
│   ├── step_platform.html
│   ├── step_personnel.html
│   ├── step_project.html
│   ├── economics.html
│   ├── report_pdf.html
│   ├── results.html
│   ├── summary.html
│   └── components/
│       └── rating_select.html
├── static/
    ├── css/
    │   ├── report.css
    │   └── styles.css
    └── js/
        └── wizard.js
└── tests/
    ├── test_report_export.py
    ├── test_routes.py
    └── test_services.py
```

## Flujo de la pagina web

1. Inicio: presenta la aplicacion e inicia la estimacion.
2. Tamano: captura nombre del proyecto y KSLOC.
3. Factores de escala: registra PREC, FLEX, RESL, TEAM y PMAT.
4. Producto: registra RELY, DATA, CPLX, RUSE y DOCU.
5. Plataforma: registra TIME, STOR y PVOL.
6. Personal: registra ACAP, PCAP, PCON, AEXP, PEXP y LTEX.
7. Proyecto: registra TOOL, SITE y SCED.
8. Resumen: muestra todas las selecciones y valores guardados en sesion.
9. Datos economicos: muestra el esfuerzo PM y solicita salario mensual promedio y moneda.
10. Resultados: muestra esfuerzo, TDEV, personal promedio, costo total, formulas sustituidas y sensibilidad.
11. Exportacion PDF: descarga un reporte imprimible con los resultados finales.
