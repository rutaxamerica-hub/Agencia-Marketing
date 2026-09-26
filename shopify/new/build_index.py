from lib import *
import copy
orig = load('../original/templates/index.json')
S = orig['sections']
HERO_IMG = "shopify://shop_images/Gemini_Generated_Image_qtzrjtqtzrjtqtzr_1.jpg"
IMG_OF = "shopify://shop_images/photo-1735948055457-8d816fb80a87.jpg"
IMG_REC = "shopify://shop_images/photo-1591343395082-e120087004b4.jpg"
IMG_KIT = "shopify://shop_images/photo-1586401100295-7a8096fd231a.jpg"
IMG_AUTH = "shopify://shop_images/photo-1645005512968-0c1fe99f0093.jpg"

sections = {}

# 1. HERO — una idea: qué es EJE + qué lo diferencia + siguiente paso
sections["hero"] = section([
  ("hero_text", group([
     ("kicker", kicker("Ergonomía y recuperación", color=ACCENT_LIGHT)),
     ("title", text("<h1>Primero entendemos qué te duele. Después, te decimos qué usar.</h1>", preset="h1", color=PAPER, wrap="balance")),
     ("sub", text("<p>Productos para tu escritorio y para después de entrenar, elegidos según un diagnóstico de 2 minutos. Cada uno con su guía de uso.</p>",
                  preset="custom", size="1.125rem", line="loose", color="#CFCBC2", max_width="narrow")),
     ("ctas", group([
        ("cta1", button("Hacer diagnóstico gratis", "/pages/diagnostico")),
        ("cta2", button("Ver productos", "/collections/all", style="button-custom", bg="rgba(0,0,0,0)", fg=PAPER, border="#6B6860")),
     ], direction="row", gap=12, mobile_vertical=False, halign="flex-start")),
  ], gap=20, pad=(8,8,0,0), valign_col="center")),
  ("hero_media", group([("img", image(HERO_IMG, ratio="adapt", radius=6, height="fill"))], height="fill")),
], direction="row", gap=56, bg=DARK, pad=(72,72), height="", valign="center")

# 2. CATEGORÍAS — atajo directo a comprar, cada card explica para qué es
def cat_card(img, title, line, cta, url):
    return group([
        ("img", image(img, ratio="landscape", radius=4)),
        ("body", group([
            ("t", text(f"<h3>{title}</h3>", preset="h4")),
            ("d", text(f"<p>{line}</p>", preset="custom", size="0.875rem", color=MUTED, line="loose")),
            ("c", button(cta, url, style="button-unstyled", link_color=ACCENT)),
        ], gap=6, pad=(4,4,4,4))),
    ], gap=16, link=url)

sections["categorias"] = section([
  ("head", group([
     ("k", kicker("Compra por necesidad")),
     ("h", text("<h2>¿Dónde lo necesitas?</h2>", preset="h2")),
  ], gap=10)),
  ("cards", group([
     ("oficina", cat_card(IMG_OF, "Oficina", "Espalda, cuello y postura mientras trabajas sentado.", "Ver oficina →", "/collections/oficina")),
     ("recuperacion", cat_card(IMG_REC, "Recuperación", "Automasaje, movilidad y compresión después de entrenar.", "Ver recuperación →", "/collections/recuperacion")),
     ("kits", cat_card(IMG_KIT, "Kits", "Combos armados para un problema completo, en una compra.", "Ver kits →", "/collections/kits")),
  ], direction="row", gap=24, valign="flex-start")),
], gap=36, pad=(80,72))

# 3. CÓMO FUNCIONA — la propuesta de valor en 3 pasos
def step(n, title, line):
    return group([
        ("n", text(f"<p>{n}</p>", preset="custom", font="var(--font-accent--family)", size="0.875rem", color=ACCENT)),
        ("t", text(f"<h3>{title}</h3>", preset="h4")),
        ("d", text(f"<p>{line}</p>", preset="custom", size="0.9375rem" if False else "1rem", color=MUTED, line="loose")),
    ], gap=10, bg=CARD, border="solid", border_color=LINE, radius=6, pad=(28,28,28,28), height="fill")

sections["como_funciona"] = section([
  ("head", group([
     ("k", kicker("Cómo funciona")),
     ("h", text("<h2>No vendemos a ciegas.</h2>", preset="h2")),
     ("s", text("<p>Tres pasos para que compres lo que de verdad te sirve.</p>", preset="custom", size="1.125rem", color=MUTED)),
  ], gap=10)),
  ("steps", group([
     ("s1", step("01", "Entiende qué te pasa", "Respondes 4 preguntas sobre dónde y cuándo te molesta.")),
     ("s2", step("02", "Elige lo correcto", "Te recomendamos el producto o kit que corresponde. Nada de más.")),
     ("s3", step("03", "Úsalo bien", "Cada compra trae una guía de uso desarrollada con kinesiólogo.")),
  ], direction="row", gap=16, valign="flex-start")),
  ("cta", button("Empezar diagnóstico", "/pages/diagnostico", style="button-secondary")),
], gap=36, bg=SAND, pad=(80,80))

# 4. KITS — productos con bajada visible en la tarjeta
pl = copy.deepcopy(S["product_list_kits"])
hdr = pl["blocks"]["static-header"]
hdr["settings"]["align_baseline"] = False
hdr["blocks"] = {
  "product_list_text_heading": text("<h2>Empieza por un kit</h2>", preset="h2", width="100%"),
  "product_list_button": button("Ver todos los kits", "/collections/kits", style="button-unstyled", link_color=ACCENT),
}
hdr["blocks"]["product_list_text_heading"]["settings"]["width"] = "fit-content"
hdr["block_order"] = ["product_list_text_heading", "product_list_button"]
card = pl["blocks"]["static-product-card"]
card["settings"]["product_card_gap"] = 6
card["blocks"]["product_card_gallery"]["settings"]["image_ratio"] = "square"
card["blocks"]["product_card_gallery"]["settings"]["border_radius"] = 4
card["blocks"]["product_title"]["settings"].update({"type_preset":"custom","font":"var(--font-subheading--family)","font_size":"1rem","padding-block-start":8})
card["blocks"]["bajada"] = text("<p>{{ closest.product.metafields.custom.bajada.value }}</p>", preset="custom", size="0.875rem", color=MUTED, line="normal")
card["blocks"]["price"]["settings"].update({"type_preset":"paragraph","padding-block-start":4})
card["block_order"] = ["product_card_gallery", "product_title", "bajada", "price"]
pl["settings"].update({"columns_gap":20,"rows_gap":36,"gap":36,"background_color":"","padding-block-start":88,"padding-block-end":80})
sections["kits"] = pl

# 5. EL PROBLEMA — un dato, una idea, un link
sections["problema"] = section([
  ("media", group([("img", image(IMG_AUTH, ratio="portrait", radius=6))])),
  ("body", group([
     ("k", kicker("El problema")),
     ("stat", text("<h2>7 de cada 10</h2>", preset="custom", font="var(--font-heading--family)", size="4.5rem", color=ACCENT, line="tight")),
     ("stat_l", text("<p>personas que trabajan desde casa en Chile tienen molestias musculares.</p>", preset="custom", size="1.25rem", line="normal", max_width="narrow")),
     ("sp", text("<p>La mayoría ya probó algo. Lo que falla no es el esfuerzo: es comprar sin diagnóstico y usar sin guía.</p>", preset="custom", size="1rem", color=MUTED, line="loose", max_width="narrow", pad=(8,0,0,0))),
     ("link", button("Por qué pasa esto →", "/pages/el-problema", style="button-unstyled", link_color=ACCENT)),
     ("src", text("<p>Fuente: Revista Emprende e Infogate, 2025.</p>", preset="custom", size="0.75rem", color="#8A867C")),
  ], gap=14, valign_col="center")),
], direction="row", gap=64, pad=(80,80), valign="center")

DIV = {"type":"_divider","settings":{"thickness":1,"corner_radius":"square","divider_color":"#34312C","width_percent":100,"padding-block-start":0,"padding-block-end":0},"blocks":{}}
# 6. LA GUÍA — lo que recibes además del producto
def guide_row(n, title, line):
    return group([
        ("n", text(f"<p>{n}</p>", preset="custom", font="var(--font-accent--family)", size="0.75rem", color="#8A867C", width="fit-content")),
        ("b", group([
            ("t", text(f"<h3>{title}</h3>", preset="h5", color=PAPER)),
            ("d", text(f"<p>{line}</p>", preset="custom", size="0.9375rem" if False else "0.875rem", color="#A9A59C", line="normal")),
        ], gap=2, width="fill")),
    ], direction="row", gap=20, mobile_vertical=False, halign="flex-start", valign="flex-start", width="fill")

sections["guia"] = section([
  ("intro", group([
     ("k", kicker("Incluido en cada compra", color=ACCENT_LIGHT)),
     ("h", text("<h2>No te llega solo un producto. Te llega cómo usarlo.</h2>", preset="h2", color=PAPER, wrap="balance")),
     ("s", text("<p>Cada producto EJE trae su guía de uso. Sin adivinar, sin buscar tutoriales.</p>", preset="custom", size="1.125rem", color="#CFCBC2", line="loose", max_width="narrow")),
  ], gap=16)),
  ("list", group([
     ("g1", guide_row("01", "Cómo usarlo", "Paso a paso, desde el primer día.")),
     ("d1", DIV),
     ("g2", guide_row("02", "Cuándo", "En qué momento de tu jornada o de tu entrenamiento.")),
     ("d2", DIV),
     ("g3", guide_row("03", "Dónde", "En qué zona del cuerpo o de tu escritorio.")),
     ("d3", DIV),
     ("g4", guide_row("04", "Cuánto tiempo", "Duración y frecuencia recomendadas.")),
     ("d4", DIV),
     ("g5", guide_row("05", "Cómo ajustarlo", "Para que se adapte a tu cuerpo y a tu espacio.")),
  ], gap=18)),
], direction="row", gap=64, bg=DARK, pad=(88,88), valign="center")

# 7. GARANTÍAS
def trust(ic, title, line):
    return group([
        ("i", icon(ic, width=22, color=INK)),
        ("t", text(f"<h3>{title}</h3>", preset="h5")),
        ("d", text(f"<p>{line}</p>", preset="custom", size="0.875rem", color=MUTED, line="loose")),
    ], gap=8)

sections["garantias"] = section([
  ("row", group([
     ("t1", trust("truck", "Envíos a todo Chile", "Despachamos a regiones con seguimiento.")),
     ("t2", trust("return", "Cambio si no calza", "Si el producto no coincide con tu diagnóstico, lo cambias o lo devuelves.")),
     ("t3", trust("chat_bubble", "Atención directa", "¿Dudas antes de comprar? <a href='/pages/contact'>Escríbenos</a>.")),
  ], direction="row", gap=40, valign="flex-start")),
], gap=24, pad=(64,64), bg=SAND)

# 7. CIERRE — un solo CTA
sections["cierre"] = section([
  ("h", text("<h2>¿No sabes por dónde empezar?</h2>", preset="h2", align="center", color=PAPER, wrap="balance")),
  ("s", text("<p>Responde 4 preguntas y te decimos qué usar.</p>", preset="custom", size="1.125rem", align="center", color="#CFCBC2")),
  ("c", button("Hacer diagnóstico gratis", "/pages/diagnostico")),
], gap=16, bg=DARK, pad=(88,88), align_col="center")

order = ["hero","categorias","como_funciona","kits","guia","problema","garantias","cierre"]
dump_pruned({"sections": sections, "order": order}, 'templates/index.json')
print("ok")
