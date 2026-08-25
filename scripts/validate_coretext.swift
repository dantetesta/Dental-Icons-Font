import CoreText
import Foundation

guard CommandLine.arguments.count > 1 else {
    fputs("Usage: swift validate_coretext.swift FONT...\n", stderr)
    exit(2)
}

var failed = false

func shapedGlyphNames(_ text: String, font: CTFont) -> [String] {
    let attributes: [NSAttributedString.Key: Any] = [
        NSAttributedString.Key(kCTFontAttributeName as String): font,
        NSAttributedString.Key(kCTLigatureAttributeName as String): 1,
    ]
    let line = CTLineCreateWithAttributedString(NSAttributedString(string: text, attributes: attributes))
    var names: [String] = []
    for item in CTLineGetGlyphRuns(line) as NSArray {
        let run = item as! CTRun
        let count = CTRunGetGlyphCount(run)
        var glyphs = Array(repeating: CGGlyph(), count: count)
        glyphs.withUnsafeMutableBufferPointer { buffer in
            CTRunGetGlyphs(run, CFRange(location: 0, length: 0), buffer.baseAddress!)
        }
        names.append(contentsOf: glyphs.map { CTFontCopyNameForGlyph(font, $0) as String? ?? "" })
    }
    return names
}

for argument in CommandLine.arguments.dropFirst() {
    let url = URL(fileURLWithPath: argument)
    guard let descriptors = CTFontManagerCreateFontDescriptorsFromURL(url as CFURL) as? [CTFontDescriptor],
          descriptors.count == 1 else {
        fputs("FAIL \(argument): CoreText could not parse one face\n", stderr)
        failed = true
        continue
    }

    let descriptor = descriptors[0]
    let family = CTFontDescriptorCopyAttribute(descriptor, kCTFontFamilyNameAttribute) as? String ?? ""
    let style = CTFontDescriptorCopyAttribute(descriptor, kCTFontStyleNameAttribute) as? String ?? ""
    let postScript = CTFontDescriptorCopyAttribute(descriptor, kCTFontNameAttribute) as? String ?? ""

    let font = CTFontCreateWithFontDescriptor(descriptor, 72, nil)
    let languages = CTFontCopySupportedLanguages(font) as? [String] ?? []
    let composed = shapedGlyphNames("M1", font: font)
    let paired = shapedGlyphNames("m1 M1", font: font)
    let rightSide = shapedGlyphNames("| I L C P1 P2 M1 M2 M3", font: font).filter { $0.hasSuffix("_r") }

    if !family.hasPrefix("Dental Icons ") || style != "Regular" || !postScript.hasSuffix("-Regular") ||
       !languages.contains("en") || !languages.contains("pt") || composed != ["prof_m1_l"] || paired != ["occl_m1_l", "space", "prof_m1_l"] || rightSide.count != 8 {
        fputs("FAIL \(argument): CoreText identity/shaping mismatch \(family) | \(style) | \(postScript) | \(composed) | \(paired) | right=\(rightSide.count)\n", stderr)
        failed = true
    } else {
        print("PASS \(argument): \(family) | \(style) | \(postScript) | ligatures/context OK")
    }
}

exit(failed ? 1 : 0)
