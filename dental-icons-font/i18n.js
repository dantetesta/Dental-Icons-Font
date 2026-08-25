(() => {
  "use strict";

  const STORAGE_KEY = "dental-icons-language";
  const SUPPORTED = new Set(["pt-BR", "pt-PT", "en", "es"]);
  const LUSOPHONE_COUNTRIES = new Set(["PT", "AO", "CV", "GW", "MZ", "ST", "TL", "GQ", "MO"]);
  const SPANISH_COUNTRIES = new Set(["ES", "AR", "BO", "CL", "CO", "CR", "CU", "DO", "EC", "SV", "GT", "HN", "MX", "NI", "PA", "PY", "PE", "PR", "UY", "VE"]);

  // Source (pt-BR), English, Spanish, Portuguese (Portugal).
  const ENTRIES = [
    ["Dental Icons Font — escreva odontogramas", "Dental Icons Font — write odontograms", "Dental Icons Font — escribe odontogramas", "Dental Icons Font — escreva odontogramas"],
    ["Dental Icons Font: escreva odontogramas no Word, PowerPoint, Pages, LibreOffice e na web. Criação de Dante Testa.", "Dental Icons Font: write odontograms in Word, PowerPoint, Pages, LibreOffice and on the web. Created by Dante Testa.", "Dental Icons Font: escribe odontogramas en Word, PowerPoint, Pages, LibreOffice y la web. Creada por Dante Testa.", "Dental Icons Font: escreva odontogramas no Word, PowerPoint, Pages, LibreOffice e na web. Criação de Dante Testa."],
    ["Ir para o simulador", "Skip to the simulator", "Ir al simulador", "Ir para o simulador"],
    ["Navegação principal", "Main navigation", "Navegación principal", "Navegação principal"],
    ["Testar", "Try it", "Probar", "Testar"],
    ["Como usar", "How it works", "Cómo usar", "Como utilizar"],
    ["Formatos", "Formats", "Formatos", "Formatos"],
    ["Baixar fonte", "Download font", "Descargar fuente", "Descarregar fonte"],
    ["Tipografia odontológica brasileira", "Brazilian dental typography", "Tipografía odontológica brasileña", "Tipografia odontológica brasileira"],
    ["Uma fonte para escrever o que o", "A font for writing what the", "Una fuente para escribir lo que el", "Um tipo de letra para escrever o que o"],
    ["dentista vê.", "dentist sees.", "dentista ve.", "dentista vê."],
    ["Dentes em perfil e vista oclusal, organizados no teclado para criar odontogramas em documentos, apresentações, aplicativos e sites.", "Profile and occlusal tooth views, organized on the keyboard for creating odontograms in documents, presentations, apps and websites.", "Dientes de perfil y vista oclusal, organizados en el teclado para crear odontogramas en documentos, presentaciones, aplicaciones y sitios web.", "Dentes de perfil e em vista oclusal, organizados no teclado para criar odontogramas em documentos, apresentações, aplicações e sites."],
    ["Experimentar agora", "Try it now", "Probar ahora", "Experimentar agora"],
    ["Baixar para instalar", "Download to install", "Descargar para instalar", "Descarregar para instalar"],
    ["glifos anatômicos", "anatomical glyphs", "glifos anatómicos", "glifos anatómicos"],
    ["leituras clínicas", "clinical views", "lecturas clínicas", "leituras clínicas"],
    ["escala vetorial", "vector scaling", "escala vectorial", "escala vetorial"],
    ["ESPÉCIME INTERATIVO", "INTERACTIVE SPECIMEN", "ESPÉCIMEN INTERACTIVO", "ESPÉCIME INTERATIVO"],
    ["64 GLIFOS / 4 VISTAS", "64 GLYPHS / 4 VIEWS", "64 GLIFOS / 4 VISTAS", "64 GLIFOS / 4 VISTAS"],
    ["SOB O CURSOR", "UNDER THE CURSOR", "BAJO EL CURSOR", "SOB O CURSOR"],
    ["Mova o cursor", "Move the cursor", "Mueve el cursor", "Mova o cursor"],
    ["para observar", "to explore", "para explorar", "para observar"],
    ["Compatibilidade", "Compatibility", "Compatibilidad", "Compatibilidade"],
    ["Uma instalação. O mesmo idioma visual em:", "One installation. The same visual language in:", "Una instalación. El mismo lenguaje visual en:", "Uma instalação. A mesma linguagem visual em:"],
    ["Sites", "Websites", "Sitios", "Sites"],
    ["apps", "apps", "aplicaciones", "aplicações"],
    ["Laboratório interativo", "Interactive lab", "Laboratorio interactivo", "Laboratório interativo"],
    ["Digite. Configure.", "Type. Configure.", "Escribe. Configura.", "Escreva. Configure."],
    ["Use de verdade.", "Use it for real.", "Úsala de verdad.", "Utilize de verdade."],
    ["Teste a fonte nos cenários mais comuns do consultório. Cada ajuste acontece em tempo real.", "Test the font in the most common clinical scenarios. Every adjustment happens in real time.", "Prueba la fuente en los escenarios más habituales de la clínica. Cada ajuste ocurre en tiempo real.", "Teste o tipo de letra nos cenários mais comuns do consultório. Cada ajuste acontece em tempo real."],
    ["Controles do simulador", "Simulator controls", "Controles del simulador", "Controlos do simulador"],
    ["Sequência dentária", "Dental sequence", "Secuencia dental", "Sequência dentária"],
    ["Misture M1 e m1 para ver perfil e face juntos. Use “|” para a linha média.", "Mix M1 and m1 to see profile and occlusal views together. Use “|” for the midline.", "Combina M1 y m1 para ver perfil y cara oclusal a la vez. Usa “|” para la línea media.", "Combine M1 e m1 para ver perfil e face em conjunto. Utilize “|” para a linha média."],
    ["Sequências prontas", "Ready-made sequences", "Secuencias listas", "Sequências predefinidas"],
    ["Arcada completa", "Full arch", "Arcada completa", "Arcada completa"],
    ["Anteriores", "Anterior teeth", "Anteriores", "Anteriores"],
    ["Posteriores", "Posterior teeth", "Posteriores", "Posteriores"],
    ["Meia arcada", "Half arch", "Media arcada", "Meia arcada"],
    ["Leitura clínica", "Clinical reading", "Lectura clínica", "Leitura clínica"],
    ["Arcada", "Arch", "Arcada", "Arcada"],
    ["Superior", "Upper", "Superior", "Superior"],
    ["Inferior", "Lower", "Inferior", "Inferior"],
    ["Caixa / vista", "Case / view", "Caja / vista", "Caixa / vista"],
    ["Digitado", "As typed", "Escrito", "Escrito"],
    ["Perfil", "Profile", "Perfil", "Perfil"],
    ["Oclusal", "Occlusal", "Oclusal", "Oclusal"],
    ["Composição", "Composition", "Composición", "Composição"],
    ["Tamanho", "Size", "Tamaño", "Tamanho"],
    ["Espaço", "Spacing", "Espacio", "Espaço"],
    ["Linha", "Line", "Línea", "Linha"],
    ["Curva dental", "Dental curve", "Curva dental", "Curva dentária"],
    ["Compacta", "Compact", "Compacta", "Compacta"],
    ["Aparência", "Appearance", "Apariencia", "Aspeto"],
    ["Cor do odontograma", "Odontogram color", "Color del odontograma", "Cor do odontograma"],
    ["Verde clínico", "Clinical green", "Verde clínico", "Verde clínico"],
    ["Azul", "Blue", "Azul", "Azul"],
    ["Grafite", "Graphite", "Grafito", "Grafite"],
    ["Vinho", "Wine", "Vino", "Bordô"],
    ["Mostrar códigos", "Show codes", "Mostrar códigos", "Mostrar códigos"],
    ["Contexto de visualização", "Preview context", "Contexto de visualización", "Contexto de visualização"],
    ["Documento", "Document", "Documento", "Documento"],
    ["Sistema web", "Web system", "Sistema web", "Sistema web"],
    ["Impressão", "Print", "Impresión", "Impressão"],
    ["Ficha clínica — Odontograma", "Clinical record — Odontogram", "Ficha clínica — Odontograma", "Ficha clínica — Odontograma"],
    ["Copiar sequência", "Copy sequence", "Copiar secuencia", "Copiar sequência"],
    ["Exportar PNG", "Export PNG", "Exportar PNG", "Exportar PNG"],
    ["Usar a fonte no meu computador", "Use the font on my computer", "Usar la fuente en mi ordenador", "Utilizar o tipo de letra no meu computador"],
    ["Entenda em um segundo", "Understand it in one second", "Entiéndelo en un segundo", "Perceba num segundo"],
    ["Um código.", "One code.", "Un código.", "Um código."],
    ["Duas leituras.", "Two views.", "Dos lecturas.", "Duas leituras."],
    ["Digite o código de um dente e compare simultaneamente o perfil e a face oclusal. A única mudança no teclado é usar maiúscula ou minúscula.", "Type a tooth code and compare its profile and occlusal views side by side. The only keyboard change is uppercase or lowercase.", "Escribe el código de un diente y compara simultáneamente el perfil y la cara oclusal. El único cambio en el teclado es usar mayúscula o minúscula.", "Escreva o código de um dente e compare simultaneamente o perfil e a face oclusal. A única alteração no teclado é utilizar maiúscula ou minúscula."],
    ["Digite um código", "Type a code", "Escribe un código", "Escreva um código"],
    ["Códigos dentários", "Dental codes", "Códigos dentales", "Códigos dentários"],
    ["Lado", "Side", "Lado", "Lado"],
    ["Esquerdo", "Left", "Izquierdo", "Esquerdo"],
    ["Direito", "Right", "Derecho", "Direito"],
    ["Maiúscula mostra o perfil.", "Uppercase shows the profile.", "La mayúscula muestra el perfil.", "A maiúscula mostra o perfil."],
    ["Minúscula mostra a face.", "Lowercase shows the occlusal view.", "La minúscula muestra la cara oclusal.", "A minúscula mostra a face."],
    ["MAIÚSCULA", "UPPERCASE", "MAYÚSCULA", "MAIÚSCULA"],
    ["MINÚSCULA", "LOWERCASE", "MINÚSCULA", "MINÚSCULA"],
    ["VISTA 01", "VIEW 01", "VISTA 01", "VISTA 01"],
    ["VISTA 02", "VIEW 02", "VISTA 02", "VISTA 02"],
    ["Dente em perfil", "Tooth in profile", "Diente de perfil", "Dente de perfil"],
    ["Coroa e raízes representadas em um único glifo.", "Crown and roots represented in a single glyph.", "Corona y raíces representadas en un único glifo.", "Coroa e raízes representadas num único glifo."],
    ["MESMO DENTE", "SAME TOOTH", "MISMO DIENTE", "MESMO DENTE"],
    ["Face oclusal", "Occlusal surface", "Cara oclusal", "Face oclusal"],
    ["Superfície e sulcos do mesmo elemento dental.", "Surface and grooves of the same dental element.", "Superficie y surcos del mismo elemento dental.", "Superfície e sulcos do mesmo elemento dentário."],
    ["Pronta para acompanhar seu trabalho", "Ready for your workflow", "Lista para tu trabajo", "Pronta para acompanhar o seu trabalho"],
    ["Do laudo impresso", "From the printed report", "Del informe impreso", "Do relatório impresso"],
    ["ao software da clínica.", "to your clinic software.", "al software de la clínica.", "ao software da clínica."],
    ["Instale no Windows ou Linux e procure por ODONTO ABOVE ou ODONTO UNDER.", "Install on Windows or Linux and look for ODONTO ABOVE or ODONTO UNDER.", "Instala en Windows o Linux y busca ODONTO ABOVE u ODONTO UNDER.", "Instale no Windows ou Linux e procure ODONTO ABOVE ou ODONTO UNDER."],
    ["Apple & criação gráfica", "Apple & graphic design", "Apple y diseño gráfico", "Apple e criação gráfica"],
    ["Use os mesmos nomes no macOS, Pages, Keynote e aplicativos compatíveis.", "Use the same names in macOS, Pages, Keynote and compatible apps.", "Usa los mismos nombres en macOS, Pages, Keynote y aplicaciones compatibles.", "Utilize os mesmos nomes no macOS, Pages, Keynote e aplicações compatíveis."],
    ["Sites & sistemas", "Websites & systems", "Sitios y sistemas", "Sites e sistemas"],
    ["Integre via", "Integrate with", "Integra mediante", "Integre através de"],
    ["usando os aliases web documentados abaixo.", "using the web aliases documented below.", "usando los alias web documentados a continuación.", "utilizando os aliases web documentados abaixo."],
    ["Nomes oficiais das famílias", "Official family names", "Nombres oficiales de las familias", "Nomes oficiais das famílias"],
    ["É assim que a fonte aparece no seu aplicativo.", "This is how the font appears in your app.", "Así aparece la fuente en tu aplicación.", "É assim que o tipo de letra aparece na sua aplicação."],
    ["Depois de instalar, procure exatamente por estes nomes no seletor de fontes do Pages, Keynote, Word, PowerPoint, LibreOffice ou OpenOffice.", "After installation, look for these exact names in the font selector in Pages, Keynote, Word, PowerPoint, LibreOffice or OpenOffice.", "Después de instalar, busca exactamente estos nombres en el selector de fuentes de Pages, Keynote, Word, PowerPoint, LibreOffice u OpenOffice.", "Depois da instalação, procure exatamente estes nomes no seletor de tipos de letra do Pages, Keynote, Word, PowerPoint, LibreOffice ou OpenOffice."],
    ["ARCADA SUPERIOR", "UPPER ARCH", "ARCADA SUPERIOR", "ARCADA SUPERIOR"],
    ["ARCADA INFERIOR", "LOWER ARCH", "ARCADA INFERIOR", "ARCADA INFERIOR"],
    ["Nome exibido nos aplicativos de texto e criação.", "Name displayed in text and design apps.", "Nombre mostrado en aplicaciones de texto y diseño.", "Nome apresentado nas aplicações de texto e criação."],
    ["Arquivo macOS", "macOS file", "Archivo macOS", "Ficheiro macOS"],
    ["Arquivo Windows/Linux", "Windows/Linux file", "Archivo Windows/Linux", "Ficheiro Windows/Linux"],
    ["Alias web", "Web alias", "Alias web", "Alias web"],
    ["Importante:", "Important:", "Importante:", "Importante:"],
    ["ABOVE = superior e UNDER = inferior. Os aliases “Dental Icons Upper” e “Dental Icons Lower” são usados somente no CSS da webfont fornecida no pacote.", "ABOVE = upper and UNDER = lower. The “Dental Icons Upper” and “Dental Icons Lower” aliases are used only in the webfont CSS included in the package.", "ABOVE = superior y UNDER = inferior. Los alias “Dental Icons Upper” y “Dental Icons Lower” se usan únicamente en el CSS de la webfont incluida en el paquete.", "ABOVE = superior e UNDER = inferior. Os aliases “Dental Icons Upper” e “Dental Icons Lower” são utilizados apenas no CSS da webfont incluída no pacote."],
    ["Instalação guiada", "Installation guide", "Instalación guiada", "Instalação guiada"],
    ["Baixou.", "Downloaded.", "Descargada.", "Descarregou."],
    ["Instalou.", "Installed.", "Instalada.", "Instalou."],
    ["Digitou.", "Typed.", "Escrita.", "Escreveu."],
    ["Escolha seu ambiente para ver o passo a passo.", "Choose your environment for step-by-step instructions.", "Elige tu entorno para ver las instrucciones paso a paso.", "Escolha o seu ambiente para ver as instruções passo a passo."],
    ["Plataforma", "Platform", "Plataforma", "Plataforma"],
    ["Abra Windows-Linux", "Open Windows-Linux", "Abre Windows-Linux", "Abra Windows-Linux"],
    ["Use somente os dois arquivos TTF dessa pasta.", "Use only the two TTF files in this folder.", "Usa únicamente los dos archivos TTF de esta carpeta.", "Utilize apenas os dois ficheiros TTF desta pasta."],
    ["Instale as duas famílias", "Install both families", "Instala las dos familias", "Instale as duas famílias"],
    ["Selecione “Instalar para todos os usuários” quando disponível.", "Select “Install for all users” when available.", "Selecciona “Instalar para todos los usuarios” cuando esté disponible.", "Selecione “Instalar para todos os utilizadores” quando disponível."],
    ["Reabra seu aplicativo", "Reopen your app", "Vuelve a abrir la aplicación", "Reabra a aplicação"],
    ["Selecione ODONTO ABOVE (superior) ou ODONTO UNDER (inferior).", "Select ODONTO ABOVE (upper) or ODONTO UNDER (lower).", "Selecciona ODONTO ABOVE (superior) u ODONTO UNDER (inferior).", "Selecione ODONTO ABOVE (superior) ou ODONTO UNDER (inferior)."],
    ["Instale os dois arquivos OTF", "Install both OTF files", "Instala los dos archivos OTF", "Instale os dois ficheiros OTF"],
    ["Upper para a arcada superior e Lower para a inferior. Se já existirem, escolha “Substituir”.", "Upper is for the upper arch and Lower for the lower arch. If they already exist, choose “Replace”.", "Upper corresponde a la arcada superior y Lower a la inferior. Si ya existen, elige “Reemplazar”.", "Upper corresponde à arcada superior e Lower à inferior. Se já existirem, escolha “Substituir”."],
    ["Encerre e reabra o Pages", "Quit and reopen Pages", "Cierra y vuelve a abrir Pages", "Encerre e reabra o Pages"],
    ["Use Command-Q para o aplicativo atualizar a lista de fontes.", "Use Command-Q so the app refreshes its font list.", "Usa Command-Q para que la aplicación actualice la lista de fuentes.", "Utilize Command-Q para a aplicação atualizar a lista de tipos de letra."],
    ["Escolha a família legível", "Choose the readable family", "Elige la familia legible", "Escolha a família legível"],
    ["Use ODONTO ABOVE (superior) ou ODONTO UNDER (inferior), com ligaturas ativas.", "Use ODONTO ABOVE (upper) or ODONTO UNDER (lower), with ligatures enabled.", "Usa ODONTO ABOVE (superior) u ODONTO UNDER (inferior), con las ligaduras activadas.", "Utilize ODONTO ABOVE (superior) ou ODONTO UNDER (inferior), com as ligaturas ativas."],
    ["Instale no sistema", "Install on the system", "Instala en el sistema", "Instale no sistema"],
    ["Use o gerenciador de fontes do seu computador.", "Use your computer's font manager.", "Usa el gestor de fuentes de tu ordenador.", "Utilize o gestor de tipos de letra do computador."],
    ["Reinicie a suíte", "Restart the suite", "Reinicia la suite", "Reinicie o pacote"],
    ["Feche também o Quickstarter, se estiver ativo.", "Also close Quickstarter if it is running.", "Cierra también Quickstarter si está activo.", "Feche também o Quickstarter, caso esteja ativo."],
    ["Selecione a arcada", "Select the arch", "Selecciona la arcada", "Selecione a arcada"],
    ["Procure por ODONTO ABOVE (superior) ou ODONTO UNDER (inferior).", "Look for ODONTO ABOVE (upper) or ODONTO UNDER (lower).", "Busca ODONTO ABOVE (superior) u ODONTO UNDER (inferior).", "Procure ODONTO ABOVE (superior) ou ODONTO UNDER (inferior)."],
    ["Copiar", "Copy", "Copiar", "Copiar"],
    ["Feita para dentistas", "Made for dentists", "Hecha para dentistas", "Criada para dentistas"],
    ["Seu próximo odontograma começa com uma tecla.", "Your next odontogram starts with one keystroke.", "Tu próximo odontograma empieza con una tecla.", "O seu próximo odontograma começa com uma tecla."],
    ["Dental Icons Font para documentos, apresentações e produtos digitais.", "Dental Icons Font for documents, presentations and digital products.", "Dental Icons Font para documentos, presentaciones y productos digitales.", "Dental Icons Font para documentos, apresentações e produtos digitais."],
    ["Baixar Dental Icons Font", "Download Dental Icons Font", "Descargar Dental Icons Font", "Descarregar Dental Icons Font"],
    ["ODONTO ABOVE — superior", "ODONTO ABOVE — upper", "ODONTO ABOVE — superior", "ODONTO ABOVE — superior"],
    ["ODONTO UNDER — inferior", "ODONTO UNDER — lower", "ODONTO UNDER — inferior", "ODONTO UNDER — inferior"],
    ["TTF + OTF para desktop", "TTF + OTF for desktop", "TTF + OTF para escritorio", "TTF + OTF para computador"],
    ["WOFF2 + CSS para web", "WOFF2 + CSS for web", "WOFF2 + CSS para web", "WOFF2 + CSS para web"],
    ["Autor", "Author", "Autor", "Autor"],
    ["IDEALIZAÇÃO & DESENVOLVIMENTO", "CONCEPT & DEVELOPMENT", "CONCEPTO Y DESARROLLO", "CONCEÇÃO E DESENVOLVIMENTO"],
    ["Uma ferramenta tipográfica criada para aproximar a linguagem odontológica dos produtos que o dentista já usa.", "A typographic tool designed to bring dental language into the products dentists already use.", "Una herramienta tipográfica creada para acercar el lenguaje odontológico a los productos que el dentista ya utiliza.", "Uma ferramenta tipográfica criada para aproximar a linguagem odontológica dos produtos que o dentista já utiliza."],
    ["Voltar ao topo ↑", "Back to top ↑", "Volver arriba ↑", "Voltar ao topo ↑"]
  ];

  const localeIndex = { en: 1, es: 2, "pt-PT": 3 };
  const dictionaries = Object.fromEntries(Object.entries(localeIndex).map(([locale, index]) => [locale, Object.fromEntries(ENTRIES.map(entry => [entry[0], entry[index]]))]));
  const originalText = new WeakMap();
  const originalAttributes = new WeakMap();

  const DYNAMIC = {
    en: {upperProfile:"Upper · profile",upperOcclusal:"Upper · occlusal",lowerProfile:"Lower · profile",lowerOcclusal:"Lower · occlusal",vectorGlyph:"VECTOR GLYPH",autoDisplay:"AUTOMATIC DISPLAY",previousGlyph:"Previous glyph",nextGlyph:"Next glyph",glyphCollections:"Glyph collections",upper:"upper",lower:"lower",profile:"profile",occlusal:"occlusal surface",mixed:"profile + occlusal surface",positions:"POSITIONS",views:"VIEWS",roots:"ROOTS",face:"SURFACE",left:"left",right:"right",sequenceCopied:"Sequence copied",copySequence:"Select and copy the sequence",pngExported:"PNG exported at 2400 × 1200 px",copied:"Copied",select:"Select",copy:"Copy",downloadStarted:"Download started: TTF, OTF and WOFF2"},
    es: {upperProfile:"Superior · perfil",upperOcclusal:"Superior · oclusal",lowerProfile:"Inferior · perfil",lowerOcclusal:"Inferior · oclusal",vectorGlyph:"GLIFO VECTORIAL",autoDisplay:"EXHIBICIÓN AUTOMÁTICA",previousGlyph:"Glifo anterior",nextGlyph:"Glifo siguiente",glyphCollections:"Colecciones de glifos",upper:"superior",lower:"inferior",profile:"perfil",occlusal:"cara oclusal",mixed:"perfil + cara oclusal",positions:"POSICIONES",views:"VISTAS",roots:"RAÍCES",face:"CARA",left:"izquierdo",right:"derecho",sequenceCopied:"Secuencia copiada",copySequence:"Selecciona y copia la secuencia",pngExported:"PNG exportado a 2400 × 1200 px",copied:"Copiado",select:"Selecciona",copy:"Copiar",downloadStarted:"Descarga iniciada: TTF, OTF y WOFF2"},
    "pt-PT": {upperProfile:"Superior · perfil",upperOcclusal:"Superior · oclusal",lowerProfile:"Inferior · perfil",lowerOcclusal:"Inferior · oclusal",vectorGlyph:"GLIFO VETORIAL",autoDisplay:"EXIBIÇÃO AUTOMÁTICA",previousGlyph:"Glifo anterior",nextGlyph:"Glifo seguinte",glyphCollections:"Coleções de glifos",upper:"superior",lower:"inferior",profile:"perfil",occlusal:"face oclusal",mixed:"perfil + face oclusal",positions:"POSIÇÕES",views:"VISTAS",roots:"RAÍZES",face:"FACE",left:"esquerdo",right:"direito",sequenceCopied:"Sequência copiada",copySequence:"Selecione e copie a sequência",pngExported:"PNG exportado em 2400 × 1200 px",copied:"Copiado",select:"Selecione",copy:"Copiar",downloadStarted:"Transferência iniciada: TTF, OTF e WOFF2"},
    "pt-BR": {upperProfile:"Superior · perfil",upperOcclusal:"Superior · oclusal",lowerProfile:"Inferior · perfil",lowerOcclusal:"Inferior · oclusal",vectorGlyph:"GLIFO VETORIAL",autoDisplay:"EXIBIÇÃO AUTOMÁTICA",previousGlyph:"Glifo anterior",nextGlyph:"Próximo glifo",glyphCollections:"Coleções de glifos",upper:"superior",lower:"inferior",profile:"perfil",occlusal:"face oclusal",mixed:"perfil + face oclusal",positions:"POSIÇÕES",views:"VISTAS",roots:"RAÍZES",face:"FACE",left:"esquerdo",right:"direito",sequenceCopied:"Sequência copiada",copySequence:"Selecione e copie a sequência",pngExported:"PNG exportado em 2400 × 1200 px",copied:"Copiado",select:"Selecione",copy:"Copiar",downloadStarted:"Download iniciado: TTF, OTF e WOFF2"}
  };

  function translateStatic(locale) {
    const dictionary = dictionaries[locale] || {};
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        const parent = node.parentElement;
        if (!parent || parent.closest("script, style, code, pre, .language-selector")) return NodeFilter.FILTER_REJECT;
        return node.nodeValue.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (!originalText.has(node)) originalText.set(node, node.nodeValue.trim());
      const source = originalText.get(node);
      const translated = locale === "pt-BR" ? source : (dictionary[source] || source);
      const leading = node.nodeValue.match(/^\s*/)?.[0] || "";
      const trailing = node.nodeValue.match(/\s*$/)?.[0] || "";
      node.nodeValue = `${leading}${translated}${trailing}`;
    }

    document.querySelectorAll("[aria-label], [alt], [title]").forEach(element => {
      if (element.closest(".language-selector")) return;
      if (!originalAttributes.has(element)) {
        originalAttributes.set(element, Object.fromEntries(["aria-label", "alt", "title"].filter(name => element.hasAttribute(name)).map(name => [name, element.getAttribute(name)])));
      }
      for (const [name, source] of Object.entries(originalAttributes.get(element))) {
        element.setAttribute(name, locale === "pt-BR" ? source : (dictionary[source] || source));
      }
    });
  }

  function languageFromCountry(country) {
    const code = String(country || "").toUpperCase();
    if (code === "BR") return "pt-BR";
    if (LUSOPHONE_COUNTRIES.has(code)) return "pt-PT";
    if (SPANISH_COUNTRIES.has(code)) return "es";
    return "en";
  }

  function languageFromBrowser() {
    const languages = navigator.languages?.length ? navigator.languages : [navigator.language];
    for (const language of languages) {
      const normalized = String(language || "").toLowerCase();
      if (normalized === "pt-br") return "pt-BR";
      if (normalized.startsWith("pt")) return "pt-PT";
      if (normalized.startsWith("es")) return "es";
      if (normalized.startsWith("en")) return "en";
    }
    return "en";
  }

  function applyLanguage(locale, { persist = false, announce = true } = {}) {
    if (!SUPPORTED.has(locale)) locale = "en";
    document.documentElement.lang = locale;
    translateStatic(locale);
    document.title = locale === "pt-BR" ? ENTRIES[0][0] : dictionaries[locale][ENTRIES[0][0]];
    const description = document.querySelector('meta[name="description"]');
    if (description) description.content = locale === "pt-BR" ? ENTRIES[1][0] : dictionaries[locale][ENTRIES[1][0]];
    const selector = document.querySelector("#language-select");
    if (selector) selector.value = locale;
    if (persist) localStorage.setItem(STORAGE_KEY, locale);
    api.current = locale;
    if (announce) window.dispatchEvent(new CustomEvent("dental-language-change", { detail: { locale } }));
  }

  async function detectByCountry() {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3500);
    try {
      const response = await fetch("https://get.geojs.io/v1/ip/country.json", { signal: controller.signal, cache: "no-store" });
      if (!response.ok) throw new Error(`GeoJS ${response.status}`);
      const data = await response.json();
      return languageFromCountry(data.country);
    } finally {
      clearTimeout(timeout);
    }
  }

  const api = {
    current: "pt-BR",
    t(key) { return DYNAMIC[api.current]?.[key] || DYNAMIC["pt-BR"][key] || key; },
    set(locale) { applyLanguage(locale, { persist: true }); },
    languageFromCountry
  };
  window.DentalI18n = api;

  const selector = document.querySelector("#language-select");
  selector?.addEventListener("change", event => api.set(event.target.value));

  const stored = localStorage.getItem(STORAGE_KEY);
  if (SUPPORTED.has(stored)) {
    applyLanguage(stored, { announce: false });
  } else {
    const fallback = languageFromBrowser();
    applyLanguage(fallback, { announce: false });
    detectByCountry().then(locale => applyLanguage(locale, { persist: true })).catch(() => applyLanguage(fallback, { persist: true }));
  }
})();
