from lib import *
# ---------- COLECCIÓN ----------
c = load('../original/templates/collection.json')
h = c['sections']['section']
h['blocks']['text_tqQTNE']['settings'].update({"type_preset":"h2","font":"var(--font-heading--family)"})
h['blocks']['text_twGGkJ']['settings'].update({"type_preset":"custom","font_size":"1.125rem","text_color":MUTED,"max_width":"narrow","line_height":"loose"})
h['settings'].update({"gap":10,"padding-block-start":56,"padding-block-end":24})
mc = c['sections']['main']
mc['blocks']['filters']['settings'].update({"enable_filtering":False,"enable_sorting":True,"enable_grid_density":False})
card = mc['blocks']['product-card']
card['settings']['product_card_gap'] = 6
card['blocks']['card-gallery']['settings'].update({"image_ratio":"square","border_radius":4})
card['blocks']['product_title_4nY4eT']['settings'].update({"type_preset":"custom","font":"var(--font-subheading--family)","padding-block-start":8})
card['blocks']['bajada'] = text("<p>{{ closest.product.metafields.custom.bajada.value }}</p>", preset="custom", size="0.875rem", color=MUTED)
card['blocks']['price_EzJzMm']['settings'].update({"type_preset":"paragraph","padding-block-start":4})
card['block_order'] = ["card-gallery","product_title_4nY4eT","bajada","price_EzJzMm"]
h['blocks']['guia'] = text("<p>Cada producto incluye su guía de uso.</p>", preset="custom", size="0.875rem", color=MUTED)
h['block_order'] = ["text_tqQTNE","text_twGGkJ","guia"]
mc['settings'].update({"columns_gap_horizontal":20,"columns_gap_vertical":36,"padding-block-end":72})
dump_pruned(c, 'templates/collection.json')

# ---------- CARRITO ----------
k = load('../original/templates/cart.json')
k['sections']['cart-section']['blocks']['cart-page-title']['settings']['title'] = "Tu carrito"
k['sections']['cart-section']['settings']['padding-block-start'] = 40
pl = k['sections']['product_list_NNFgcy']
hb = pl['blocks']['static-header']['blocks']
hb['product_list_text_fifeh4']['settings'].update({"text":"<h2>Completa tu rutina</h2>","type_preset":"h4","font":"var(--font-heading--family)"})
hb['product_list_button_eibbma']['settings']['label'] = "Ver todo"
pc = pl['blocks']['static-product-card']
bo = pc['block_order']
pc['blocks'][bo[0]]['settings'].update({"image_ratio":"square","border_radius":4})
pc['blocks'][bo[1]]['settings'].update({"type_preset":"custom","font":"var(--font-subheading--family)","padding-block-start":8})
pc['blocks']['bajada'] = text("<p>{{ closest.product.metafields.custom.bajada.value }}</p>", preset="custom", size="0.875rem", color=MUTED)
pc['block_order'] = [bo[0], bo[1], 'bajada', bo[2]]
pl['settings'].update({"collection":"kits","columns_gap":20,"rows_gap":32,"padding-block-start":64,"padding-block-end":72})
dump_pruned(k, 'templates/cart.json')

# ---------- HEADER ----------
hg = load('../original/sections/header-group.json')
ann = hg['sections']['header_announcements_9jGBFp']['blocks']['announcement_BxgCk9']['settings']
ann.update({"text":"Envíos a todo Chile · Guía de uso incluida en cada producto","link":"","font":"var(--font-subheading--family)","case":"none","letter_spacing":"normal","font_size":"0.75rem"})
import copy as _c
annsec = hg['sections']['header_announcements_9jGBFp']
a2 = _c.deepcopy(annsec['blocks']['announcement_BxgCk9'])
a2['settings'].update({"text":"Cada producto incluye su guía de uso","link":"/pages/sobre-nosotros"})
annsec['blocks']['announcement_guia'] = a2
annsec['blocks'].pop('announcement_guia'); annsec['block_order'] = ['announcement_BxgCk9']
annsec['settings']['speed'] = 6
hs = hg['sections']['header_section']['settings']
hs.update({"show_country":False,"show_language":False})
dump(hg, 'sections/header-group.json')

# ---------- FOOTER ----------
fg = load('../original/sections/footer-group.json')
f = fg['sections']['footer_m9NzUG']
gb = f['blocks']['group_H6VpwJ']['blocks']
gb['text_LWt8Pz']['settings'].update({"text":"<h2>Consejos de postura y recuperación</h2>","font":"var(--font-heading--family)"})
gb['text_f9CFLH']['settings'].update({"text":"<p>Guías cortas y novedades de EJE. Sin spam.</p>","type_preset":"custom","text_color":MUTED,"font_size":"0.875rem"})
f['blocks']['footer_menu'] = {"type":"menu","settings":{"menu":"footer","heading":"","menu_spacing":10,"show_as_accordion":False,"accordion_icon":"caret","accordion_dividers":False,"background_color":"","text_color":"","heading_preset":"h5","link_preset":"paragraph","padding-block-start":0,"padding-block-end":0,"padding-inline-start":0,"padding-inline-end":0},"blocks":{}}
f['blocks']['pagos'] = payment_icons()
f['blocks']['text_address']['settings']['text'] = "<p>EJE — 2 Norte 1135, Talca, Chile</p>"
f['block_order'] = ['group_H6VpwJ','email_signup_crihX7','footer_menu','pagos','text_address']
f['settings'].update({"gap":24,"padding-block-start":64,"padding-block-end":32})
sl = fg['sections']['footer_utilities_jLGE8U']['blocks']['social_links_Ew63Kq']['settings']
for key in ('instagram_url','youtube_url','tiktok_url'): sl[key] = ""   # eran links genéricos (instagram.com, etc.)
dump(fg, 'sections/footer-group.json')

# ---------- AJUSTES GLOBALES ----------
s = load('../original/config/settings_data.json')
cur = s['current']
cur.update({
  "type_size_paragraph":"16",
  "type_size_h1":"56", "type_size_h2":"40", "type_size_h3":"32", "type_size_h4":"20", "type_size_h5":"16", "type_size_h6":"12",
  "button_border_radius_primary":4, "button_border_radius_secondary":4, "card_corner_radius":4, "inputs_border_radius":4, "popover_border_radius":4, "variant_button_radius":4, "card_hover_effect":"lift",
})
dump(s, 'config/settings_data.json')
print('ok')
