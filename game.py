import codecs
import os
from hacktools import common, nitro

# Ranges for BIN string locations
binrange = [
    (0x952cc, 0xa0320),
    (0xc3a78, 0xd73cf)
]
freeranges = [
    [(0x98ce4, 0x98e66), (0x98e74, 0x98ec7), (0x98ed4, 0x99303)],
    [(0xc8778, 0xc8a70), (0xc8ab0, 0xc926d), (0xc93e8, 0xc9668), (0xc9714, 0xc98af), (0xcb040, 0x0cb743)]
]
monthsection = [
    (0x97920, 0x9797f),
    (0xc6bf4, 0xc6c50)
]
skipsection = [
    [(0x9791c, 0x9791f)],
    [(0xc6bec, 0xc6bf3), (0xcfc80, 0xcfc83), (0xc73cd, 0xc73d1), (0xc3b78, 0xc3b7b), (0xc4540, 0xc4543), (0xd50a8, 0xd50ab)],
]
# Identifier and size of WSB code blocks
wsbcodes = {
    (0x81, 0xb9): 6, (0x81, 0x1a): 6,
    (0x81, 0x11): 4, (0x81, 0x12): 4, (0x89, 0x04): 4,
    (0xca, 0x00): 4, (0xcb, 0x00): 4, (0xcc, 0x00): 4, (0xcd, 0x00): 4, (0xce, 0x00): 4, (0xcf, 0x00): 4,
    (0xd0, 0x00): 4, (0xd1, 0x00): 4, (0xd7, 0x00): 4,
    (0x98, 0x00): 2,
    (0x88, 0x00): 2, (0x88, 0x01): 2, (0x88, 0x04): 2,
    (0x89, 0x00): 2, (0x89, 0x01): 2,
    (0x41, 0x09): 2, (0x41, 0x0A): 2, (0x41, 0x29): 2, (0x41, 0x2A): 2, (0x41, 0x49): 2, (0x41, 0x4a): 2, (0x41, 0x69): 2, (0x41, 0x8c): 2,
    (0x42, 0x09): 2, (0x42, 0x29): 2,
    (0x43, 0x29): 2,
    (0x44, 0x09): 2,
    (0x45, 0x29): 2,
    (0x54, 0x09): 2, (0x54, 0x29): 2,
    (0x16, 0x00): 0,
    (0x00, 0x00): 0,
}
# Identifiers of WSB code blocks containing a pointer
wsbpointers = [(0x81, 0xb9), (0xca, 0x00), (0xcb, 0x00), (0xcc, 0x00), (0xcd, 0x00), (0xce, 0x00), (0xcf, 0x00), (0xd0, 0x00), (0xd7, 0x00)]
# Wordwrap value
wordwrap = (205, 215)


# Game-specific string
def writeShiftJIS(f, s, len2=False, untilZero=False, maxlen=0, encoding="shift_jis", firstgame=True):
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
            if maxlen > 0 and i + 1 >= maxlen:
                return -1
            code = s[x+1] + s[x+2]
            f.write(bytes.fromhex(code))
            x += 3
            i += 1
            j += 1
        elif c == "U" and x < len(s) - 4 and s[x:x+4] == "UNK(":
            if maxlen > 0 and i + 2 >= maxlen:
                return -1
            code = s[x+4] + s[x+5]
            f.write(bytes.fromhex(code))
            code = s[x+6] + s[x+7]
            f.write(bytes.fromhex(code))
            x += 8
            i += 2
            j += 2
        elif c == ">" and s[x+1] == ">":
            if maxlen > 0 and i + 2 >= maxlen:
                return -1
            x += 1
            f.writeByte(0x81)
            f.writeByte(0xa5)
            i += 2
            j += 1
        elif c == "|":
            if maxlen > 0 and i + 2 >= maxlen:
                return -1
            f.writeByte(0x0d)
            f.writeByte(0x0a)
            i += 2
            j += 2
        elif ord(c) < 128:
            if maxlen > 0 and i + 1 >= maxlen:
                return -1
            f.writeByte(ord(c))
            i += 1
            j += 1
        else:
            if maxlen > 0 and i + 2 >= maxlen:
                return -1
            f.write(c.encode(encoding))
            i += 2
            j += 1
        x += 1
        if maxlen > 0 and i >= maxlen:
            return -1
    if untilZero:
        padding = 1
    else:
        if firstgame:
            padding = 4 - (i % 2)
        else:
            padding = 1 + ((i + 1) % 4)
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
            if b1 == 0x0d and b2 == 0x0a:
                sjis += "|"
                i += 2
                j += 2
            elif b1 == 0x81 and b2 == 0xa5:
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
    ismonth = monthsection is not None and f.tell() >= monthsection[0] and f.tell() <= monthsection[1]
    while True:
        if skipsection is not None:
            for skiprange in skipsection:
                if f.tell() >= skiprange[0] and f.tell() <= skiprange[1]:
                    return ""
        b1 = f.readByte()
        if b1 == 0:
            return ret
        if ((b1 >= 0x20 and b1 <= 0x7e) or b1 == 0x0a or b1 == 0xa5) and (len(ret) > 0 or chr(b1) == "%" or chr(b1) == "L" or ismonth):
            if b1 == 0xa5:
                ret += "･"
            elif b1 == 0x0a:
                ret += "|"
            else:
                ret += chr(b1)
            continue
        b2 = f.readByte()
        if b1 == 0x0d and b2 == 0x0a:
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


def getFixChars():
    fixchars = []
    if not os.path.isfile("data/fontconfig.txt"):
        return fixchars
    with codecs.open("data/fontconfig.txt", "r", "utf-8") as f:
        chars = common.getSection(f, "", "|")
        for char in chars:
            fixchars.append((char, chars[char][0].replace("<3D>", "=")))
    return fixchars


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


def readKBG(f):
    # Read palette
    pallen = 0x200
    colornum = 0x100
    palettes = []
    for i in range(pallen // (colornum * 2)):
        palette = []
        for j in range(colornum):
            palette.append(common.readPalette(f.readUShort()))
        palettes.append(palette)
    indexedpalettes = {i: palettes[i] for i in range(0, len(palettes))}
    # Read tiles
    ncgr = nitro.NCGR()
    ncgr.tiles = []
    ncgr.width = f.readUInt() * 8
    ncgr.height = f.readUInt() * 8
    ncgr.bpp = 8
    ncgr.tilesize = 8
    ncgr.lineal = False
    ncgr.tilelen = (ncgr.width // 8) * (ncgr.height // 8) * 0x40
    ncgr.tileoffset = f.tell()
    return indexedpalettes, ncgr
