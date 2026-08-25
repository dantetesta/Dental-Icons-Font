# Dental Icons Font

Fonte vetorial para escrever representações dentárias em documentos, apresentações, aplicativos e interfaces web. O sistema transforma códigos curtos — `I`, `L`, `C`, `P1`, `P2`, `M1`, `M2` e `M3` — em glifos anatômicos organizados por arcada e vista.

- **Autor e diretor criativo:** Dante Testa
- **Site:** [www.dantetesta.com.br](https://www.dantetesta.com.br)
- **Versão atual:** 1.1.2-beta
- **Ano de criação:** 2026

> Projeto em fase beta. A anatomia deve passar por revisão odontológica antes de uso clínico definitivo.

## O que este repositório contém

- 64 referências raster isoladas: 16 posições × 2 arcadas × 2 vistas;
- 64 SVGs monoline reconstruídos com curvas Bézier;
- duas famílias tipográficas: `Dental Icons Upper` e `Dental Icons Lower`;
- arquivos instaláveis TTF e OTF;
- webfonts WOFF2 e folha CSS;
- 32 pontos Unicode PUA diretos por família para aplicativos sem ligaturas;
- scripts reproduzíveis de vetorização, compilação OpenType e empacotamento;
- validadores de estrutura, shaping, CoreText/macOS, WOFF2 e integridade do ZIP;
- landing page interativa com simulador, comparação de vistas e download;
- página técnica simples na raiz para inspeção dos desenhos.

## Autoria e proveniência

Este projeto foi concebido, dirigido e produzido para Dante Testa. Os glifos foram desenvolvidos a partir dos 64 desenhos dentários de referência preservados em [`assets/reference-glyphs`](assets/reference-glyphs), e não a partir de uma fonte comercial, biblioteca de ícones ou pacote vetorial de terceiros.

O processo de produção registrado no próprio repositório é:

1. isolamento dos desenhos de referência por posição, arcada e vista;
2. redução para eixo central e limpeza de componentes espúrios;
3. reconstrução em caminhos SVG com curvas Catmull–Rom convertidas em Bézier;
4. normalização de escala, direção anatômica, terminações e junções;
5. conversão dos caminhos para contornos TrueType e CFF/OpenType;
6. criação das ligaturas `P1`, `P2`, `M1`, `M2` e `M3` e das alternâncias contextuais de lado;
7. geração dos artefatos TTF, OTF, WOFF2 e do pacote de instalação.

O histórico Git, os desenhos-fonte, os vetores intermediários e os scripts permitem auditar como os arquivos finais foram produzidos. Dependências de software de código aberto são usadas apenas como ferramentas de processamento e compilação; elas não fornecem os desenhos dos dentes.

O desenvolvimento foi assistido por ferramentas de inteligência artificial sob direção, seleção e aprovação de Dante Testa. Essa assistência não transfere a autoria do projeto nem introduz, por si só, direitos sobre fontes ou bibliotecas externas.

## Mapa tipográfico

| Código | Dente | Maiúscula | Minúscula |
|---|---|---|---|
| `I` / `i` | Incisivo central | perfil | face oclusal |
| `L` / `l` | Incisivo lateral | perfil | face oclusal |
| `C` / `c` | Canino | perfil | face oclusal |
| `P1` / `p1` | Primeiro pré-molar | perfil | face oclusal |
| `P2` / `p2` | Segundo pré-molar | perfil | face oclusal |
| `M1` / `m1` | Primeiro molar | perfil | face oclusal |
| `M2` / `m2` | Segundo molar | perfil | face oclusal |
| `M3` / `m3` | Terceiro molar | perfil | face oclusal |

Use `Dental Icons Upper` para a arcada superior e `Dental Icons Lower` para a inferior. A barra vertical separa os lados e ativa as formas contextuais do lado direito:

```text
M3 M2 M1 P2 P1 C L I | I L C P1 P2 M1 M2 M3
```

As ligaturas tipográficas precisam estar habilitadas para que códigos com dois caracteres, como `M1` e `P2`, sejam convertidos em um único dente. O pacote também inclui `MAPA-DE-GLIFOS.txt` com pontos Unicode PUA diretos para softwares que não executam ligaturas OpenType.

No simulador da landing page, o controle **Caixa / vista** oferece três leituras:

- `A/a · Digitado`: respeita a caixa de cada código e permite misturar `m1 M1`;
- `A · Perfil`: converte a sequência inteira para maiúsculas e mostra os dentes em perfil;
- `a · Oclusal`: converte a sequência inteira para minúsculas e mostra as faces oclusais.

## Instalação

### macOS, Pages e Keynote

1. No ZIP, abra a pasta `macOS` e instale somente `DentalIconsUpper-Regular.otf` e `DentalIconsLower-Regular.otf` no Catálogo de Fontes.
2. Se uma versão anterior já existir, escolha **Substituir**, não **Manter Ambos**.
3. Encerre completamente o Pages ou Keynote com `Command + Q` e abra novamente.
4. Selecione `Dental Icons Upper` ou `Dental Icons Lower` na lista de fontes.
5. Se `M1` ou `P2` não formar um dente: **Formatar → Fonte → Ligadura → Usar Padrão** ou **Usar Tudo**.

### Windows e Microsoft Office

1. No ZIP, abra a pasta `Windows-Linux` e instale somente os dois arquivos TTF.
2. Selecione **Instalar para todos os usuários** quando disponível.
3. Feche e reabra Word, PowerPoint ou o aplicativo de destino.
4. Selecione uma das duas famílias Dental Icons e mantenha ligaturas padrão habilitadas.

### LibreOffice e OpenOffice

Instale os dois arquivos TTF da pasta `Windows-Linux` no sistema operacional, reinicie o aplicativo e selecione a família correspondente à arcada. O suporte a ligaturas OpenType pode variar conforme a versão e o mecanismo de layout de texto; nesse caso, use os códigos diretos de `MAPA-DE-GLIFOS.txt`.

## Uso como webfont

Copie o conteúdo da pasta `Web` — os dois WOFF2 e `dental-icons.css` — para o mesmo diretório:

```html
<link rel="stylesheet" href="/fonts/dental-icons.css">
<span class="dental-icons-upper">M1 P2 C L I | I L C P2 M1</span>
<span class="dental-icons-lower">m1 p2 c l i | i l c p2 m1</span>
```

O CSS ativa ligaturas comuns e alternâncias contextuais, necessárias para os códigos compostos e para as formas do lado direito após a barra vertical.

## Desenvolvimento e compilação

Requisitos Python:

```bash
python3 -m pip install -r requirements.txt
```

Ferramentas externas usadas pelo compilador:

- `librsvg` (`rsvg-convert`);
- ImageMagick (`magick`);
- Potrace (`potrace`);
- WOFF2 (`woff2_compress`, recomendado).

No macOS com Homebrew:

```bash
brew install librsvg imagemagick potrace woff2
```

Para refazer todo o pipeline:

```bash
python3 -B scripts/vectorize_reference.py
python3 -B scripts/build_fonts.py
```

O segundo comando recompila as fontes e recria `dental-icons-font/downloads/dental-icons-font.zip` a partir de uma lista positiva de arquivos de distribuição.

Para executar a validação reproduzível dos seis artefatos e do ZIP:

```bash
python3 -B scripts/validate_fonts.py
swift scripts/validate_coretext.swift build/fonts/*.otf build/fonts/*.ttf
```

O primeiro comando confere tabelas obrigatórias, nomes, métricas, permissão de incorporação, mapas Unicode, contornos, ligaturas, alternâncias direita/esquerda, leitura pelo Fontconfig, descompressão WOFF2 e a lista positiva do ZIP. No macOS, o segundo confirma que CoreText — mecanismo usado pelos aplicativos nativos — reconhece as famílias e processa os recursos OpenType.

Para visualizar a landing page localmente:

```bash
python3 -B -m http.server 8765 --bind 127.0.0.1
```

Depois acesse `http://127.0.0.1:8765/dental-icons-font/`.

## Estrutura

```text
assets/reference-glyphs/      referências raster preservadas
assets/reference-vectors/     SVGs Bézier que alimentam a fonte
scripts/                      vetorização e compilação
build/fonts/                  TTF, OTF, WOFF2 e staging do pacote
dental-icons-font/            landing page e simulador
dental-icons-font/downloads/  ZIP instalável entregue ao usuário
index.html                    prova técnica simples
```

## Direitos

Copyright © 2026 Dante Testa. Todos os direitos reservados.

Este é um projeto proprietário mantido em repositório privado. Nenhuma permissão de cópia, redistribuição, modificação, sublicenciamento ou comercialização é concedida sem autorização expressa e por escrito de Dante Testa. Consulte [`LICENSE`](LICENSE).

Dental Icons Font é uma ferramenta de representação visual e não substitui avaliação, diagnóstico ou documentação clínica profissional.

## Compatibilidade e formatos

- **OTF/CFF:** distribuição recomendada para macOS, Pages, Keynote, Office para Mac e aplicativos gráficos;
- **TTF/TrueType:** distribuição recomendada para Windows, Linux, Microsoft Office, LibreOffice e OpenOffice;
- **WOFF2:** distribuição exclusiva para navegadores e sistemas web; não deve ser instalada como fonte de desktop.

As fontes usam tabelas OpenType padronizadas e foram validadas localmente com FontTools, HarfBuzz, Fontconfig, WOFF2, FontBakery e CoreText. Compatibilidade absoluta com toda versão histórica de todo editor não pode ser garantida; por isso o mapa PUA acompanha a distribuição como alternativa às ligaturas.
