#!/usr/bin/env python3
"""Genera el PDF de evidencias de ejecución del MiniCompiler."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(
    "/Users/macbookair/.cursor/projects/Users-macbookair-Documents-mini-compiler/assets"
)
OUT = Path(__file__).resolve().parent / "Evidencias_de_ejecucion.pdf"

# A4 a 150 dpi
W, H = 1240, 1754
MARGIN = 64
BG = (248, 249, 252)
INK = (22, 28, 37)
MUTED = (90, 98, 110)
ACCENT = (37, 99, 235)
LINE = (220, 224, 230)
WHITE = (255, 255, 255)

FONT_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

CASES = [
    {
        "num": "1",
        "title": "Compilación correcta — vista general",
        "code": "a = 10\nb = 5\nresultado = (a + b) * 2",
        "note": "Las seis fases se completan con éxito (✓). Se observan tokens, árbol sintáctico, tabla de símbolos y código intermedio de tres direcciones.",
        "image": "Captura_de_Pantalla_2026-11-24_a_la_s__10.59.41_p.m.-c335d963-3e99-47d0-b59d-9b910220309c.png",
    },
    {
        "num": "1",
        "title": "Compilación correcta — optimización y ensamblador",
        "code": "a = 10\nb = 5\nresultado = (a + b) * 2",
        "note": "El optimizador reduce (a + b) * 2 a resultado = 30 (propagación, plegado y eliminación de código muerto). MiniCPU genera MOV hacia resultado.",
        "image": "Captura_de_Pantalla_2026-11-24_a_la_s__11.00.02_p.m.-47eb21a1-6076-4502-8146-04c84c95ea4e.png",
    },
    {
        "num": "2",
        "title": "Error léxico",
        "code": "a = 10 @ 5",
        "note": "El carácter @ no es válido. La fase Tokens marca error (✗) y las fases siguientes no se ejecutan.",
        "image": "Captura_de_Pantalla_2026-11-24_a_la_s__11.01.16_p.m.-d23d9c82-ae11-4b08-8046-06c237fd3c07.png",
    },
    {
        "num": "3",
        "title": "Error sintáctico",
        "code": "x = 10 +",
        "note": "Los tokens son correctos. Falta un operando después de +. El análisis sintáctico falla y el proceso se detiene.",
        "image": "Captura_de_Pantalla_2026-11-24_a_la_s__11.01.49_p.m.-db6dfcb4-257c-4d32-9ebd-0757b7fbdb92.png",
    },
    {
        "num": "4",
        "title": "Error semántico",
        "code": "resultado = a + 5",
        "note": "Léxico y sintaxis correctos. La variable a no fue declarada. El análisis semántico falla; no se genera código.",
        "image": "Captura_de_Pantalla_2026-11-24_a_la_s__11.02.24_p.m.-0330c1c8-5f7d-4c14-a036-f047ff430b85.png",
    },
    {
        "num": "5",
        "title": "Optimización — plegado de constantes",
        "code": "x = 2 + 3",
        "note": "Código intermedio: t1 = 2 + 3; x = t1. Código optimizado: x = 5. Técnicas: plegado, propagación y eliminación del temporal.",
        "image": "Captura_de_Pantalla_2026-11-24_a_la_s__11.03.11_p.m.-751359a7-8741-4c24-8608-9ffedc20487f.png",
    },
    {
        "num": "6",
        "title": "Pruebas automatizadas",
        "code": "python -m unittest discover -s tests -v",
        "note": "Se ejecutaron 7 casos de demostración. Todos resultaron OK.",
        "image": "Captura_de_Pantalla_2026-11-24_a_la_s__11.03.52_p.m.-d93469a4-9251-4018-a4f7-44c22a04afd3.png",
    },
]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def header(draw, page_title, page_num, total):
    draw.rectangle([0, 0, W, 88], fill=(15, 23, 42))
    title_f = font(FONT_BOLD, 22)
    sub_f = font(FONT_REG, 16)
    draw.text((MARGIN, 22), "MiniCompiler Web", font=title_f, fill=WHITE)
    draw.text((MARGIN, 52), page_title, font=sub_f, fill=(186, 198, 216))
    label = f"{page_num} / {total}"
    tw = draw.textlength(label, font=sub_f)
    draw.text((W - MARGIN - tw, 36), label, font=sub_f, fill=(186, 198, 216))


def footer(draw):
    fnt = font(FONT_REG, 14)
    text = "Evidencias de ejecución y pruebas  ·  Taller final: desarrollo de un compilador"
    draw.text((MARGIN, H - 42), text, font=fnt, fill=MUTED)


def fit_image(path, box_w, box_h):
    img = Image.open(path).convert("RGB")
    scale = min(box_w / img.width, box_h / img.height)
    new_size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
    return img.resize(new_size, Image.Resampling.LANCZOS)


def cover_page(total):
    page = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(page)
    d.rectangle([0, 0, W, 280], fill=(15, 23, 42))
    d.text((MARGIN, 70), "TALLER FINAL", font=font(FONT_REG, 22), fill=(147, 197, 253))
    d.text((MARGIN, 110), "Evidencias de ejecución", font=font(FONT_BOLD, 48), fill=WHITE)
    d.text((MARGIN, 178), "y pruebas realizadas", font=font(FONT_BOLD, 48), fill=WHITE)
    d.text(
        (MARGIN, 250),
        "MiniCompiler Web  ·  lenguaje MiniLang",
        font=font(FONT_REG, 20),
        fill=(186, 198, 216),
    )

    y = 340
    meta = [
        ("Proyecto", "Compilador web educativo (análisis y síntesis)"),
        ("Repositorio", "https://github.com/edwchalo/mini-compiler"),
        ("Interfaz", "http://127.0.0.1:8080"),
        ("Fecha", "24 de noviembre de 2026"),
    ]
    label_f = font(FONT_BOLD, 18)
    value_f = font(FONT_REG, 18)
    for label, value in meta:
        d.text((MARGIN, y), label, font=label_f, fill=ACCENT)
        d.text((MARGIN + 180, y), value, font=value_f, fill=INK)
        y += 42

    y += 24
    d.text((MARGIN, y), "Contenido", font=font(FONT_BOLD, 24), fill=INK)
    y += 48
    items = [
        "1. Compilación correcta (vista general y detalle de optimización)",
        "2. Error léxico  —  carácter no permitido",
        "3. Error sintáctico  —  expresión incompleta",
        "4. Error semántico  —  variable no declarada",
        "5. Optimización  —  plegado de constantes",
        "6. Pruebas automatizadas  —  7 tests OK",
    ]
    item_f = font(FONT_REG, 20)
    for item in items:
        d.ellipse([MARGIN, y + 8, MARGIN + 10, y + 18], fill=ACCENT)
        d.text((MARGIN + 28, y), item, font=item_f, fill=INK)
        y += 44

    y += 20
    note_f = font(FONT_REG, 16)
    note = (
        "Estas capturas demuestran que el compilador muestra cada fase, "
        "identifica el error en la etapa correspondiente y no continúa el "
        "proceso como si la compilación hubiera sido exitosa."
    )
    for line in wrap(d, note, note_f, W - 2 * MARGIN):
        d.text((MARGIN, y), line, font=note_f, fill=MUTED)
        y += 26

    footer(d)
    d.text(
        (W - MARGIN - d.textlength("1 / %s" % total, font=font(FONT_REG, 16)), 36),
        "1 / %s" % total,
        font=font(FONT_REG, 16),
        fill=(186, 198, 216),
    )
    return page


def case_page(case, page_num, total):
    page = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(page)
    header(d, "Evidencias de ejecución y pruebas", page_num, total)

    y = 120
    badge = f"Caso {case['num']}"
    badge_f = font(FONT_BOLD, 16)
    bw = d.textlength(badge, font=badge_f) + 28
    d.rounded_rectangle([MARGIN, y, MARGIN + bw, y + 36], radius=8, fill=ACCENT)
    d.text((MARGIN + 14, y + 8), badge, font=badge_f, fill=WHITE)

    title_f = font(FONT_BOLD, 28)
    d.text((MARGIN, y + 52), case["title"], font=title_f, fill=INK)

    y += 110
    d.text((MARGIN, y), "Código fuente / comando", font=font(FONT_BOLD, 16), fill=MUTED)
    y += 30
    code_f = font(FONT_REG, 18)
    code_lines = case["code"].split("\n")
    box_h = 18 + 28 * len(code_lines)
    d.rounded_rectangle(
        [MARGIN, y, W - MARGIN, y + box_h],
        radius=10,
        fill=(15, 23, 42),
    )
    cy = y + 12
    for line in code_lines:
        d.text((MARGIN + 20, cy), line, font=code_f, fill=(226, 232, 240))
        cy += 28

    y += box_h + 20
    note_f = font(FONT_REG, 17)
    for line in wrap(d, case["note"], note_f, W - 2 * MARGIN):
        d.text((MARGIN, y), line, font=note_f, fill=INK)
        y += 24

    y += 16
    box_top = y
    box_bottom = H - 70
    box_w = W - 2 * MARGIN
    box_h = box_bottom - box_top
    d.rounded_rectangle(
        [MARGIN - 4, box_top - 4, W - MARGIN + 4, box_bottom + 4],
        radius=12,
        outline=LINE,
        width=2,
        fill=WHITE,
    )

    shot = fit_image(ASSETS / case["image"], box_w - 16, box_h - 16)
    x = MARGIN + (box_w - shot.width) // 2
    iy = box_top + (box_h - shot.height) // 2
    page.paste(shot, (x, iy))

    footer(d)
    return page


def main():
    total = 1 + len(CASES)
    pages = [cover_page(total)]
    for i, case in enumerate(CASES, start=2):
        pages.append(case_page(case, i, total))

    first, rest = pages[0], pages[1:]
    first.save(
        OUT,
        "PDF",
        save_all=True,
        append_images=rest,
        resolution=150.0,
        title="Evidencias de ejecución — MiniCompiler Web",
        author="edwchalo",
    )
    print(OUT)


if __name__ == "__main__":
    main()
