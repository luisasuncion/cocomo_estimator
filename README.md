# Estimador COCOMO II

Aplicacion web independiente para registrar datos del modelo COCOMO II mediante un asistente por pasos y calcular el esfuerzo estimado en personas-mes. La Semana 12 incorpora el motor de calculo del esfuerzo; tiempo de desarrollo, costo total, personal requerido, salario promedio y pruebas de sensibilidad se implementaran posteriormente.

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
9. Resultado: calcula y muestra suma de factores, exponente E, EAF y esfuerzo PM.

## Alcance actual

Esta version solo calcula esfuerzo en personas-mes. No calcula todavia tiempo de desarrollo, costo total, personal requerido, salario promedio ni sensibilidad.
