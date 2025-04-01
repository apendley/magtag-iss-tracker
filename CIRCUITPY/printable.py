from fonts import contains_glyph

# Take advantage of the MagTag/ESP32-S2's massive 2MB PSRAM to provide a 
# mapping from unicode code points to (hopefully reasonable) ascii substitutes.
# Fair warning: I used ChatGPT to help generate this map, and I have not double-checked 
# every single mapping. I am 0% vouching for its accuracy, and if you use it, you do so 
# at your own risk. Corrections by speakers of any of the included languages are welcome.
_unicode_to_ascii_map = {
    # Latin characters with acute, grave, circumflex, tilde, umlaut, and other common accents
    0x00C0: 'A',  # À
    0x00C1: 'A',  # Á
    0x00C2: 'A',  # Â
    0x00C3: 'A',  # Ã
    0x00C4: 'A',  # Ä
    0x00C5: 'A',  # Å
    0x00C6: 'AE', # Æ
    0x00C7: 'C',  # Ç
    0x00C8: 'E',  # È
    0x00C9: 'E',  # É
    0x00CA: 'E',  # Ê
    0x00CB: 'E',  # Ë
    0x00CC: 'I',  # Ì
    0x00CD: 'I',  # Í
    0x00CE: 'I',  # Î
    0x00CF: 'I',  # Ï
    0x00D1: 'N',  # Ñ
    0x00D2: 'O',  # Ò
    0x00D3: 'O',  # Ó
    0x00D4: 'O',  # Ô
    0x00D5: 'O',  # Õ
    0x00D6: 'O',  # Ö
    0x00D8: 'O',  # Ø
    0x00D9: 'U',  # Ù
    0x00DA: 'U',  # Ú
    0x00DB: 'U',  # Û
    0x00DC: 'U',  # Ü
    0x00DD: 'Y',  # Ý
    0x0152: 'OE', # Œ
    0x00DF: 'ss', # ß
    0x00E0: 'a',  # à
    0x00E1: 'a',  # á
    0x00E2: 'a',  # â
    0x00E3: 'a',  # ã
    0x00E4: 'a',  # ä
    0x00E5: 'a',  # å
    0x00E6: 'ae', # æ
    0x00E7: 'c',  # ç
    0x00E8: 'e',  # è
    0x00E9: 'e',  # é
    0x00EA: 'e',  # ê
    0x00EB: 'e',  # ë
    0x00EC: 'i',  # ì
    0x00ED: 'i',  # í
    0x00EE: 'i',  # î
    0x00EF: 'i',  # ï
    0x00F1: 'n',  # ñ
    0x00F2: 'o',  # ò
    0x00F3: 'o',  # ó
    0x00F4: 'o',  # ô
    0x00F5: 'o',  # õ
    0x00F6: 'o',  # ö
    0x00F8: 'o',  # ø
    0x00F9: 'u',  # ù
    0x00FA: 'u',  # ú
    0x00FB: 'u',  # û
    0x00FC: 'u',  # ü
    0x00FD: 'y',  # ý
    0x00FF: 'y',  # ÿ

    # Characters with macron, caron, and other diacritic marks
    0x0100: 'A',  # Ā
    0x0102: 'A',  # Ă
    0x0104: 'A',  # Ą
    0x0112: 'E',  # Ē
    0x0114: 'E',  # Ĕ
    0x0116: 'E',  # Ė
    0x0118: 'E',  # Ę
    0x011A: 'E',  # Ě
    0x012A: 'I',  # Ī
    0x012C: 'I',  # Ĭ
    0x012E: 'I',  # Į
    0x0130: 'I',  # İ
    0x014C: 'O',  # Ō
    0x014E: 'O',  # Ŏ
    0x0150: 'O',  # Ő
    0x016A: 'U',  # Ū
    0x016C: 'U',  # Ŭ
    0x016E: 'U',  # Ů
    0x0170: 'U',  # Ű
    0x0172: 'U',  # Ų
    0x0176: 'Y',  # Ŷ
    0x0179: 'Z',  # Ź
    0x017B: 'Z',  # Ż
    0x017D: 'Z',  # Ž

    # Ligatures used in various languages (common in French, German, Danish, etc.)
    0x0152: 'OE', # Œ
    0x00E6: 'ae', # æ

    # Characters used in Scandinavian languages (e.g., Danish, Norwegian, Swedish)
    0x00C5: 'A',  # Å
    0x00E5: 'a',  # å
    0x00D8: 'O',  # Ø
    0x00F8: 'o',  # ø
    0x00C4: 'A',  # Ä
    0x00E4: 'a',  # ä
    0x00D6: 'O',  # Ö
    0x00F6: 'o',  # ö

    # Characters used in Eastern European and Slavic languages (e.g., Czech, Slovak, Polish)
    0x010C: 'C',  # Č
    0x0107: 'c',  # č
    0x010E: 'D',  # Ď
    0x0111: 'd',  # ď
    0x011A: 'E',  # Ė
    0x011B: 'e',  # ė
    0x0158: 'R',  # Ř
    0x0159: 'r',  # ř
    0x0160: 'S',  # Š
    0x0161: 's',  # š
    0x017D: 'Z',  # Ž
    0x017E: 'z',  # ž
    0x0141: 'L',  # Ł
    0x0142: 'l',  # ł

    # Characters from the Baltic languages (e.g., Latvian, Lithuanian)
    0x0112: 'E',  # Ē
    0x0113: 'e',  # ē
    0x0136: 'K',  # Ķ
    0x0137: 'k',  # ķ
    0x0139: 'L',  # Ĺ
    0x013A: 'l',  # ĺ
    0x014C: 'O',  # Ō
    0x014D: 'o',  # ō

    # Characters used in Romanian (e.g., Ș, Ț) and some other regional variations
    0x0218: 'S',  # Ș
    0x0219: 's',  # ș
    0x021A: 'T',  # Ţ
    0x021B: 't',  # ţ

    # Characters used in Turkish (e.g., İ, ı, Ğ, Ş)
    0x0130: 'I',  # İ
    0x0131: 'i',  # ı
    0x011E: 'G',  # Ğ
    0x011F: 'g',  # ğ
    0x015E: 'S',  # Ş
    0x015F: 's',  # ş

    # Iberian Peninsula (Spanish, Portuguese)
    0x00D1: 'N',  # Ñ
    0x00F1: 'n',  # ñ
    0x00C7: 'C',  # Ç
    0x00E7: 'c',  # ç

    # Special characters for Eastern European languages (Hungarian, Ukrainian, etc.)
    0x0150: 'O',  # Ő
    0x0151: 'o',  # ő
    0x0170: 'U',  # Ű
    0x0171: 'u',  # ű

    # Characters from French, Italian, and other Romance languages (é, è, ç)
    0x00E9: 'e',  # é
    0x00E8: 'e',  # è
    0x00EA: 'e',  # ê
    0x00EB: 'e',  # ë
    0x00E7: 'c',  # ç
    
    # Miscellaneous European characters
    0x011E: 'G',  # Ğ
    0x011F: 'g',  # ğ
    0x0130: 'I',  # İ
    0x0131: 'i',  # ı
    0x015E: 'S',  # Ş
    0x015F: 's',  # ş

    # Greek letters (converted to closest Latin equivalent for display)
    0x03B1: 'a',  # α
    0x03B2: 'b',  # β
    0x03B3: 'g',  # γ
    0x03B4: 'd',  # δ
    0x03B5: 'e',  # ε
    0x03B6: 'z',  # ζ
    0x03B7: 'h',  # η
    0x03B8: 'th', # θ
    0x03B9: 'i',  # ι
    0x03BA: 'k',  # κ
    0x03BB: 'l',  # λ
    0x03BC: 'm',  # μ
    0x03BD: 'n',  # ν
    0x03BE: 'x',  #,

    # Uppercase Cyrillic
    0x0410: "A",   # А -> A
    0x0411: "B",   # Б -> B
    0x0412: "V",   # В -> V
    0x0413: "G",   # Г -> G
    0x0414: "D",   # Д -> D
    0x0415: "E",   # Е -> E
    0x0401: "Yo",  # Ё -> Yo (or just E)
    0x0416: "Zh",  # Ж -> Zh
    0x0417: "Z",   # З -> Z
    0x0418: "I",   # И -> I
    0x0419: "J",   # Й -> J (or I)
    0x041A: "K",   # К -> K
    0x041B: "L",   # Л -> L
    0x041C: "M",   # М -> M
    0x041D: "N",   # Н -> N
    0x041E: "O",   # О -> O
    0x041F: "P",   # П -> P
    0x0420: "R",   # Р -> R
    0x0421: "S",   # С -> S
    0x0422: "T",   # Т -> T
    0x0423: "U",   # У -> U
    0x0424: "F",   # Ф -> F
    0x0425: "H",   # Х -> H
    0x0426: "C",   # Ц -> C
    0x0427: "Ch",  # Ч -> Ch
    0x0428: "Sh",  # Ш -> Sh
    0x0429: "Shch",# Щ -> Shch
    0x042B: "Y",   # Ы -> Y
    0x042C: "E",   # Э -> E
    0x042E: "Yu",  # Ю -> Yu
    0x042F: "Ya",  # Я -> Ya

    # Lowercase Cyrillic
    0x0430: "a",   # а -> a
    0x0431: "b",   # б -> b
    0x0432: "v",   # в -> v
    0x0433: "g",   # г -> g
    0x0434: "d",   # д -> d
    0x0435: "e",   # е -> e
    0x0451: "yo",  # ё -> yo
    0x0436: "zh",  # ж -> zh
    0x0437: "z",   # з -> z
    0x0438: "i",   # и -> i
    0x0439: "j",   # й -> j (or i)
    0x043A: "k",   # к -> k
    0x043B: "l",   # л -> l
    0x043C: "m",   # м -> m
    0x043D: "n",   # н -> n
    0x043E: "o",   # о -> o
    0x043F: "p",   # п -> p
    0x0440: "r",   # р -> r
    0x0441: "s",   # с -> s
    0x0442: "t",   # т -> t
    0x0443: "u",   # у -> u
    0x0444: "f",   # ф -> f
    0x0445: "h",   # х -> h
    0x0446: "c",   # ц -> c
    0x0447: "ch",  # ч -> ch
    0x0448: "sh",  # ш -> sh
    0x0449: "shch",# щ -> shch
    0x044B: "y",   # ы -> y
    0x044C: "e",   # э -> e
    0x044E: "yu",  # ю -> yu
    0x044F: "ya",  # я -> ya

    # Special characters
    0x0454: "u",   # є -> u
    0x0456: "i",   # і -> i
    0x0457: "yi",  # ї -> yi
    0x0458: "j",   # ј -> j
    0x045A: "l",   # љ -> l
    0x045C: "nj",  # њ -> nj
    0x045E: "ts",  # тс (non-standard)
    0x0460: "s",   # ш -> s
    0x0462: "s",   # шч

    # Arabic
    0x0621: "'",   # ء -> '
    0x0622: "A",   # آ -> A
    0x0623: "A",   # أ -> A
    0x0624: "A",   # إ -> A
    0x0625: "E",   # ة -> E
    0x0626: "E",   # ة -> E
    0x0627: "A",   # ا -> A
    0x0628: "b",   # ب -> b
    0x0629: "t",   # ت -> t
    0x062A: "t",   # ت -> t
    0x062B: "th",  # ث -> th
    0x062C: "j",   # ج -> j
    0x062D: "h",   # ح -> h
    0x062E: "kh",  # خ -> kh
    0x062F: "d",   # د -> d
    0x0630: "dh",  # ذ -> dh
    0x0631: "r",   # ر -> r
    0x0632: "z",   # ز -> z
    0x0633: "s",   # س -> s
    0x0634: "sh",  # ش -> sh
    0x0635: "s",   # ص -> s
    0x0636: "sh",  # ض -> sh
    0x0637: "s",   # ط -> t
    0x0638: "th",  # ظ -> th
    0x0639: "a",   # ع -> a
    0x063A: "gh",  # غ -> gh
    0x063B: "f",   # ف -> f
    0x063C: "q",   # ق -> q
    0x063D: "k",   # ك -> k
    0x063E: "l",   # ل -> l
    0x063F: "m",   # م -> m
    0x0640: "n",   # ن -> n
    0x0641: "f",   # ف -> f
    0x0642: "q",   # ق -> q
    0x0643: "k",   # ك -> k
    0x0644: "l",   # ل -> l
    0x0645: "m",   # م -> m
    0x0646: "n",   # ن -> n
    0x0647: "h",   # ه -> h
    0x0648: "w",   # و -> w
    0x0649: "y",   # ى -> y
    0x064A: "y",   # ي -> y    

    # Farsi
    0x067E: "p",   # پ -> p
    0x0686: "ch",  # چ -> ch
    0x0698: "zh",  # ژ -> zh
    0x06A9: "k",   # ک -> k
    0x06AF: "g",   # گ -> g

    # Hebrew
    0x05D0: "A",   # א -> A
    0x05D1: "B",   # ב -> B
    0x05D2: "G",   # ג -> G
    0x05D3: "D",   # ד -> D
    0x05D4: "H",   # ה -> H
    0x05D5: "V",   # ו -> V
    0x05D6: "Z",   # ז -> Z
    0x05D7: "Ch",  # ח -> Ch
    0x05D8: "T",   # ט -> T
    0x05D9: "Y",   # י -> Y
    0x05DA: "K",   # כ -> K
    0x05DB: "L",   # ל -> L
    0x05DC: "M",   # מ -> M
    0x05DD: "N",   # נ -> N
    0x05DE: "S",   # ס -> S
    0x05DF: "E",   # ע -> E
    0x05E0: "P",   # פ -> P
    0x05E1: "Ts",  # צ -> Ts
    0x05E2: "Q",   # ק -> Q
    0x05E3: "R",   # ר -> R
    0x05E4: "Sh",  # ש -> Sh
    0x05E5: "T",   # ת -> T    
}

# Returns whether text can be printed without any "?" characters.
# If substitute_ascii is True, ascii substitions are are allowed, where possible.
def is_printable(text, substitute_ascii):
    if text is None:
        return False

    for char in text:
        c = get_printable_character(char, substitute_ascii=substitute_ascii)

        if c is None:
            return False

    return True

# Convert non-printable characters into printable characters.
# If substitute_ascii is True, an attempt will be made
# to transliterate unrecognized characters into ASCII substitutes.
# If no substitution can be found, unrecognized character will
# be replaced with the fallback.
def make_printable(text, substitute_ascii=True, fallback='?'):
    if text is None:
        return ""

    validated_string = ""

    for char in text:
        printable = get_printable_character(char, substitute_ascii)

        if printable is not None:
            validated_string += printable
        else:
            validated_string += fallback

    return validated_string

# Given a character, determine if it can be printed by our fonts.
# If substitute_ascii is True, an attempt will be made
# to transliterate unrecognized characters into ASCII substitutes.
# If no printable character can be found, return None.
# Otherwise, return the printable character.
def get_printable_character(char, substitute_ascii):
    code_point = ord(char)

    # First, check to see if the code point is supported by the font.
    if contains_glyph(code_point):
        return char

    # If not, and if specified, attempt to substitute the
    # code points not in the font with "reduced" ascii equivalents.
    if substitute_ascii and (code_point in _unicode_to_ascii_map):
        return _unicode_to_ascii_map[code_point]
    
    # Give up and let the caller decide how to handle the character.
    return None
