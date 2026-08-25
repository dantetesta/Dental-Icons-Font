#!/usr/bin/env python3
"""Deterministic release checks for Dental Icons desktop and web fonts."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "build" / "fonts"
ZIP_PATH = ROOT / "dental-icons-font" / "downloads" / "dental-icons-font.zip"
FAMILIES = {
    "Upper": "ODONTO ABOVE",
    "Lower": "ODONTO UNDER",
}
FORMATS = ("otf", "ttf", "woff2")
PUA = set(range(0xE000, 0xE020))
EXPECTED_ZIP = {
    "LEIA-ME.txt",
    "LICENCA.txt",
    "MAPA-DE-GLIFOS.txt",
    "macOS/DentalIconsUpper-Regular.otf",
    "macOS/DentalIconsLower-Regular.otf",
    "Windows-Linux/DentalIconsUpper-Regular.ttf",
    "Windows-Linux/DentalIconsLower-Regular.ttf",
    "Web/DentalIconsUpper-Regular.woff2",
    "Web/DentalIconsLower-Regular.woff2",
    "Web/dental-icons.css",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def name_value(font: TTFont, name_id: int) -> str:
    value = font["name"].getName(name_id, 3, 1, 0x409)
    return value.toUnicode() if value else ""


def validate_tables(path: Path, label: str, family: str) -> None:
    font = TTFont(path)
    required = {"head", "hhea", "maxp", "OS/2", "hmtx", "cmap", "name", "post", "GDEF", "GPOS", "GSUB"}
    require(required <= set(font.keys()), f"{path.name}: missing tables {required - set(font.keys())}")
    if path.suffix == ".otf":
        require("CFF " in font and "glyf" not in font, f"{path.name}: OTF must use CFF outlines")
    else:
        require("glyf" in font and "CFF " not in font, f"{path.name}: TTF/WOFF2 must use TrueType outlines")
    if path.suffix == ".ttf":
        require({"gasp", "prep"} <= set(font.keys()), f"{path.name}: missing TrueType rasterization tables")

    require(font["head"].unitsPerEm == 1000, f"{path.name}: unexpected unitsPerEm")
    require(round(font["head"].fontRevision, 3) == 1.103, f"{path.name}: wrong revision")
    require(font["hhea"].ascent == 800 and font["hhea"].descent == -200, f"{path.name}: bad hhea metrics")
    require(font["hhea"].numberOfHMetrics == len(font.getGlyphOrder()), f"{path.name}: compressed/incomplete hmtx")

    os2 = font["OS/2"]
    require(os2.version >= 4, f"{path.name}: OS/2 table is too old")
    require(os2.fsType == 0, f"{path.name}: embedding is not installable")
    require(os2.fsSelection & 0x1C0 == 0x1C0, f"{path.name}: Regular/USE_TYPO_METRICS/WWS flags missing")
    require(os2.achVendID == "Dtst", f"{path.name}: invalid vendor ID")
    require(os2.panose.bFamilyType == 2, f"{path.name}: document editors may hide non-text PANOSE families")
    require((os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap) == (800, -200, 0), f"{path.name}: typo metrics mismatch")
    require((os2.usWinAscent, os2.usWinDescent) == (800, 200), f"{path.name}: Windows clipping metrics mismatch")
    require(os2.ulCodePageRange1 & 1, f"{path.name}: Latin 1 code-page bit missing")

    for name_id in (0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19):
        require(name_value(font, name_id), f"{path.name}: name ID {name_id} missing")
    require(name_value(font, 1) == family, f"{path.name}: legacy family mismatch")
    require(name_value(font, 2) == "Regular", f"{path.name}: style is not Regular")
    require(name_value(font, 6) == f"DentalIcons{label}-Regular", f"{path.name}: PostScript name mismatch")

    cmap = font.getBestCmap()
    require({0, 13, 32, 160, 124} <= set(cmap), f"{path.name}: control/space cmap incomplete")
    require(PUA <= set(cmap), f"{path.name}: direct PUA fallback map incomplete")
    require({ord(c) for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"} <= set(cmap), f"{path.name}: basic alphanumeric cmap incomplete")

    glyph_set = font.getGlyphSet()
    for glyph_name in font.getGlyphOrder():
        if glyph_name in {".null", "nonmarkingreturn", "space"}:
            continue
        pen = BoundsPen(glyph_set)
        glyph_set[glyph_name].draw(pen)
        require(pen.bounds is not None, f"{path.name}: {glyph_name} is unexpectedly blank")
        _, y_min, _, y_max = pen.bounds
        require(y_min >= -200 and y_max <= 800, f"{path.name}: {glyph_name} can be clipped ({y_min}, {y_max})")


def shape(path: Path, text: str, features: str = "ccmp=1,liga=1,calt=1,kern=1") -> list[str]:
    result = subprocess.run(
        ["hb-shape", str(path), text, f"--features={features}"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return [piece.split("=", 1)[0] for piece in result.strip("[]").split("|") if "=" in piece]


def validate_shaping(path: Path) -> None:
    require(shape(path, "M1") == ["prof_m1_l"], f"{path.name}: M1 did not compose")
    require(shape(path, "m1 M1") == ["occl_m1_l", "space", "prof_m1_l"], f"{path.name}: case does not select distinct views")
    full = shape(path, "M3 M2 M1 P2 P1 C L I | I L C P1 P2 M1 M2 M3")
    right = [name for name in full[17:] if name not in {"space", "bar"}]
    require(right == ["prof_i_r", "prof_l_r", "prof_c_r", "prof_p1_r", "prof_p2_r", "prof_m1_r", "prof_m2_r", "prof_m3_r"], f"{path.name}: right-side contextual sequence failed: {right}")
    require(shape(path, "M1", "ccmp=0,liga=0,calt=0,kern=0") == ["Mbase", "one"], f"{path.name}: visible non-ligature fallback failed")
    require(shape(path, "\ue000") == ["prof_m3_l"], f"{path.name}: direct PUA fallback failed")


def validate_fontconfig(path: Path, expected_family: str) -> None:
    result = subprocess.run(
        ["fc-scan", "--format", "%{family}|%{style}", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    require(result == f"{expected_family}|Regular", f"{path.name}: fontconfig identity mismatch: {result}")


def validate_woff2(path: Path, label: str, family: str) -> None:
    require(path.read_bytes()[:4] == b"wOF2", f"{path.name}: invalid WOFF2 signature")
    with tempfile.TemporaryDirectory(prefix="dental-woff2-") as tmp:
        copy = Path(tmp) / path.name
        shutil.copy2(path, copy)
        subprocess.run(["woff2_decompress", str(copy)], check=True, capture_output=True)
        decompressed = copy.with_suffix(".ttf")
        require(decompressed.exists(), f"{path.name}: WOFF2 round trip failed")
        validate_tables(decompressed, label, family)
        validate_shaping(decompressed)


def validate_zip() -> None:
    with zipfile.ZipFile(ZIP_PATH) as archive:
        names = {name for name in archive.namelist() if not name.endswith("/")}
        require(names == EXPECTED_ZIP, f"ZIP allowlist mismatch: missing={EXPECTED_ZIP - names}, extra={names - EXPECTED_ZIP}")
        require(archive.testzip() is None, "ZIP CRC/integrity test failed")
        lowered = "\n".join(names).lower()
        for forbidden in (".env", "agents.md", "claude.md", "memory.md", ".git", "token", "secret", "backup", "screenshot"):
            require(forbidden not in lowered, f"ZIP contains forbidden pattern: {forbidden}")
        css = archive.read("Web/dental-icons.css").decode("utf-8")
        require(css.count("@font-face") == 2 and 'format("woff2")' in css, "Web CSS is incomplete")


def main() -> None:
    for command in ("hb-shape", "fc-scan", "woff2_decompress"):
        require(shutil.which(command) is not None, f"required validator not found: {command}")

    for label, family in FAMILIES.items():
        for extension in FORMATS:
            path = FONTS / f"DentalIcons{label}-Regular.{extension}"
            require(path.exists(), f"missing artifact: {path}")
            if extension in {"otf", "ttf"}:
                validate_tables(path, label, family)
                validate_shaping(path)
                validate_fontconfig(path, family)
            else:
                validate_woff2(path, label, family)
            print(f"PASS {path.relative_to(ROOT)}")
    validate_zip()
    print(f"PASS {ZIP_PATH.relative_to(ROOT)} (clean runtime allowlist and CRC)")
    print("All Dental Icons release checks passed.")


if __name__ == "__main__":
    main()
