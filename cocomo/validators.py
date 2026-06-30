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
