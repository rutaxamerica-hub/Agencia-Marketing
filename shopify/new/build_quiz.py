from lib import *
q = load('../original/templates/page.diagnostico.json')
blk = q['sections']['main']['blocks']['quiz']['settings']
L = blk['custom_liquid']
R = [
 ('<p class="eje-quiz__kicker">Diagnóstico gratis · 2 minutos</p>', '<p class="eje-quiz__kicker">Diagnóstico gratis · 4 preguntas · Sin registro</p>'),
 ('<h1 class="eje-quiz__title">Encuentra tu protocolo EJE</h1>', '<h1 class="eje-quiz__title">Descubre qué necesitas en 2 minutos</h1>'),
 ('<p class="eje-quiz__sub">Responde 4 preguntas rápidas. Al final te decimos exactamente qué producto necesitas — con respaldo de un kinesiólogo, no una recomendación al azar.</p>',
  '<p class="eje-quiz__sub">Responde 4 preguntas y te recomendamos un producto concreto, con la razón de por qué.</p>'),
 ('data-quiz-start>Empezar diagnóstico</button>', 'data-quiz-start>Empezar</button>'),
 ('<legend>¿Dónde sientes más molestia?</legend>', '<legend>¿Cuándo aparece la molestia?</legend>'),
 ('<span>En el escritorio / oficina en casa</span>', '<span>Trabajando en el escritorio</span>'),
 ('<span>Después de entrenar o hacer deporte</span>', '<span>Después de entrenar o hacer deporte</span>'),
 ('<span>Ambas situaciones</span>', '<span>En ambos momentos</span>'),
 ('<legend>¿Dónde te duele más?</legend>', '<legend>¿En qué zona la sientes más?</legend>'),
 ('<span>Todo el cuerpo, en general</span>', '<span>En varias zonas</span>'),
 ('<legend>¿Qué tan seguido te molesta?</legend>', '<legend>¿Qué tan seguido?</legend>'),
 ('<span>Prevenir el dolor antes de que empiece</span>', '<span>Prevenir molestias</span>'),
 ('<span>Aliviar una molestia que ya tengo</span>', '<span>Aliviar una molestia que ya tengo</span>'),
 ('<span>Recuperarme más rápido después de esfuerzo físico</span>', '<span>Recuperarme mejor después de entrenar</span>'),
 ('<p class="eje-quiz__kicker" data-result-kicker>Tu diagnóstico</p>', '<p class="eje-quiz__kicker" data-result-kicker>Tu recomendación</p>'),
 ('<p>Estamos afinando el catálogo para tu perfil. Mientras tanto, explora todos nuestros productos:</p>', '<p>No encontramos una recomendación exacta para tu perfil. Revisa el catálogo o escríbenos y te ayudamos a elegir.</p>'),
 ('href="/collections/all">Ver todos los productos</a>', 'href="/collections/all">Ver productos</a>'),
 ('data-quiz-restart>Volver a hacer el diagnóstico</button>', 'data-quiz-restart>Repetir diagnóstico</button>'),
 # copy de resultados: más simple y sin promesas médicas
 ('desc: "Tu perfil indica tensión por postura de escritorio, concentrada en cuello y hombros. Un corrector de postura ajustable + protocolo de movilidad diario es lo que más te va a ayudar."',
  'desc: "Tu molestia aparece en el escritorio y se concentra en cuello y hombros. Parte con un recordatorio de postura y pausas de movilidad."'),
 ('desc: "Pasas muchas horas sentado y la zona lumbar se resiente. Necesitas soporte lumbar activo y pausas de movimiento guiadas."',
  'desc: "Pasas muchas horas sentado y lo sientes en la espalda baja. Lo primero es darle apoyo a esa zona en tu silla."'),
 ('desc: "Tu diagnóstico apunta a dolor relacionado con trabajo de escritorio. El Kit Setup Correcto (soporte lumbar + reposapiés) es tu mejor punto de partida."',
  'desc: "Tu molestia está ligada al trabajo de escritorio. El Kit Setup Correcto (soporte lumbar + reposapiés) es el mejor punto de partida."'),
 ('desc: "El desgaste post-entrenamiento se concentra en piernas y articulaciones. Una banda de compresión favorece la circulación y acelera tu vuelta al día siguiente."',
  'desc: "Después de entrenar lo sientes sobre todo en las piernas. La compresión es un buen complemento para tu recuperación."'),
 ('desc: "Entrenas seguido y tu cuerpo necesita recuperarse mejor. Este rodillo está pensado para reducir el dolor muscular post-esfuerzo con liberación miofascial diaria."',
  'desc: "Entrenas seguido y quieres recuperarte mejor. Un rodillo para automasaje es la base de cualquier rutina post-entreno."'),
 ('desc: "Tu día combina trabajo sentado y actividad física. El Kit Setup Correcto te da la base ergonómica correcta durante el día; luego puedes sumar recuperación activa después de entrenar."',
  'desc: "Tu día combina horas sentado y entrenamiento. Empieza por el escritorio con el Kit Setup Correcto; después puedes sumar recuperación."'),
 ('desc: "Con base en tus respuestas, el Kit Setup Correcto es el punto de partida más seguro y universal para empezar."',
  'desc: "Según tus respuestas, el Kit Setup Correcto es el punto de partida más seguro."'),
 ('title: "Corrector de Postura — Cuello y Hombros"', 'title: "Corrector de Postura Ajustable"'),
]
for a,b in R:
    assert a in L, a[:60]
    L = L.replace(a,b)

# JS: auto-avance al elegir, botón final "Ver mi resultado", ocultar imagen vacía
js_old = '''    function showQuestion(index) {
      questions.forEach(function (q, i) {
        q.hidden = i !== index;
      });
      var backBtn = root.querySelector("[data-quiz-back]");
      backBtn.hidden = index === 0;
      updateProgress();
    }'''
js_new = '''    function showQuestion(index) {
      questions.forEach(function (q, i) {
        q.hidden = i !== index;
      });
      var backBtn = root.querySelector("[data-quiz-back]");
      backBtn.hidden = index === 0;
      root.querySelector("[data-quiz-next]").textContent = index === questions.length - 1 ? "Ver mi resultado" : "Siguiente";
      updateProgress();
    }

    /* Al elegir una opción avanzamos solos (menos clics); "Siguiente" sigue disponible. */
    questions.forEach(function (q, i) {
      q.addEventListener("change", function () {
        if (i !== currentIndex || i === questions.length - 1) return;
        setTimeout(function () { root.querySelector("[data-quiz-next]").click(); }, 220);
      });
    });'''
assert js_old in L; L = L.replace(js_old, js_new)
img_old = '''        root.querySelector("[data-result-product-image]").src = product.image || "";'''
img_new = '''        var img = root.querySelector("[data-result-product-image]");
        img.hidden = !product.image;
        if (product.image) { img.src = product.image; img.alt = product.title; }'''
assert img_old in L; L = L.replace(img_old, img_new)
L = L.replace('<a class="eje-quiz__btn eje-quiz__btn--primary" data-result-product-link href="#">Ver producto</a>',
              '<a class="eje-quiz__btn eje-quiz__btn--primary" data-result-product-link href="#">Ver producto recomendado</a>')

# CSS: botones táctiles de 48px, opciones más limpias, títulos contenidos en mobile
css_old = '''  .eje-quiz__btn {
    display: inline-flex;'''
css_new = '''  .eje-quiz__btn {
    min-height: 48px;
    display: inline-flex;'''
assert css_old in L; L = L.replace(css_old, css_new)
L = L.replace('''    border-radius: 2px;
    font-size: 0.95rem;''', '''    border-radius: 4px;
    font-size: 0.95rem;''')
L = L.replace('''    padding: 16px;
    border: 1px solid #d6d2c6;
    border-radius: 4px;
    cursor: pointer;''', '''    padding: 16px 18px;
    border: 1px solid #d6d2c6;
    border-radius: 6px;
    background: #f8f6f2;
    cursor: pointer;''')
L = L.replace('''  .eje-quiz {
    max-width: 640px;
    margin: 0 auto;
    padding: 48px 20px;''', '''  .eje-quiz {
    max-width: 600px;
    margin: 0 auto;
    padding: 72px 20px 88px;''')
L = L.replace('''    font-size: clamp(28px, 5vw, 42px);''', '''    font-size: clamp(30px, 5vw, 44px);
    text-wrap: balance;''')
for h in ['postura','lumbar','kit','compresion','rodillo']:
    old = "url: {% if product_" + h + ".url != blank %}"
    assert old in L, h
    L = L.replace(old, "variant: {{ product_" + h + ".selected_or_first_available_variant.id | json }},\n        " + old)
old = """        <a class="eje-quiz__btn eje-quiz__btn--primary" data-result-product-link href="#">Ver producto recomendado</a>"""
new = """        <p class="eje-quiz__includes">Incluye guía de uso: cómo, cuándo y dónde usarlo.</p>
        <div class="eje-quiz__result-ctas">
          <a class="eje-quiz__btn eje-quiz__btn--primary" data-result-add href="#">Agregar al carrito</a>
          <a class="eje-quiz__btn eje-quiz__btn--ghost" data-result-product-link href="#">Ver detalle</a>
        </div>"""
assert old in L; L = L.replace(old, new)
old = """        root.querySelector("[data-result-product-link]").href = product.url;"""
new = old + """
        var add = root.querySelector("[data-result-add]");
        add.hidden = !product.variant;
        if (product.variant) add.href = "/cart/add?id=" + product.variant + "&quantity=1";"""
assert old in L; L = L.replace(old, new)
old = """  .eje-quiz [hidden] {"""
new = """  .eje-quiz__includes {
    font-size: 0.85rem;
    color: #57554c;
    margin: 0 0 14px;
  }

  .eje-quiz__result-ctas {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }

  .eje-quiz [hidden] {"""
assert old in L; L = L.replace(old, new)
blk['custom_liquid'] = L
dump(q, 'templates/page.diagnostico.json')
print('ok', len(L))
