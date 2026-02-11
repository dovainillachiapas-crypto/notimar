def classify(title):
    t = title.lower()

    if "homicidio" in t or "ejecutado" in t or "ataque armado" in t:
        return "🔴 Alto"
    elif "robo de vehículo" in t:
        return "🟠 Medio"
    elif "asalto" in t:
        return "🟡 Medio"
    else:
        return "🟢 Bajo"
