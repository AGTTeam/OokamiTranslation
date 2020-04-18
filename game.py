from hacktools import common, nitro

# Control codes found in strings
codes = [0x0D, 0x0A]
# Control codes found in BIN strings
bincodes = [0x0A, 0x20, 0xA5]
# Ranges for BIN string locations
binrange = [(611020, 656160), (801400, 881600)]
# Identifier and size of WSB code blocks
wsbcodes = {
    (0x81, 0xB9): 6, (0x81, 0x1A): 6,
    (0x81, 0x11): 4, (0x81, 0x12): 4, (0x89, 0x04): 4,
    (0xCA, 0x00): 4, (0xCB, 0x00): 4, (0xCD, 0x00): 4, (0xCE, 0x00): 4, (0xCF, 0x00): 4,
    (0xD0, 0x00): 4, (0xD1, 0x00): 4, (0xD7, 0x00): 4,
    (0x98, 0x00): 2,
    (0x88, 0x00): 2, (0x88, 0x01): 2, (0x88, 0x04): 2,
    (0x89, 0x00): 2, (0x89, 0x01): 2,
    (0x41, 0x09): 2, (0x41, 0x0A): 2, (0x41, 0x29): 2, (0x41, 0x2A): 2, (0x41, 0x49): 2, (0x41, 0x4A): 2, (0x41, 0x69): 2, (0x41, 0x8C): 2,
    (0x42, 0x29): 2,
    (0x54, 0x09): 2, (0x54, 0x29): 2
}
# Identifiers of WSB code blocks containing a pointer
wsbpointers = [(0xCA, 0x00), (0xCB, 0x00), (0xCD, 0x00), (0xCE, 0x00), (0xCF, 0x00), (0xD0, 0x00), (0xD7, 0x00)]


# Game-specific string
def writeShiftJIS(f, s, len2=False, untilZero=False, maxlen=0, encoding="shift_jis"):
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
                    sjis += f.read(2).decode(encoding)
                except UnicodeDecodeError:
                    common.logDebug("UnicodeDecodeError")
                    sjis += "[ERROR" + str(f.tell() - 2) + "]"
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
    while True:
        b1 = f.readByte()
        if b1 == 0:
            if (ret.count("UNK(") * 9) + (ret.count("<") * 4) == len(ret):
                return ""
            return ret
        if ret != "" and b1 in bincodes:
            if b1 == 0xA5:
                ret += "･"
            else:
                ret += "<" + common.toHex(b1) + ">"
            continue
        b2 = f.readByte()
        if b1 == 0x0D and b2 == 0x0A:
            ret += "|"
        elif common.checkShiftJIS(b1, b2):
            f.seek(-2, 1)
            try:
                ret += f.read(2).decode(encoding)
            except UnicodeDecodeError:
                if unk >= 5:
                    return ""
                ret += writeUNK(b1, b2)
                unk += 1
        elif len(ret) > 0 and unk < 5:
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
