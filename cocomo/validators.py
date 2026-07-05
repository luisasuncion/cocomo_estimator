def validate_ksloc(value):
    if value is None or str(value).strip() == "":
        return None, "KSLOC es obligatorio."

    try:
        ksloc = float(str(value).replace(",", "."))
    except ValueError:
        return None, "KSLOC debe ser numerico."

    if ksloc <= 0:
        return None, "KSLOC debe ser mayor que cero."

    return ksloc, None


def validate_salary(value):
    if value is None or str(value).strip() == "":
        return None, "El salario mensual promedio es obligatorio."

    try:
        salary = float(str(value).replace(",", "."))
    except ValueError:
        return None, "El salario mensual promedio debe ser numerico."

    if salary <= 0:
        return None, "El salario mensual promedio debe ser mayor que cero."

    return salary, None


def validate_currency(value):
    allowed_currencies = {"PEN"}
    currency = (value or "PEN").strip().upper()

    if currency not in allowed_currencies:
        return None, "Seleccione una moneda valida."

    return currency, None


def validate_ratings(form, table):
    errors = []
    selected = {}

    for code, options in table.items():
        rating = form.get(code)
        if rating not in options:
            errors.append(f"Seleccione una calificacion valida para {code}.")
            continue
        selected[code] = {"rating": rating, "value": options[rating]}

    return selected, errors
