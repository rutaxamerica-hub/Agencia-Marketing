from lib import *
p = load('../original/templates/product.json')
m = p['sections']['main']
# quitar bloque "Disclosures" vacío (sin metacampos no muestra nada)
m['blocks'].pop('disclosures_g9mWze', None); m['block_order'] = []
m['settings']['gap'] = 48
# Galería: una imagen a la vez (carrusel) en vez de grid con todas visibles.
# Antes se veían todas las fotos apiladas de una vez (media_presentation "grid"),
# lo que da un aire de ficha de dropshipping. Con "carousel" se navega imagen por
# imagen, con miniaturas clicables para saltar a una foto específica.
mg = m['blocks']['media-gallery']['settings']
for _k in ('media_columns', 'image_gap', 'large_first_image'):
    mg.pop(_k, None)
mg.update({
    "media_presentation": "carousel",
    "slideshow_controls_style": "thumbnails",
    "slideshow_mobile_controls_style": "dots",
    "thumbnail_position": "left",
    "thumbnail_width": 64,
    "thumbnail_radius": 4,
    "media_radius": 6,
})
pd = m['blocks']['product-details']
pd['settings']['gap'] = 24
g = pd['blocks']['group_icgrde']
g['settings']['gap'] = 10
g['blocks']['text_xrnftG']['settings'].update({"type_preset":"h3","font":"var(--font-heading--family)","wrap":"balance"})
g['blocks']['bajada'] = text("<p>{{ closest.product.metafields.custom.bajada.value }}</p>", preset="custom", size="1.125rem", color=MUTED, line="normal")
g['blocks']['price_tVjtKg']['settings'].update({"type_preset":"h4","padding-block-start":6})
g['block_order'] = ['text_xrnftG', 'bajada', 'price_tVjtKg']
# línea de confianza corta, justo bajo el botón de compra
pd['blocks']['trust'] = text("<p>Envíos a todo Chile · Cambio si no calza con tu diagnóstico</p>",
                             preset="custom", size="0.8125rem" if False else "0.75rem", color=MUTED, font="var(--font-accent--family)", line="loose")
pd['blocks']['recibes'] = group([
    ("k", text("<h2>Qué incluye</h2>", preset="h6")),
    ("l", text("<ul><li><strong>{{ closest.product.title }}</strong></li><li><strong>Guía de uso EJE:</strong> cómo usarlo, cuándo, en qué zona, cuánto tiempo y cada cuánto.</li></ul>", preset="rte")),
], gap=8, bg=CARD, border="solid", border_color=LINE, radius=6, pad=(18,14,20,20))
# Guía de uso: antes vivía escondida dentro del acordeón; ahora es su propia
# tarjeta visible, con borde de acento, justo después de "Qué incluye".
pd['blocks']['guia_uso'] = group([
    ("head", group([
        ("icon", icon("clipboard", width=20, color=ACCENT)),
        ("h", text("<h2>Guía de uso incluida</h2>", preset="h6")),
    ], direction="row", gap=8, valign="center", mobile_vertical=False)),
    ("l", text("<p>Cada compra trae la guía EJE: <strong>cómo</strong> usarlo, <strong>cuándo</strong>, <strong>dónde</strong> aplicarlo y <strong>cuánto tiempo</strong>, más cómo ajustarlo a tu cuerpo.</p>", preset="rte")),
], gap=10, bg=CARD, border="solid", border_color=ACCENT, radius=6, pad=(18,14,20,20))
# descripción
pd['blocks']['text_aEtTtq']['settings'].update({"type_preset":"rte"})
# acordeón con información secundaria
def row(key, heading, html, ic):
    return (key, {"type":"_accordion-row","settings":{"heading":heading,"open_by_default":False,"icon":ic,"width":20},
                  "blocks":{"t": text(html, preset="rte")},"block_order":["t"]})
acc_blocks = dict([
  row("envios", "Envíos", "<p>Despachamos a todo Chile con seguimiento.</p>", "truck"),
  row("cambios", "Cambios y devoluciones", "<p>Si el producto no coincide con lo que recomendó tu diagnóstico, lo cambias o lo devuelves.</p>", "return"),
  row("dudas", "¿No sabes si es para ti?", "<p>Haz el <a href=\"/pages/diagnostico\">diagnóstico gratis</a> (2 minutos) o <a href=\"/pages/contact\">escríbenos</a>.</p>", "question_mark"),
])
pd['blocks']['info'] = {"type":"accordion","settings":{"icon":"plus","dividers":True,"divider_color":LINE,"type_preset":"h5",
    "background_color":"","text_color":"","border":"none","border_width":1,"border_opacity":100,"border_color":"","border_radius":0,
    "padding-block-start":8,"padding-block-end":0,"padding-inline-start":0,"padding-inline-end":0},
    "blocks":acc_blocks,"block_order":list(acc_blocks.keys())}
pd['block_order'] = ['group_icgrde', 'divider_VJhene', 'variant_picker_R3rGDr', 'buy_buttons_eYQEYi', 'recibes', 'guia_uso', 'trust', 'text_aEtTtq', 'info']
# recomendaciones
r = p['sections']['product_recommendations_qggXJq']
r['blocks']['text_cbcgyb']['settings'].update({"text":"<h2>Combínalo con</h2>","type_preset":"h3","font":"var(--font-heading--family)"})
c = r['blocks']['static-product-card']
bo = c['block_order']
gal, title, price = bo
c['blocks'][gal]['settings'].update({"image_ratio":"square","border_radius":4})
c['blocks'][title]['settings'].update({"type_preset":"custom","font":"var(--font-subheading--family)","padding-block-start":8})
c['blocks']['bajada'] = text("<p>{{ closest.product.metafields.custom.bajada.value }}</p>", preset="custom", size="0.875rem", color=MUTED)
c['blocks'][price]['settings'].update({"type_preset":"paragraph","padding-block-start":4})
c['block_order'] = [gal, title, 'bajada', price]
r['settings'].update({"columns_gap":20,"rows_gap":32,"gap":32,"padding-block-start":72,"padding-block-end":72})
dump_pruned(p, 'templates/product.json')
print('ok')
