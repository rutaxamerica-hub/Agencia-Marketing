# Contenido nuevo de productos EJE. Solo información ya existente en la tienda.
def desc(intro, ideal, incluye=None, extra=None, link=None):
    h = f"<p>{intro}</p>"
    if incluye:
        h += "<p><strong>Incluye</strong></p><ul>" + "".join(f"<li>{i}</li>" for i in incluye) + "</ul>"
    h += "<p><strong>Ideal si</strong></p><ul>" + "".join(f"<li>{i}</li>" for i in ideal) + "</ul>"
    if extra:
        h += f"<p>{extra}</p>"
    if link:
        h += f"<p>{link}</p>"
    return h

KIT_SETUP = '<a href="/products/kit-setup-correcto">Kit Setup Correcto</a>'
KIT_ESC = '<a href="/products/kit-escritorio-completo">Kit Escritorio Completo</a>'
KIT_REC = '<a href="/products/kit-recuperacion-post-entreno">Kit Recuperación Post-Entreno</a>'
KIT_POS = '<a href="/products/kit-postura-movilidad">Kit Postura + Movilidad</a>'

P = {
 "gid://shopify/Product/15394571845947": dict(  # Soporte Lumbar
   bajada="Apoyo para la espalda baja en tu silla de trabajo.",
   html=desc("Cojín lumbar con correa ajustable. Se fija a tu silla y acompaña la curva de la espalda baja durante las horas sentado.",
     ["Pasas muchas horas sentado.", "Terminas el día con la espalda baja cargada."],
     link=f"También viene en el {KIT_SETUP}, junto al reposapiés.")),
 "gid://shopify/Product/15394572501307": dict(  # Reposapiés
   bajada="Pies bien apoyados mientras trabajas sentado.",
   html=desc("Reposapiés con inclinación ajustable. Te permite apoyar bien los pies y bajar la tensión en piernas y espalda baja en jornadas largas.",
     ["Tus pies no llegan cómodos al suelo.", "Pasas jornadas largas sentado."],
     link=f"También viene en el {KIT_SETUP}, junto al soporte lumbar.")),
 "gid://shopify/Product/15394572566843": dict(  # Soporte laptop
   bajada="Sube el notebook a la altura de tus ojos.",
   html=desc("Brazo articulado que eleva el notebook a la altura de los ojos. Dejas de mirar hacia abajo y liberas espacio en el escritorio.",
     ["Trabajas con notebook varias horas al día.", "Terminas la jornada con el cuello tenso."],
     link=f"También viene en el {KIT_ESC}.")),
 "gid://shopify/Product/15394572599611": dict(  # Cojín asiento
   bajada="Asiento más cómodo en jornadas largas.",
   html=desc("Cojín de memory foam con corte anatómico. Reparte el peso y reduce la presión sobre coxis y glúteos al estar sentado.",
     ["Tu silla se vuelve incómoda después de unas horas.", "Sientes molestia en el coxis al estar sentado."],
     extra="Como todo memory foam, pierde firmeza con el uso. Conviene renovarlo con el tiempo.",
     link=f"También viene en el {KIT_ESC}.")),
 "gid://shopify/Product/15394572632379": dict(  # Lámpara
   bajada="Luz regulable para trabajar sin cansar la vista.",
   html=desc("Lámpara LED de escritorio con temperatura de color regulable. Sin parpadeo ni deslumbramiento.",
     ["Pasas muchas horas frente a la pantalla.", "La luz de tu escritorio te cansa la vista."])),
 "gid://shopify/Product/15394572697915": dict(  # Organizador cables
   bajada="Cables ordenados y enchufes a mano.",
   html=desc("Sistema para ordenar cables más una mini regleta de escritorio. Tu setup queda limpio y sin enredos.",
     ["Tienes cables a la vista en el escritorio.", "Necesitas enchufes más cerca."],
     link=f"También viene en el {KIT_ESC}.")),
 "gid://shopify/Product/15394572730683": dict(  # Corrector postura
   bajada="Un recordatorio para mantener los hombros en su lugar.",
   html=desc("Banda ajustable que te recuerda mantener los hombros en una postura neutra durante el día.",
     ["Te encorvas frente al computador sin darte cuenta.", "Buscas una primera solución simple."],
     extra="La guía de uso te explica cuándo conviene usar un corrector y cuándo no.",
     link=f"También viene en el {KIT_POS}.")),
 "gid://shopify/Product/15394573418811": dict(  # Pistola masaje
   bajada="Masaje de percusión con protocolo de uso por deporte.",
   html=desc("Pistola de masaje de percusión para después de entrenar. No es solo el aparato: incluye un protocolo de uso por deporte, avalado por kinesiólogo, que te dice cómo y cuándo usarla.",
     ["Entrenas varias veces por semana.", "Quieres una rutina de recuperación con instrucciones claras."],
     extra="Es el único producto con motor de nuestro catálogo, por eso pasa por un control de calidad reforzado.")),
 "gid://shopify/Product/15394574139707": dict(  # Rodillo
   bajada="Automasaje antes o después de entrenar.",
   html=desc("Rodillo de espuma con superficie texturizada para liberación miofascial (automasaje) antes o después de entrenar.",
     ["Entrenas seguido y terminas con los músculos cargados.", "Quieres algo simple para usar a diario."],
     link=f"También viene en el {KIT_REC}.")),
 "gid://shopify/Product/15394574762299": dict(  # Bandas
   bajada="Bandas de distinta resistencia para movilidad y activación.",
   html=desc("Set de bandas elásticas de distintas resistencias para movilidad, activación y trabajo de piernas.",
     ["Quieres activar el cuerpo antes de entrenar.", "Buscas ejercicios de movilidad en casa."],
     link=f"También viene en el {KIT_REC}.")),
 "gid://shopify/Product/15394575515963": dict(  # Bola doble
   bajada="Automasaje preciso en cuello, espalda y glúteos.",
   html=desc("Bola doble tipo “peanut” para liberar tensión en cuello, espalda y glúteos, con una precisión que un rodillo no logra.",
     ["Tienes tensión en puntos específicos.", "Quieres algo pequeño para usar en casa o llevar al gimnasio."])),
 "gid://shopify/Product/15394576138555": dict(  # Compresión
   bajada="Compresión para piernas después de entrenar.",
   html=desc("Manga de compresión textil para piernas, pensada para la recuperación después de entrenar.",
     ["Entrenas piernas con frecuencia.", "Quieres sumar compresión a tu rutina de recuperación."])),
 "gid://shopify/Product/15394576367931": dict(  # Cinta estiramiento
   bajada="Estiramientos guiados, con posiciones impresas.",
   html=desc("Correa de estiramiento con una guía impresa de posiciones. Te ayuda a estirar bien, sin necesidad de un instructor.",
     ["Pasas muchas horas sentado y te sientes rígido.", "Quieres una rutina corta de movilidad en casa."],
     link=f"También viene en el {KIT_POS}.")),
 "gid://shopify/Product/15394576400699": dict(  # Magnesio
   bajada="Magnesio de uso tópico para después de entrenar.",
   html=desc("Spray de magnesio para aplicar sobre la piel después de entrenar. Es de uso externo: no se ingiere.",
     ["Ya tienes una rutina de recuperación y quieres complementarla."],
     link=f"También viene en el {KIT_REC}.")),
 "gid://shopify/Product/15394576433467": dict(  # Kit Setup Correcto
   bajada="Soporte lumbar + reposapiés: la base de un escritorio cómodo.",
   html=desc("Las dos piezas base para trabajar sentado con buena postura, más una guía impresa para medir y ajustar tu puesto desde el primer día.",
     ["Trabajas sentado muchas horas.", "No sabes por dónde empezar. Es nuestra recomendación base."],
     incluye=['<a href="/products/soporte-lumbar-ajustable">Soporte Lumbar Ajustable</a>', '<a href="/products/reposapies-ergonomico-inclinable">Reposapiés Ergonómico Inclinable</a>', "Guía de medición impresa"])),
 "gid://shopify/Product/15394591965499": dict(  # Kit Escritorio
   bajada="Pantalla a la altura correcta, asiento cómodo y escritorio ordenado.",
   html=desc("Tres piezas que cambian cómo se siente trabajar sentado: pantalla a la altura de los ojos, un asiento que reparte el peso y cables en orden.",
     ["Estás armando tu escritorio de teletrabajo.", "Trabajas con notebook."],
     incluye=['<a href="/products/soporte-para-laptop-con-brazo-ajustable">Soporte para Laptop con Brazo Ajustable</a>', '<a href="/products/cojin-de-asiento-anatomico">Cojín de Asiento Anatómico</a>', '<a href="/products/organizador-de-cables-mini-regleta">Organizador de Cables + Mini Regleta</a>'])),
 "gid://shopify/Product/15394592096571": dict(  # Kit Recuperación
   bajada="Rodillo, bandas y magnesio: tu rutina post-entreno completa.",
   html=desc("Una rutina de recuperación completa: automasaje y movilidad con el rodillo y las bandas, y magnesio tópico para cerrar el día.",
     ["Entrenas con regularidad.", "Quieres recuperarte mejor entre sesiones, no solo estirar."],
     incluye=['<a href="/products/rodillo-de-espuma-texturizado">Rodillo de Espuma Texturizado</a>', '<a href="/products/set-de-bandas-de-resistencia-y-movilidad">Set de Bandas de Resistencia y Movilidad</a>', '<a href="/products/spray-de-magnesio-topico-post-entreno">Spray de Magnesio Tópico</a>'])),
 "gid://shopify/Product/15394592227643": dict(  # Kit Postura
   bajada="Corrector de postura + cinta de estiramiento guiada.",
   html=desc("Trabaja la postura desde dos frentes: un recordatorio durante el día y movilidad guiada para compensar las horas sentado.",
     ["Pasas muchas horas sentado.", "Ya resolviste tu escritorio y quieres trabajar el cuerpo."],
     incluye=['<a href="/products/corrector-de-postura-ajustable">Corrector de Postura Ajustable</a>', '<a href="/products/cinta-de-estiramiento-con-guia-de-posiciones">Cinta de Estiramiento con Guía de Posiciones</a>'])),
}
