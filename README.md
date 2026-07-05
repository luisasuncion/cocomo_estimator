# Estimador COCOMO II

Aplicacion web independiente para registrar datos del modelo COCOMO II mediante un asistente por pasos y calcular esfuerzo, tiempo nominal, personal promedio, costo laboral y analisis de sensibilidad. La Semana 13 agrega datos economicos y mantiene los calculos previos de E, EAF y PM.

## Tecnologias utilizadas

- Python 3
- Flask
- Bootstrap 5
- HTML, CSS y JavaScript
- pytest

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

## Ejecutar pruebas

```bash
pytest
```

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
├── cocomo/
│   ├── __init__.py
│   ├── tables.py
│   ├── services.py
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
│   ├── results.html
│   ├── summary.html
│   └── components/
│       └── rating_select.html
├── static/
    ├── css/
    │   └── styles.css
    └── js/
        └── wizard.js
└── tests/
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

Cada vez que se pulsa Siguiente, el backend valida los datos, busca el valor numerico en las tablas COCOMO II y guarda la seleccion en `session["cocomo_data"]`. Al pulsar Calcular estimacion, se calcula el esfuerzo PM y se solicita el salario. Luego se guardan los resultados finales en `session["cocomo_result"]`.

La ruta de calculo usa POST. La pantalla de resultados no borra los datos; Volver al resumen y Modificar salario conservan la estimacion, mientras Nueva estimacion limpia `session["cocomo_data"]` y `session["cocomo_result"]`.

## Alcance actual

Esta version calcula esfuerzo, tiempo nominal, personal promedio, costo laboral y sensibilidad. No agrega base de datos ni costos indirectos.
