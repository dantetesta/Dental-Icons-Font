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
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / "assets" / "reference-vectors"
BUILD = ROOT / "build" / "fonts"
PUBLIC_DOWNLOADS = ROOT / "dental-icons-font" / "downloads"
VERSION = "1.0.2-beta"
FONT_REVISION = 1.002
UPM = 1000
PROFILE_HEIGHT = 194
OCCLUSAL_HEIGHT = 112
LOGICAL_TO_FONT = 4.2
ADVANCE = 520
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
    transform = (scale, 0, 0, -scale, 25, logical_height * LOGICAL_TO_FONT)
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


def bar_outline(kind: str):
    if kind == "ttf":
        pen = TTGlyphPen(None)
    else:
        pen = T2CharStringPen(180, None)
    pen.moveTo((82, 120)); pen.lineTo((98, 120)); pen.lineTo((98, 760)); pen.lineTo((82, 760)); pen.closePath()
    return pen.glyph() if kind == "ttf" else pen.getCharString()


def feature_code() -> str:
    rules = ["feature liga {"]
    for code in ("M1", "M2", "M3"):
        digit = {"1": "one", "2": "two", "3": "three"}[code[1]]
        rules.append(f"  sub Mbase {digit} by {glyph_name('profile', code, 'l')};")
        rules.append(f"  sub mbase {digit} by {glyph_name('occlusal', code, 'l')};")
    for code in ("P1", "P2"):
        digit = {"1": "one", "2": "two"}[code[1]]
        rules.append(f"  sub Pbase {digit} by {glyph_name('profile', code, 'l')};")
        rules.append(f"  sub pbase {digit} by {glyph_name('occlusal', code, 'l')};")
    rules.append("} liga;")

    rules.append("feature calt {")
    for view in ("profile", "occlusal"):
        prefix = ["bar", "space"]
        for index, code in enumerate(RIGHT_CODES, 1):
            source = glyph_name(view, code, "l")
            target = glyph_name(view, code, "r")
            rules.extend([
                f"lookup {view}Right{index} {{",
                f"  sub {' '.join(prefix)} {source}' by {target};",
                f"}} {view}Right{index};",
            ])
            prefix.extend([target, "space"])
    rules.append("} calt;")
    return "\n".join(rules)


def collect_outlines(arch: str, kind: str, temporary: Path):
    outlines = {
        ".notdef": empty_outline(kind), "space": empty_outline(kind, 220),
        "bar": bar_outline(kind), "Mbase": empty_outline(kind, 0),
        "Pbase": empty_outline(kind, 0), "mbase": empty_outline(kind, 0),
        "pbase": empty_outline(kind, 0), "one": empty_outline(kind, 0),
        "two": empty_outline(kind, 0), "three": empty_outline(kind, 0),
    }
    for view in ("profile", "occlusal"):
        for position, code in enumerate(LEFT_CODES, 1):
            outlines[glyph_name(view, code, "l")] = outline_for(
                source_path(arch, view, position, code), temporary, kind
            )
        for position, code in enumerate(RIGHT_CODES, 9):
            outlines[glyph_name(view, code, "r")] = outline_for(
                source_path(arch, view, position, code), temporary, kind
            )
    return outlines


def font_names(arch: str):
    label = "Upper" if arch == "upper" else "Lower"
    family = f"Dental Icons {label}"
    return label, family, family.replace(" ", "") + "-Regular"


def metrics_for(glyph_order: list[str]) -> dict[str, tuple[int, int]]:
    metrics = {name: (ADVANCE, 25) for name in glyph_order}
    metrics["space"] = (220, 0); metrics["bar"] = (180, 0)
    for name in ("Mbase", "Pbase", "mbase", "pbase", "one", "two", "three"):
        metrics[name] = (0, 0)
    return metrics


def character_map() -> dict[int, str]:
    return {
        32: "space", 124: "bar", ord("M"): "Mbase", ord("P"): "Pbase",
        ord("m"): "mbase", ord("p"): "pbase", ord("1"): "one",
        ord("2"): "two", ord("3"): "three",
        ord("I"): glyph_name("profile", "I", "l"),
        ord("L"): glyph_name("profile", "L", "l"),
        ord("C"): glyph_name("profile", "C", "l"),
        ord("i"): glyph_name("occlusal", "I", "l"),
        ord("l"): glyph_name("occlusal", "L", "l"),
        ord("c"): glyph_name("occlusal", "C", "l"),
    }


def setup_common(builder: FontBuilder, family: str, postscript: str, glyph_order: list[str], metrics):
    builder.setupGlyphOrder(glyph_order)
    builder.setupCharacterMap(character_map())
    builder.setupHorizontalMetrics(metrics)
    builder.setupHorizontalHeader(ascent=860, descent=-140)
    builder.setupNameTable({
        "familyName": family, "styleName": "Regular", "uniqueFontIdentifier": f"DanteTesta:{postscript}:{VERSION}",
        "fullName": family, "psName": postscript, "version": f"Version {FONT_REVISION:.3f}; Dental Icons {VERSION}",
        "copyright": "Copyright © 2026 Dante Testa. Todos os direitos reservados.",
        "manufacturer": "Dante Testa", "designer": "Dante Testa",
        "designerURL": "https://www.dantetesta.com.br", "vendorURL": "https://www.dantetesta.com.br",
        "licenseDescription": "Software proprietário. Uso sujeito à autorização de Dante Testa.",
        "licenseInfoURL": "https://www.dantetesta.com.br",
        "description": "Fonte vetorial original para representação tipográfica de dentes e odontogramas.",
    })
    builder.setupOS2(sTypoAscender=860, sTypoDescender=-140, usWinAscent=860, usWinDescent=140)
    builder.setupPost()


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
    else:
        setup_common(builder, family, postscript, glyph_order, metrics)
        builder.setupCFF(postscript, {
            "FullName": family, "FamilyName": family, "Weight": "Regular", "version": f"{FONT_REVISION:.3f}",
        }, outlines, {})
    addOpenTypeFeaturesFromString(builder.font, feature_code())
    builder.font["head"].fontRevision = FONT_REVISION
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
    for file in files:
        shutil.copy2(file, staging / file.name)
    (staging / "dental-icons.css").write_text('''@font-face {
  font-family: "Dental Icons Upper";
  src: url("DentalIconsUpper-Regular.woff2") format("woff2");
  font-display: swap;
}
@font-face {
  font-family: "Dental Icons Lower";
  src: url("DentalIconsLower-Regular.woff2") format("woff2");
  font-display: swap;
}
.dental-icons-upper { font-family: "Dental Icons Upper"; font-variant-ligatures: common-ligatures contextual; }
.dental-icons-lower { font-family: "Dental Icons Lower"; font-variant-ligatures: common-ligatures contextual; }
''', encoding="utf-8")
    (staging / "LEIA-ME.txt").write_text(f'''DENTAL ICONS FONT — {VERSION}
Autor: Dante Testa
Site: https://www.dantetesta.com.br

Dental Icons Upper: arcada superior.
Dental Icons Lower: arcada inferior.
Maiúsculas: dentes em perfil. Minúsculas: vista oclusal.

Códigos: I, L, C, P1, P2, M1, M2, M3.
Exemplo: M3 M2 M1 P2 P1 C L I | I L C P1 P2 M1 M2 M3

Instalação no macOS / Pages:
1. Abra os dois arquivos OTF no Catálogo de Fontes.
2. Se já existir uma versão, escolha Substituir (não Manter Ambos).
3. Encerre completamente o Pages com Command-Q e abra novamente.
4. No Pages, procure Dental Icons Upper ou Dental Icons Lower.
5. Se M1/P2 não virar um dente, use Formatar > Fonte > Ligadura > Usar Padrão ou Usar Tudo.

No Windows: abra os dois arquivos TTF, selecione Instalar e reinicie o Office.
Web: envie os arquivos WOFF2 e dental-icons.css para o mesmo diretório.

Versão beta: recomenda-se validação anatômica antes de uso clínico definitivo.
''', encoding="utf-8")
    PUBLIC_DOWNLOADS.mkdir(parents=True, exist_ok=True)
    zip_path = PUBLIC_DOWNLOADS / "dental-icons-font.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(staging.iterdir()):
            archive.write(file, file.name)
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
