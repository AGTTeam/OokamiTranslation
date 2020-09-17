from hacktools import common, nitro

# Ranges for BIN string locations
binrange = [
    (0x952CC, 0xA0320),
    (0xC3A78, 0xD73C0)
]
freeranges = [
    [(0x98ce4, 0x98e66), (0x98e74, 0x98ec7), (0x98ed4, 0x99303)],
    None
]
# Identifier and size of WSB code blocks
wsbcodes = {
    (0x81, 0xB9): 6, (0x81, 0x1A): 6,
    (0x81, 0x11): 4, (0x81, 0x12): 4, (0x89, 0x04): 4,
    (0xCA, 0x00): 4, (0xCB, 0x00): 4, (0xCC, 0x00): 4, (0xCD, 0x00): 4, (0xCE, 0x00): 4, (0xCF, 0x00): 4,
    (0xD0, 0x00): 4, (0xD1, 0x00): 4, (0xD7, 0x00): 4,
    (0x98, 0x00): 2,
    (0x88, 0x00): 2, (0x88, 0x01): 2, (0x88, 0x04): 2,
    (0x89, 0x00): 2, (0x89, 0x01): 2,
    (0x41, 0x09): 2, (0x41, 0x0A): 2, (0x41, 0x29): 2, (0x41, 0x2A): 2, (0x41, 0x49): 2, (0x41, 0x4A): 2, (0x41, 0x69): 2, (0x41, 0x8C): 2,
    (0x42, 0x09): 2, (0x42, 0x29): 2,
    (0x43, 0x29): 2,
    (0x44, 0x09): 2,
    (0x45, 0x29): 2,
    (0x54, 0x09): 2, (0x54, 0x29): 2,
    (0x16, 0x00): 0
}
# Identifiers of WSB code blocks containing a pointer
wsbpointers = [(0xCA, 0x00), (0xCB, 0x00), (0xCC, 0x00), (0xCD, 0x00), (0xCE, 0x00), (0xCF, 0x00), (0xD0, 0x00), (0xD7, 0x00)]
# Characters to replace when reading a section
fixchars = [("’", "'"), ("”", "\""), ("“", "{"), ("‘", "}")]


# Game-specific string
def writeShiftJIS(f, s, len2=False, untilZero=False, maxlen=0, encoding="shift_jis"):
    s = s.replace("～", "〜")
    if not untilZero:
        pos = f.tell()
        if len2:
            f.writeShort(0)
            f.writeShort(0)
        else:
            f.writeByte(0)
            f.writeByte(0)
    i = j = 0
    x = 0
    while x < len(s):
        c = s[x]
        if c == "<" and x < len(s) - 3 and s[x+3] == ">":
            code = s[x+1] + s[x+2]
            f.write(bytes.fromhex(code))
            x += 3
            i += 1
            j += 1
        elif c == "U" and x < len(s) - 4 and s[x:x+4] == "UNK(":
            code = s[x+4] + s[x+5]
            f.write(bytes.fromhex(code))
            code = s[x+6] + s[x+7]
            f.write(bytes.fromhex(code))
            x += 8
            i += 2
            j += 2
        elif c == ">" and s[x+1] == ">":
            x += 1
            f.writeByte(0x81)
            f.writeByte(0xA5)
            i += 2
            j += 1
        elif c == "|":
            f.writeByte(0x0D)
            f.writeByte(0x0A)
            i += 2
            j += 2
        elif ord(c) < 128:
            f.writeByte(ord(c))
            i += 1
            j += 1
        else:
            f.write(c.encode(encoding))
            i += 2
            j += 1
        x += 1
        if maxlen > 0 and i >= maxlen:
            return -1
    if untilZero:
        padding = 1
    else:
        padding = 4 - (i % 2)
    for x in range(padding):
        f.writeByte(0x00)
        i += 1
        j += 1
    if not untilZero:
        endpos = f.tell()
        f.seek(pos)
        if len2:
            f.writeShort(j)
            f.writeShort(i)
        else:
            f.writeByte(j)
            f.writeByte(i)
        f.seek(endpos)
    return i


def writeBINShiftJIS(f, s, maxlen, encoding):
    return writeShiftJIS(f, s, False, True, maxlen, encoding)


def readShiftJIS(f, len2=False, untilZero=False, encoding="shift_jis"):
    if untilZero:
        strlen2 = 999
    else:
        if len2:
            strlen = f.readUShort()
            strlen2 = f.readUShort()
        else:
            strlen = f.readByte()
            strlen2 = f.readByte()
    sjis = ""
    i = j = 0
    padding = 0
    while i < strlen2:
        b1 = f.readByte()
        if b1 == 0x00:
            i += 1
            j += 1
            padding += 1
            if untilZero:
                return sjis, i
        else:
            b2 = f.readByte()
            if b1 == 0x0D and b2 == 0x0A:
                sjis += "|"
                i += 2
                j += 2
            elif b1 == 0x81 and b2 == 0xA5:
                sjis += ">>"
                i += 2
                j += 1
            elif not common.checkShiftJIS(b1, b2):
                f.seek(-1, 1)
                sjis += chr(b1)
                i += 1
                j += 1
            else:
                f.seek(-2, 1)
                try:
                    sjis += f.read(2).decode(encoding).replace("〜", "～")
                except UnicodeDecodeError:
                    common.logDebug("UnicodeDecodeError at", f.tell() - 2)
                    sjis += "UNK(" + common.toHex(b1) + common.toHex(b2) + ")"
                i += 2
                j += 1
    if not untilZero and j != strlen:
        common.logWarning("Wrong strlen", strlen, j)
    return sjis, i


def writeUNK(b1, b2):
    if b1 >= 32 and b1 <= 126 and b2 >= 32 and b2 <= 126:
        return chr(b1) + chr(b2)
    return "UNK(" + common.toHex(b1) + common.toHex(b2) + ")"


def detectShiftJIS(f, encoding="shift_jis"):
    ret = ""
    unk = 0
    monthsection = f.tell() >= 0x97920 and f.tell() <= 0x9797f
    while True:
        if f.tell() >= 0x9791c and f.tell() <= 0x9791f:
            return ""
        b1 = f.readByte()
        if b1 == 0:
            return ret
        if ((b1 >= 0x20 and b1 <= 0x7E) or b1 == 0x0A or b1 == 0xA5) and (len(ret) > 0 or chr(b1) == "%" or chr(b1) == "L" or monthsection):
            if b1 == 0xA5:
                ret += "･"
            elif b1 == 0x0A:
                ret += "|"
            else:
                ret += chr(b1)
            continue
        b2 = f.readByte()
        if b1 == 0x0D and b2 == 0x0A:
            ret += "||"
        elif common.checkShiftJIS(b1, b2):
            f.seek(-2, 1)
            try:
                ret += f.read(2).decode(encoding).replace("〜", "～")
            except UnicodeDecodeError:
                if unk >= 4:
                    return ""
                ret += writeUNK(b1, b2)
                unk += 1
        elif len(ret) > 0 and unk < 4:
            ret += writeUNK(b1, b2)
            unk += 1
        else:
            return ""


def readImage(infolder, file, extension):
    palettefile = file.replace(extension, ".NCLR")
    mapfile = file.replace(extension, ".NSCR")
    cellfile = file.replace(extension, ".NCER")
    # Fix palette name for shared palettes
    if file.startswith("goodsinstance/"):
        palettefile = "goodsinstance/goodsinstance.NCLR"
    palettes, image, map, cell, width, height = nitro.readNitroGraphic(infolder + palettefile, infolder + file, infolder + mapfile, infolder + cellfile)
    # Ignore map for this particular file
    if file == "cg/cg_shita.NCGR":
        map = None
        width = image.width
        height = image.height
    return palettes, image, map, cell, width, height, mapfile, cellfile
