#!/usr/bin/env python3
"""Build installable Dental Icons fonts and a clean public download package."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables.O_S_2f_2 import Panose
from fontTools.ttLib.tables.ttProgram import Program


ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / "assets" / "reference-vectors"
BUILD = ROOT / "build" / "fonts"
PUBLIC_DOWNLOADS = ROOT / "dental-icons-font" / "downloads"
VERSION = "1.1.3-beta"
FONT_REVISION = 1.103
UPM = 1000
PROFILE_HEIGHT = 194
OCCLUSAL_HEIGHT = 112
LOGICAL_TO_FONT = 4.2
ADVANCE = 520
VERTICAL_SHIFT = -140
FONT_TIMESTAMP = 3870417600  # 2026-08-24 12:00 UTC in the OpenType epoch.
PUA_START = 0xE000
MENU_LETTERS = "ABDENORTUV"
LEFT_CODES = ["M3", "M2", "M1", "P2", "P1", "C", "L", "I"]
RIGHT_CODES = ["I", "L", "C", "P1", "P2", "M1", "M2", "M3"]


def required_tools() -> None:
    for command in ("rsvg-convert", "magick", "potrace"):
        if not shutil.which(command):
            raise SystemExit(f"{command} is required")


def source_path(arch: str, view: str, position: int, code: str) -> Path:
    return VECTORS / f"{arch}-{view}-{position:02d}-{code.lower()}.svg"


def glyph_name(view: str, code: str, side: str) -> str:
    prefix = "prof" if view == "profile" else "occl"
    return f"{prefix}_{code.lower()}_{side}"


def potrace_path(source: Path, temporary: Path) -> tuple[str, int]:
    is_profile = "profile" in source.stem
    width, height = (112, PROFILE_HEIGHT if is_profile else OCCLUSAL_HEIGHT)
    rendered = temporary / f"{source.stem}.png"
    bitmap = temporary / f"{source.stem}.pbm"
    traced = temporary / f"{source.stem}-outline.svg"
    subprocess.run([
        "rsvg-convert", "-w", str(width * 10), "-h", str(height * 10),
        "-b", "white", "-o", str(rendered), str(source),
    ], check=True, capture_output=True)
    subprocess.run([
        "magick", str(rendered), "-colorspace", "gray", "-threshold", "84%", str(bitmap),
    ], check=True, capture_output=True)
    subprocess.run([
        "potrace", "-s", "--flat", "--turnpolicy", "minority", "--turdsize", "2",
        "--alphamax", "1.3", "--opttolerance", "0.8", "--unit", "10",
        "-o", str(traced), str(bitmap),
    ], check=True, capture_output=True)
    tree = ElementTree.parse(traced)
    paths = [node.attrib.get("d", "") for node in tree.iter() if node.tag.endswith("path")]
    data = " ".join(path for path in paths if path.strip())
    if not data:
        raise RuntimeError(f"No outline produced for {source.name}")
    return data, height


def outline_for(source: Path, temporary: Path, kind: str):
    data, logical_height = potrace_path(source, temporary)
    # Potrace uses 10 internal units per raster pixel, and the raster is 10x
    # the logical SVG. This transform restores the logical geometry, flips it
    # to the font coordinate system, and scales it into the em square.
    scale = LOGICAL_TO_FONT / 100
    transform = (scale, 0, 0, -scale, 25, logical_height * LOGICAL_TO_FONT + VERTICAL_SHIFT)
    if kind == "ttf":
        base = TTGlyphPen(None)
        pen = TransformPen(Cu2QuPen(base, max_err=1.0, reverse_direction=True), transform)
        parse_path(data, pen)
        return base.glyph()
    base = T2CharStringPen(ADVANCE, None)
    parse_path(data, TransformPen(base, transform))
    return base.getCharString()


def empty_outline(kind: str, width: int = ADVANCE):
    if kind == "ttf":
        return TTGlyphPen(None).glyph()
    return T2CharStringPen(width, None).getCharString()


def drawing_pen(kind: str, width: int):
    return TTGlyphPen(None) if kind == "ttf" else T2CharStringPen(width, None)


def finish_pen(pen, kind: str):
    return pen.glyph() if kind == "ttf" else pen.getCharString()


def rectangle(pen, x_min: int, y_min: int, x_max: int, y_max: int) -> None:
    pen.moveTo((x_min, y_min)); pen.lineTo((x_max, y_min)); pen.lineTo((x_max, y_max)); pen.lineTo((x_min, y_max)); pen.closePath()


def polygon(pen, points: list[tuple[int, int]]) -> None:
    pen.moveTo(points[0])
    for point in points[1:]:
        pen.lineTo(point)
    pen.closePath()


def notdef_outline(kind: str):
    pen = drawing_pen(kind, ADVANCE)
    rectangle(pen, 55, -110, 465, 690)
    # Counter direction is reversed so the center remains transparent.
    pen.moveTo((115, -50)); pen.lineTo((115, 630)); pen.lineTo((405, 630)); pen.lineTo((405, -50)); pen.closePath()
    return finish_pen(pen, kind)


def fallback_letter_outline(kind: str, letter: str):
    lowercase = letter.islower(); symbol = letter.upper(); width = 400; pen = drawing_pen(kind, width)
    bottom, top, stroke = ((-50, 500, 34) if lowercase else (-60, 650, 40))
    left, right, middle = 45, 355, 200
    rectangle(pen, left, bottom, left + stroke, top)
    if symbol == "M":
        rectangle(pen, right - stroke, bottom, right, top)
        polygon(pen, [(left + stroke, top), (left + 2 * stroke, top), (middle, 255), (middle - 16, 255)])
        polygon(pen, [(right - 2 * stroke, top), (right - stroke, top), (middle + 16, 255), (middle, 255)])
    else:
        rectangle(pen, left, top - stroke, right - 35, top)
        rectangle(pen, right - 35 - stroke, 270, right - 35, top)
        rectangle(pen, left, 270, right - 35, 270 + stroke)
    return finish_pen(pen, kind)


def fallback_digit_outline(kind: str, digit: str):
    width = 260; pen = drawing_pen(kind, width); stroke = 34
    segments = {
        "a": (45, 616, 215, 650), "b": (181, 350, 215, 650),
        "c": (181, -60, 215, 250), "d": (45, -60, 215, -26),
        "e": (45, -60, 79, 250), "f": (45, 350, 79, 650),
        "g": (45, 278, 215, 312),
    }
    enabled = {"1": "bc", "2": "abged", "3": "abgcd"}[digit]
    for segment in enabled:
        rectangle(pen, *segments[segment])
    return finish_pen(pen, kind)


def menu_letter_outline(kind: str, letter: str):
    """Small geometric capitals used only to keep macOS font menus readable."""
    width = 420
    pen = drawing_pen(kind, width)
    left, right, bottom, top, middle, stroke = 45, 375, -50, 650, 300, 44

    def horizontal(y: int) -> None:
        rectangle(pen, left, y, right, y + stroke)

    def vertical(x: int, y_min: int = bottom, y_max: int = top) -> None:
        rectangle(pen, x, y_min, x + stroke, y_max)

    if letter == "A":
        polygon(pen, [(left, bottom), (left + stroke, bottom), (211, top), (190, top)])
        polygon(pen, [(right - stroke, bottom), (right, bottom), (230, top), (209, top)])
        rectangle(pen, 112, 255, 308, 255 + stroke)
    elif letter == "B":
        vertical(left); horizontal(bottom); horizontal(middle); horizontal(top - stroke)
        vertical(right - stroke, middle, top); vertical(right - stroke, bottom, middle + stroke)
    elif letter == "D":
        vertical(left); horizontal(bottom); horizontal(top - stroke); vertical(right - stroke)
    elif letter == "E":
        vertical(left); horizontal(bottom); horizontal(middle); horizontal(top - stroke)
    elif letter == "N":
        vertical(left); vertical(right - stroke)
        polygon(pen, [(left + stroke, top), (left + 2 * stroke, top), (right - stroke, bottom), (right - 2 * stroke, bottom)])
    elif letter == "O":
        vertical(left); vertical(right - stroke); horizontal(bottom); horizontal(top - stroke)
    elif letter == "R":
        vertical(left); horizontal(middle); horizontal(top - stroke); vertical(right - stroke, middle, top)
        polygon(pen, [(190, middle), (240, middle), (right, bottom), (right - stroke, bottom)])
    elif letter == "T":
        horizontal(top - stroke); rectangle(pen, 188, bottom, 232, top)
    elif letter == "U":
        vertical(left); vertical(right - stroke); horizontal(bottom)
    elif letter == "V":
        polygon(pen, [(left, top), (left + stroke, top), (211, bottom), (190, bottom)])
        polygon(pen, [(right - stroke, top), (right, top), (230, bottom), (209, bottom)])
    else:
        raise ValueError(f"Unsupported menu letter: {letter}")
    return finish_pen(pen, kind)


def bar_outline(kind: str):
    pen = drawing_pen(kind, 180)
    rectangle(pen, 82, -80, 98, 660)
    return finish_pen(pen, kind)


def tooth_glyphs(codes: tuple[str, ...] | list[str] = tuple(LEFT_CODES)) -> list[str]:
    return [glyph_name(view, code, side) for view in ("profile", "occlusal") for side in ("l", "r") for code in codes]


def feature_code() -> str:
    ligature_rules: list[str] = []
    for code in ("M1", "M2", "M3"):
        digit = {"1": "one", "2": "two", "3": "three"}[code[1]]
        ligature_rules.append(f"  sub Mbase {digit} by {glyph_name('profile', code, 'l')};")
        ligature_rules.append(f"  sub mbase {digit} by {glyph_name('occlusal', code, 'l')};")
    for code in ("P1", "P2"):
        digit = {"1": "one", "2": "two"}[code[1]]
        ligature_rules.append(f"  sub Pbase {digit} by {glyph_name('profile', code, 'l')};")
        ligature_rules.append(f"  sub pbase {digit} by {glyph_name('occlusal', code, 'l')};")

    lookup_rules: list[str] = []
    lookup_names: list[str] = []
    for view in ("profile", "occlusal"):
        prefix = ["bar", "space"]
        for index, code in enumerate(RIGHT_CODES, 1):
            source = glyph_name(view, code, "l")
            target = glyph_name(view, code, "r")
            lookup_name = f"{view}Right{index}"
            lookup_names.append(lookup_name)
            lookup_rules.extend([
                f"lookup {lookup_name} {{",
                f"  sub {' '.join(prefix)} {source}' by {target};",
                f"}} {lookup_name};",
            ])
            prefix.extend([target, "space"])

    all_teeth = tooth_glyphs()
    ligatures = tooth_glyphs(("M1", "M2", "M3", "P1", "P2"))
    bases = [glyph for glyph in all_teeth if glyph not in ligatures]
    rules = [
        "table GDEF {",
        f"GlyphClassDef [{' '.join(bases)} bar Mbase Pbase mbase pbase one two three], [{' '.join(ligatures)}], [], [];",
        *[f"LigatureCaretByPos {glyph} 260;" for glyph in ligatures],
        "} GDEF;",
        # Compile composed codes before the contextual side alternates. ccmp is
        # processed early by shaping engines; liga keeps the familiar fallback
        # for applications that expose only a Ligatures switch.
        "lookup ComposeTeeth {", *ligature_rules, "} ComposeTeeth;",
        *lookup_rules,
        "feature ccmp { lookup ComposeTeeth; } ccmp;",
        "feature liga { lookup ComposeTeeth;", *[f"  lookup {name};" for name in lookup_names], "} liga;",
        "feature calt {", *[f"  lookup {name};" for name in lookup_names], "} calt;",
        "feature kern {",
        f"  pos [{' '.join(all_teeth)}] space -45;",
        f"  pos space [{' '.join(all_teeth)}] -45;",
        "} kern;",
    ]
    return "\n".join(rules)


def collect_outlines(arch: str, kind: str, temporary: Path):
    outlines = {
        ".notdef": notdef_outline(kind), ".null": empty_outline(kind, 0),
        "nonmarkingreturn": empty_outline(kind, 0), "bar": bar_outline(kind),
        # A visible fallback keeps a complete basic alphanumeric repertoire.
        # Pages filters families that do not advertise any supported text
        # language, even when CoreText and Font Book accept the font itself.
        "unsupported": notdef_outline(kind),
        "Mbase": fallback_letter_outline(kind, "M"),
        "Pbase": fallback_letter_outline(kind, "P"), "mbase": fallback_letter_outline(kind, "m"),
        "pbase": fallback_letter_outline(kind, "p"), "one": fallback_digit_outline(kind, "1"),
        "two": fallback_digit_outline(kind, "2"), "three": fallback_digit_outline(kind, "3"),
    }
    for letter in MENU_LETTERS:
        outlines[f"menu_{letter.lower()}"] = menu_letter_outline(kind, letter)
    for view in ("profile", "occlusal"):
        for position, code in enumerate(LEFT_CODES, 1):
            outlines[glyph_name(view, code, "l")] = outline_for(
                source_path(arch, view, position, code), temporary, kind
            )
        for position, code in enumerate(RIGHT_CODES, 9):
            outlines[glyph_name(view, code, "r")] = outline_for(
                source_path(arch, view, position, code), temporary, kind
            )
    # Keeping a different-width glyph last prevents hmtx compression in CFF
    # fonts, matching Microsoft's interoperability recommendation.
    outlines["space"] = empty_outline(kind, 220)
    return outlines


def font_names(arch: str):
    label = "Upper" if arch == "upper" else "Lower"
    family = "ODONTO ABOVE" if arch == "upper" else "ODONTO UNDER"
    return label, family, f"DentalIcons{label}-Regular"


def metrics_for(glyph_order: list[str]) -> dict[str, tuple[int, int]]:
    metrics = {name: (ADVANCE, 25) for name in glyph_order}
    metrics[".null"] = (0, 0); metrics["nonmarkingreturn"] = (0, 0)
    metrics["space"] = (220, 0); metrics["bar"] = (180, 0)
    for name in ("Mbase", "Pbase", "mbase", "pbase"):
        metrics[name] = (400, 25)
    for name in ("one", "two", "three"):
        metrics[name] = (260, 25)
    for letter in MENU_LETTERS:
        metrics[f"menu_{letter.lower()}"] = (420, 25)
    return metrics


def character_map() -> dict[int, str]:
    mapping = {
        0: ".null", 13: "nonmarkingreturn", 32: "space", 160: "space", 124: "bar",
        ord("M"): "Mbase", ord("P"): "Pbase",
        ord("m"): "mbase", ord("p"): "pbase", ord("1"): "one",
        ord("2"): "two", ord("3"): "three",
        ord("I"): glyph_name("profile", "I", "l"),
        ord("L"): glyph_name("profile", "L", "l"),
        ord("C"): glyph_name("profile", "C", "l"),
        ord("i"): glyph_name("occlusal", "I", "l"),
        ord("l"): glyph_name("occlusal", "L", "l"),
        ord("c"): glyph_name("occlusal", "C", "l"),
    }
    for view_index, view in enumerate(("profile", "occlusal")):
        for position, code in enumerate(LEFT_CODES):
            mapping[PUA_START + view_index * 16 + position] = glyph_name(view, code, "l")
        for position, code in enumerate(RIGHT_CODES, 8):
            mapping[PUA_START + view_index * 16 + position] = glyph_name(view, code, "r")
    for character in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789":
        mapping.setdefault(ord(character), "unsupported")
    # Pages previews a family name using the font itself. These safe capitals
    # make ODONTO ABOVE / ODONTO UNDER readable without stealing any of the
    # direct dental codes I, L, C, M and P.
    for letter in MENU_LETTERS:
        mapping[ord(letter)] = f"menu_{letter.lower()}"
    # Pages filters its font menu for the active document language. Advertising
    # only ASCII makes the family disappear on a pt-BR system, even though Font
    # Book accepts it. Latin-1 coverage keeps it discoverable in Portuguese and
    # other Western-language documents while unsupported keys remain visible.
    for codepoint in range(0x00C0, 0x0100):
        mapping.setdefault(codepoint, "unsupported")
    return mapping


def setup_common(builder: FontBuilder, family: str, postscript: str, glyph_order: list[str], metrics):
    builder.setupGlyphOrder(glyph_order)
    builder.setupCharacterMap(character_map())
    builder.setupHorizontalMetrics(metrics)
    builder.setupHorizontalHeader(ascent=800, descent=-200, lineGap=0, caretSlopeRise=1, caretSlopeRun=0)
    builder.setupNameTable({
        "familyName": family, "styleName": "Regular", "uniqueFontIdentifier": f"DanteTesta:{postscript}:{VERSION}",
        "fullName": family, "psName": postscript, "version": f"Version {FONT_REVISION:.3f}; Dental Icons {VERSION}",
        "copyright": "Copyright © 2026 Dante Testa. Todos os direitos reservados.",
        "manufacturer": "Dante Testa", "designer": "Dante Testa",
        "designerURL": "https://www.dantetesta.com.br", "vendorURL": "https://www.dantetesta.com.br",
        "licenseDescription": "Software proprietário. Uso sujeito à autorização de Dante Testa.",
        "licenseInfoURL": "https://www.dantetesta.com.br",
        "description": "Fonte vetorial original para representação tipográfica de dentes e odontogramas.",
        "typographicFamily": family, "typographicSubfamily": "Regular",
        "sampleText": "M3 M2 M1 P2 P1 C L I | I L C P1 P2 M1 M2 M3",
    }, windows=True, mac=False)
    # Present the family to document editors as a Latin text-capable display
    # face. Marking it as Pictorial makes Pages hide it from its font chooser.
    panose = Panose()
    panose.bFamilyType = 2
    panose.bSerifStyle = 11
    panose.bWeight = 5
    panose.bProportion = 3
    panose.bContrast = 2
    panose.bStrokeVariation = 2
    panose.bArmStyle = 2
    panose.bLetterForm = 2
    panose.bMidline = 2
    panose.bXHeight = 3
    builder.setupOS2(
        version=4, xAvgCharWidth=465, usWeightClass=400, usWidthClass=5, fsType=0,
        ySubscriptXSize=650, ySubscriptYSize=600, ySubscriptXOffset=0, ySubscriptYOffset=75,
        ySuperscriptXSize=650, ySuperscriptYSize=600, ySuperscriptXOffset=0, ySuperscriptYOffset=350,
        yStrikeoutSize=50, yStrikeoutPosition=300, sFamilyClass=0, panose=panose,
        ulCodePageRange1=1, ulCodePageRange2=0, achVendID="Dtst",
        fsSelection=(1 << 6) | (1 << 7) | (1 << 8),
        sTypoAscender=800, sTypoDescender=-200, sTypoLineGap=0,
        usWinAscent=800, usWinDescent=200, sxHeight=500, sCapHeight=650,
        usDefaultChar=0, usBreakChar=32, usMaxContext=17,
    )
    builder.setupPost(keepGlyphNames=True, italicAngle=0, underlinePosition=-100, underlineThickness=50, isFixedPitch=0)


def build_font(arch: str, kind: str, temporary: Path) -> Path:
    _, family, postscript = font_names(arch)
    outlines = collect_outlines(arch, kind, temporary)
    glyph_order = list(outlines)
    metrics = metrics_for(glyph_order)
    builder = FontBuilder(UPM, isTTF=kind == "ttf")
    if kind == "ttf":
        builder.setupGlyf(outlines)
        setup_common(builder, family, postscript, glyph_order, metrics)
        builder.setupMaxp()
        gasp = newTable("gasp"); gasp.gaspRange = {65535: 0x000A}; builder.font["gasp"] = gasp
        # Tell legacy TrueType rasterizers to use compatible smart dropout
        # control. Modern grayscale and subpixel rasterizers ignore these
        # instructions, while Font Book, older Windows stacks and printers can
        # still use them at small sizes.
        prep = newTable("prep"); prep.program = Program()
        prep.program.fromBytecode(bytes((0xB8, 0x01, 0xFF, 0x85, 0xB0, 0x04, 0x8D)))
        builder.font["prep"] = prep
    else:
        setup_common(builder, family, postscript, glyph_order, metrics)
        builder.setupCFF(postscript, {
            "FullName": family, "FamilyName": family, "Weight": "Regular", "version": f"{FONT_REVISION:.3f}",
            "Notice": "Copyright 2026 Dante Testa. All rights reserved.",
            "Copyright": "Copyright 2026 Dante Testa. All rights reserved.",
            "ItalicAngle": 0, "isFixedPitch": False, "UnderlinePosition": -100, "UnderlineThickness": 50,
        }, outlines, {})
    addOpenTypeFeaturesFromString(builder.font, feature_code())
    builder.font["head"].fontRevision = FONT_REVISION
    builder.font["head"].created = FONT_TIMESTAMP; builder.font["head"].modified = FONT_TIMESTAMP
    builder.font["head"].lowestRecPPEM = 6
    if kind == "otf":
        builder.font["hhea"].numberOfHMetrics = len(glyph_order)
    output = BUILD / f"{postscript}.{kind}"
    builder.save(output)
    return output


def make_woff2(ttf: Path) -> Path:
    output = ttf.with_suffix(".woff2")
    if shutil.which("woff2_compress"):
        subprocess.run(["woff2_compress", str(ttf)], check=True, capture_output=True)
        return output
    font = TTFont(ttf)
    font.flavor = "woff2"
    font.save(output)
    return output


def package(files: list[Path]) -> Path:
    staging = BUILD / "public-package"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    macos = staging / "macOS"; windows_linux = staging / "Windows-Linux"; web = staging / "Web"
    macos.mkdir(); windows_linux.mkdir(); web.mkdir()
    for file in files:
        destination = macos if file.suffix == ".otf" else windows_linux if file.suffix == ".ttf" else web
        shutil.copy2(file, destination / file.name)
    (web / "dental-icons.css").write_text('''@font-face {
  font-family: "Dental Icons Upper";
  src: url("DentalIconsUpper-Regular.woff2") format("woff2");
  font-style: normal;
  font-weight: 400;
  font-display: swap;
}
@font-face {
  font-family: "Dental Icons Lower";
  src: url("DentalIconsLower-Regular.woff2") format("woff2");
  font-style: normal;
  font-weight: 400;
  font-display: swap;
}
.dental-icons-upper,
.dental-icons-lower {
  font-style: normal;
  font-weight: 400;
  font-synthesis: none;
  font-variant-ligatures: common-ligatures contextual;
  font-feature-settings: "ccmp" 1, "liga" 1, "calt" 1, "kern" 1;
}
.dental-icons-upper { font-family: "Dental Icons Upper"; }
.dental-icons-lower { font-family: "Dental Icons Lower"; }
''', encoding="utf-8")
    (staging / "LEIA-ME.txt").write_text(f'''DENTAL ICONS FONT — {VERSION}
Autor: Dante Testa
Site: https://www.dantetesta.com.br

ODONTO ABOVE: arcada superior (arquivo Upper).
ODONTO UNDER: arcada inferior (arquivo Lower).
Maiúsculas: dentes em perfil. Minúsculas: vista oclusal.

Códigos: I, L, C, P1, P2, M1, M2, M3.
Exemplo: M3 M2 M1 P2 P1 C L I | I L C P1 P2 M1 M2 M3

QUAL PASTA USAR
- macOS: instale somente os dois arquivos OTF da pasta macOS.
- Windows e Linux: instale somente os dois arquivos TTF da pasta Windows-Linux.
- Sites e sistemas web: publique o conteúdo da pasta Web.
- Não instale OTF e TTF simultaneamente no mesmo computador.

macOS / Pages / Keynote / Office para Mac
1. Encerre os editores com Command-Q.
2. Abra os dois OTF no Catálogo de Fontes.
3. Se houver uma versão anterior, remova-a e instale a nova; não mantenha duplicadas.
4. Reabra o editor e escolha ODONTO ABOVE ou ODONTO UNDER.
5. Para M1/P2, habilite ligaturas padrão ou todas as ligaturas.

Windows / Microsoft Office
1. Extraia o ZIP, selecione os dois TTF e use Instalar para todos os usuários.
2. Feche e reabra Word, PowerPoint ou o aplicativo de destino.
3. Mantenha ligaturas padrão habilitadas.

Linux / LibreOffice / OpenOffice
1. Instale os dois TTF pelo gerenciador de fontes da distribuição.
2. Atualize o cache de fontes e reinicie o editor.
3. No LibreOffice, confira as funcionalidades OpenType se os códigos compostos não forem ligados.

Web
1. Mantenha os WOFF2 e dental-icons.css no mesmo diretório.
2. Use as classes dental-icons-upper e dental-icons-lower.

Compatibilidade adicional
Os 32 desenhos de cada família também possuem códigos Unicode PUA diretos.
Consulte MAPA-DE-GLIFOS.txt quando um aplicativo não processar ligaturas OpenType.

Versão beta: recomenda-se validação anatômica antes de uso clínico definitivo.
''', encoding="utf-8")
    map_lines = [
        "DENTAL ICONS FONT — MAPA UNICODE PUA",
        "Autor: Dante Testa",
        "",
        "Use estes códigos como alternativa em aplicativos sem ligaturas OpenType.",
        "O mesmo mapa vale para as famílias Upper e Lower.",
        "",
    ]
    for view_index, view in enumerate(("PERFIL (maiúsculas)", "OCLUSAL (minúsculas)")):
        map_lines.append(view)
        for position, code in enumerate(LEFT_CODES + RIGHT_CODES):
            unicode_value = PUA_START + view_index * 16 + position
            side = "esquerdo" if position < 8 else "direito"
            map_lines.append(f"U+{unicode_value:04X}  posição {position + 1:02d}  {code.lower() if view_index else code:<2}  lado {side}")
        map_lines.append("")
    (staging / "MAPA-DE-GLIFOS.txt").write_text("\n".join(map_lines), encoding="utf-8")
    shutil.copy2(ROOT / "LICENSE", staging / "LICENCA.txt")
    PUBLIC_DOWNLOADS.mkdir(parents=True, exist_ok=True)
    zip_path = PUBLIC_DOWNLOADS / "dental-icons-font.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(path for path in staging.rglob("*") if path.is_file()):
            # Stable metadata makes two builds from the same sources produce
            # the same public artifact, which simplifies release verification.
            info = zipfile.ZipInfo(str(file.relative_to(staging)), (2026, 8, 24, 12, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, file.read_bytes())
    return zip_path


def main() -> None:
    required_tools()
    BUILD.mkdir(parents=True, exist_ok=True)
    built: list[Path] = []
    with tempfile.TemporaryDirectory(prefix="dental-icons-build-") as tmp:
        temporary = Path(tmp)
        for arch in ("upper", "lower"):
            built.append(build_font(arch, "ttf", temporary))
            built.append(build_font(arch, "otf", temporary))
    for ttf in [path for path in built if path.suffix == ".ttf"]:
        built.append(make_woff2(ttf))
    zip_path = package(built)
    print(f"Built {len(built)} fonts and {zip_path}")


if __name__ == "__main__":
    main()
