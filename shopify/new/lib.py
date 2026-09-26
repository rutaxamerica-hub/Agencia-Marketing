import json, copy
HEADER = """/*
 * ------------------------------------------------------------
 * IMPORTANT: The contents of this file are auto-generated.
 *
 * This file may be updated by the Shopify admin theme editor
 * or related systems. Please exercise caution as any changes
 * made to this file may be overwritten.
 * ------------------------------------------------------------
 */
"""
def load(f):
    r=open(f).read(); return json.loads(r[r.index('{'):])
def dump(d, f):
    open(f,"w").write(json.dumps(d, ensure_ascii=False, separators=(",",":")))

INK="#161512"; PAPER="#F0EEE9"; SAND="#E4DFD3"; CARD="#F8F6F2"; LINE="#D6D2C6"; MUTED="#57554C"; ACCENT="#B6462B"; ACCENT_LIGHT="#D98B6E"; DARK="#141311"

def _blocks(children):
    b={}; order=[]
    for k,v in children:
        b[k]=v; order.append(k)
    return b, order

def group(children, direction="column", gap=16, align_col="flex-start", valign_col="center", halign="flex-start", valign="center",
          bg="", border="none", border_color="", radius=0, pad=(0,0,0,0), link="", width="fill", mobile_vertical=True, height="fit", custom_width=100, width_mobile="fill"):
    blocks, order = _blocks(children)
    return {"type":"group","settings":{
        "content_direction":direction,"vertical_on_mobile":mobile_vertical,"horizontal_alignment":halign,"vertical_alignment":valign,
        "align_baseline":False,"horizontal_alignment_flex_direction_column":align_col,"vertical_alignment_flex_direction_column":valign_col,
        "gap":gap,"width":width,"custom_width":custom_width,"width_mobile":width_mobile,"custom_width_mobile":100,"height":height,"custom_height":100,
        "background_media":"none","background_color":bg,"video_position":"cover","background_image_position":"cover","toggle_overlay":False,
        "overlay_color":"#00000026","overlay_style":"solid","gradient_direction":"to top","border":border,"border_width":1,"border_opacity":100,
        "border_color":border_color,"border_radius":radius,"link":link,"open_in_new_tab":False,"placeholder":"",
        "padding-block-start":pad[0],"padding-block-end":pad[1],"padding-inline-start":pad[2],"padding-inline-end":pad[3]},
        "blocks":blocks,"block_order":order}

def text(html, preset="rte", align="left", color="", width="100%", max_width="normal", font="var(--font-body--family)", size="1rem",
         case="none", spacing="normal", line="normal", wrap="pretty", pad=(0,0,0,0)):
    return {"type":"text","settings":{"text":html,"width":width,"max_width":max_width,"alignment":align,"type_preset":preset,"font":font,
        "font_size":size,"line_height":line,"letter_spacing":spacing,"case":case,"wrap":wrap,"text_color":color,"background":False,
        "background_color":"#00000026","corner_radius":0,"padding-block-start":pad[0],"padding-block-end":pad[1],
        "padding-inline-start":pad[2],"padding-inline-end":pad[3]},"blocks":{}}

def kicker(t, color=ACCENT, align="left"):
    return text(f"<p>{t}</p>", preset="custom", align=align, color=color, font="var(--font-accent--family)", size="0.75rem", case="uppercase", spacing="loose")

def button(label, link, style="button", bg="", fg="", border="", width="fit-content", width_mobile="fit-content", link_color=""):
    s={"label":label,"link":link,"open_in_new_tab":False,"style_class":style,"width":width,"custom_width":100,"width_mobile":width_mobile,"custom_width_mobile":100}
    if style=="button-custom":
        s.update({"custom_button_background":bg,"custom_button_text":fg,"custom_button_border":border})
    if link_color: s["link_text_color"]=link_color
    return {"type":"button","settings":s,"blocks":{}}

def image(src, ratio="adapt", radius=4, height="fit"):
    return {"type":"image","settings":{"image":src,"link":"","image_ratio":ratio,"width":"fill","custom_width":100,"width_mobile":"fill","custom_width_mobile":100,
        "height":height,"border":"none","border_width":1,"border_opacity":100,"border_color":"","border_radius":radius,
        "padding-block-start":0,"padding-block-end":0,"padding-inline-start":0,"padding-inline-end":0},"blocks":{}}

def icon(name, width=28, color=""):
    return {"type":"icon","settings":{"icon":name,"width":width,"link":"","open_in_new_tab":False,"icon_color":color},"blocks":{}}

def section(children, direction="column", gap=32, bg="", pad=(72,72), width="page-width", height="", align_col="flex-start", halign="flex-start", valign="center", mobile_vertical=True):
    blocks, order = _blocks(children)
    return {"type":"section","blocks":blocks,"block_order":order,"settings":{
        "content_direction":direction,"vertical_on_mobile":mobile_vertical,"horizontal_alignment":halign,"vertical_alignment":valign,"align_baseline":False,
        "horizontal_alignment_flex_direction_column":align_col,"vertical_alignment_flex_direction_column":"center","gap":gap,
        "section_width":width,"section_height":height,"section_height_custom":50,"background_media":"none","background_color":bg,
        "video_position":"cover","background_image_position":"cover","toggle_overlay":False,"overlay_color":"#00000026","overlay_style":"solid",
        "gradient_direction":"to top","border":"none","border_width":1,"border_opacity":100,"border_color":"","border_radius":0,
        "padding-block-start":pad[0],"padding-block-end":pad[1]}}

import re as _re
_SCHEMA_FILES = {"group":"blocks/group.liquid","text":"blocks/text.liquid","button":"blocks/button.liquid","image":"blocks/image.liquid","icon":"blocks/icon.liquid","section":"sections/section.liquid"}
_DEFAULTS = {}
for _t,_f in _SCHEMA_FILES.items():
    _s = json.loads(_re.search(r'{%-?\s*schema\s*-?%}(.*?){%-?\s*endschema', open('../original/'+_f).read(), _re.S).group(1))
    _DEFAULTS[_t] = {st['id']: st.get('default') for st in _s.get('settings', []) if 'id' in st}

def prune(node):
    t = node.get("type")
    if t in _DEFAULTS and "settings" in node:
        dfl = _DEFAULTS[t]
        node["settings"] = {k: v for k, v in node["settings"].items() if not (k in dfl and dfl[k] is not None and dfl[k] == v)}
    for b in node.get("blocks", {}).values():
        prune(b)
    return node

def dump_pruned(d, f):
    d = copy.deepcopy(d)
    for s in d["sections"].values(): prune(s)
    dump(d, f)

def liquid(code):
    return {"type":"custom-liquid","settings":{"custom_liquid":code},"blocks":{}}

_KIT_CALC = ("{%- assign kp = closest.product | default: product -%}"
             "{%- assign k_items = kp.metafields.custom.incluye.value -%}"
             "{%- if k_items -%}{%- assign k_total = 0 -%}"
             "{%- for k_p in k_items -%}{%- assign k_total = k_total | plus: k_p.price -%}{%- endfor -%}"
             "{%- assign k_save = k_total | minus: kp.price -%}")
# Ahorro real del kit, calculado con los precios actuales de sus piezas (solo aparece si existe ahorro)
AHORRO_CARD = liquid(_KIT_CALC + "{%- if k_save > 0 -%}<p style=\"margin:2px 0 0;font-size:0.8125rem;font-weight:600;color:#B6462B\">Ahorras {{ k_save | money }} vs. por separado</p>{%- endif -%}{%- endif -%}")
AHORRO_PDP = liquid(_KIT_CALC + "{%- if k_save > 0 -%}<p style=\"margin:4px 0 0;display:inline-block;padding:6px 10px;border-radius:4px;background:rgba(182,70,43,.08);color:#B6462B;font-size:0.875rem;font-weight:600\">Ahorras {{ k_save | money }} <span style=\"font-weight:400;color:#57554C\">· por separado: <s>{{ k_total | money }}</s></span></p>{%- endif -%}{%- endif -%}")

def payment_icons(align="flex-start"):
    return {"type":"payment-icons","settings":{"horizontal_alignment":align,"gap":8,"padding-block-start":0,"padding-block-end":0,"padding-inline-start":0,"padding-inline-end":0},"blocks":{}}
