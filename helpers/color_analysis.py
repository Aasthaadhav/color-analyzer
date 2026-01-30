from colorsys import rgb_to_hls

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def analyze_color(hex_code):
    r, g, b = hex_to_rgb(hex_code)

    # Normalize 0–1
    rn, gn, bn = r/255, g/255, b/255

    # Convert to HLS (Hue, Lightness, Saturation)
    h, l, s = rgb_to_hls(rn, gn, bn)

    # Convert hue 0–1 → degrees 0–360
    hue_deg = h * 360

    # ---------- TEMPERATURE ----------
    if hue_deg < 60 or hue_deg > 300:
        temperature = "Warm"
    elif 60 <= hue_deg <= 180:
        temperature = "Cool"
    else:
        temperature = "Neutral"

    # ---------- VALUE (LIGHTNESS) ----------
    if l > 0.75:
        value = "Very Light"
    elif l > 0.55:
        value = "Light"
    elif l > 0.35:
        value = "Medium"
    elif l > 0.20:
        value = "Dark"
    else:
        value = "Very Dark"

    # ---------- CHROMA (SATURATION) ----------
    if s > 0.65:
        chroma = "Bright"
    elif s > 0.40:
        chroma = "Soft"
    else:
        chroma = "Muted"

    # ---------- EXTRA NOTES ----------
    notes = []

    if value in ["Very Light", "Light"]:
        notes.append("Works well for soft summer & light spring palettes.")
    if value in ["Dark", "Very Dark"]:
        notes.append("Can overpower soft palettes; suits deep winter/autumn.")
    if chroma == "Bright":
        notes.append("High chroma — good for bold contrast styling.")
    if chroma == "Muted":
        notes.append("Soft muted tone — ideal for romantic/neutral styling.")
    if temperature == "Warm":
        notes.append("Complements gold jewelry and warm-toned outfits.")
    if temperature == "Cool":
        notes.append("Matches silver/platinum accessories.")

    return {
        "hex": hex_code,
        "temperature": temperature,
        "value": value,
        "chroma": chroma,
        "hue_degree": round(hue_deg, 2),
        "lightness": round(l, 2),
        "saturation": round(s, 2),
        "description": "; ".join(notes)
    }
