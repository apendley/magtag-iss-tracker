# Adapted from wrap_text_to_pixels included with the adafruit_display_text
# library to add line break capability for hyphens and slashes.

# Original source:
# SPDX-FileCopyrightText: 2020 Tim C, 2021 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT
# https://github.com/adafruit/Adafruit_CircuitPython_Display_Text/blob/main/adafruit_display_text/__init__.py


try:
    from typing import List, Optional, Tuple

    from fontio import FontProtocol
except ImportError:
    pass

_WRAP_DELIMITERS = ['-', '/']

def _sub_split(line, delimiter):
    output_text = []

    for word in line:
        divided = word.split(delimiter)
        divided_length = len(divided)

        if divided_length > 1:
            for i in range(1, divided_length):
                divided[i - 1] = divided[i - 1] + delimiter

        output_text.extend(divided)

    return output_text

def split_for_wrapping(line):
    split_output = line.split(" ")

    for d in _WRAP_DELIMITERS:
        split_output = _sub_split(split_output, d)

    return split_output

def wrap_text_to_pixels(
    string: str,
    max_width: int,
    font: Optional[FontProtocol] = None,
    indent0: str = "",
    indent1: str = "",
) -> List[str]:
    """wrap_text_to_pixels function
    A helper that will return a list of lines with word-break wrapping.
    Leading and trailing whitespace in your string will be removed. If
    you wish to use leading whitespace see ``indent0`` and ``indent1``
    parameters.

    :param str string: The text to be wrapped.
    :param int max_width: The maximum number of pixels on a line before wrapping.
    :param font: The font to use for measuring the text.
    :type font: ~fontio.FontProtocol
    :param str indent0: Additional character(s) to add to the first line.
    :param str indent1: Additional character(s) to add to all other lines.

    :return: A list of the lines resulting from wrapping the
        input text at ``max_width`` pixels size
    :rtype: List[str]

    """
    if font is None:

        def measure(text):
            return len(text)

    else:
        if hasattr(font, "load_glyphs"):
            font.load_glyphs(string)

        def measure(text):
            total_len = 0
            for char in text:
                this_glyph = font.get_glyph(ord(char))
                if this_glyph:
                    total_len += this_glyph.shift_x
            return total_len

    lines = []
    partial = [indent0]
    width = measure(indent0)
    swidth = measure(" ")
    firstword = True
    for line_in_input in string.split("\n"):
        newline = True
        for index, word in enumerate(split_for_wrapping(line_in_input)):
            wwidth = measure(word)
            word_parts = []
            cur_part = ""

            if wwidth > max_width:
                for char in word:
                    if newline:
                        extraspace = 0
                        leadchar = ""
                    else:
                        extraspace = swidth
                        leadchar = " "
                    if (
                        measure("".join(partial))
                        + measure(cur_part)
                        + measure(char)
                        + measure("-")
                        + extraspace
                        > max_width
                    ):
                        if cur_part:
                            word_parts.append("".join(partial) + leadchar + cur_part + "-")

                        else:
                            word_parts.append("".join(partial))
                        cur_part = char
                        partial = [indent1]
                        newline = True
                    else:
                        cur_part += char
                if cur_part:
                    word_parts.append(cur_part)
                for line in word_parts[:-1]:
                    lines.append(line)
                partial.append(word_parts[-1])
                width = measure(word_parts[-1])
                if firstword:
                    firstword = False
            elif firstword:
                partial.append(word)
                firstword = False
                width += wwidth
            elif width + swidth + wwidth < max_width:
                if index > 0:
                    should_insert_space = True

                    if len(partial) > 0:
                        last_partial = partial[-1]

                        if len(last_partial) > 0:
                            if last_partial[-1] in _WRAP_DELIMITERS:
                                should_insert_space = False
                    
                    if should_insert_space == True:
                        partial.append(" ")                

                partial.append(word)
                width += wwidth + swidth
            else:
                lines.append("".join(partial))
                partial = [indent1, word]
                width = measure(indent1) + wwidth
            if newline:
                newline = False

        lines.append("".join(partial))
        partial = [indent1]
        width = measure(indent1)

    return lines
