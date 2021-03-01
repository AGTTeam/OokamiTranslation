import codecs
import os
import game
from hacktools import common, nitro


def run(firstgame):
    infolder = "data/extract/data/script/"
    outfolder = "data/repack/data/script/"
    infile = "data/wsb_input.txt"
    fontfile = "data/replace/data/font/lcfont12.NFTR"
    if not os.path.isfile(infile):
        common.logError("Input file", infile, "not found")
        return

    encoding = "shift_jis" if firstgame else "shift_jisx0213"
    common.logMessage("Repacking WSB from", infile, "...")
    # Read the glyph size from the font
    if not os.path.isfile(fontfile):
        fontfile = fontfile.replace("replace/", "extract/")
    glyphs = nitro.readNFTR(fontfile).glyphs
    wordwrap = game.wordwrap[0] if firstgame else game.wordwrap[1]
    fixchars = game.getFixChars()
    with codecs.open(infile, "r", "utf-8") as wsb:
        commonsection = common.getSection(wsb, "COMMON", fixchars=fixchars)
        chartot, transtot = common.getSectionPercentage(commonsection)
        files = common.getFiles(infolder, ".wsb")
        for file in common.showProgress(files):
            section = common.getSection(wsb, file, fixchars=fixchars)
            chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
            # Repack the file
            pointerdiff = {}
            pointers = {}
            common.logDebug(" Processing", file, "...")
            insize = os.path.getsize(infolder + file)
            with common.Stream(infolder + file, "rb") as fin:
                with common.Stream(outfolder + file, "wb") as f:
                    # Copy header
                    fin.seek(4)  # 0x10
                    codeoffset = fin.readUInt()
                    if codeoffset == 0 and not firstgame:
                        fin.seek(0)
                        f.write(fin.read())
                        continue
                    fin.seek(8, 1)  # all 0xFF
                    unk = fin.readUInt()
                    textoffset = fin.readUInt()
                    codeoffset2 = fin.readUInt()
                    fin.seek(0)
                    f.write(fin.read(32))
                    # Write new strings
                    while fin.tell() < codeoffset:
                        pos = fin.tell()
                        fpos = f.tell()
                        b1 = fin.readByte()
                        b2 = fin.readByte()
                        f.writeByte(b1)
                        f.writeByte(b2)
                        if (b1 == 0x55 and b2 == 0x08) or (b1 == 0x95 and b2 == 0x10):
                            sjis, oldlen = game.readShiftJIS(fin, b1 == 0x95, False, encoding)
                            # Fix a bugged line with wrong speaker code
                            if file == "event/ev_mou/mou_10.wsb" and sjis == "そうじゃな。|わっちの直感が申すには……>>":
                                f.seek(fpos - 12)
                                f.writeByte(0x53)
                                f.seek(fpos + 2)
                            strreplaced = False
                            if sjis != "" and sjis != ">>":
                                sjissplit = sjis.split(">>")
                                for i in range(len(sjissplit)):
                                    newsjis = sjisline = sjissplit[i]
                                    if sjisline in commonsection:
                                        newsjis = commonsection[sjisline][0]
                                    elif sjisline in section:
                                        newsjis = section[sjisline].pop(0)
                                        if len(section[sjisline]) == 0:
                                            del section[sjisline]
                                    if newsjis != "":
                                        # Disable wordwrap for strings that contain replace codes
                                        if newsjis.count("@<") > 0:
                                            sjissplit[i] = newsjis
                                        # Check for automatic centering
                                        elif newsjis.count("<<") > 0:
                                            sjissplit[i] = common.centerLines(newsjis, glyphs, wordwrap, centercode="<<")
                                        else:
                                            sjissplit[i] = common.wordwrap(newsjis, glyphs, wordwrap)
                                newsjis = ">>".join(sjissplit)
                                if newsjis != sjis and newsjis != "" and newsjis != ">>":
                                    common.logDebug("Repacking", newsjis, "at", common.toHex(pos))
                                    strreplaced = True
                                    if newsjis == "!":
                                        newsjis = ""
                                    newlen = game.writeShiftJIS(f, newsjis, b1 == 0x95, False, 0, encoding, firstgame)
                                    lendiff = newlen - oldlen
                                    if newlen > (0x80 if firstgame else 0x70) and b1 == 0x55:
                                        common.logDebug("String is too long", newlen, "changing to 0x95")
                                        f.seek(fpos)
                                        f.writeByte(0x95)
                                        f.writeByte(0x10)
                                        game.writeShiftJIS(f, newsjis, True, False, 0, encoding, firstgame)
                                        lendiff += 2
                                    if lendiff != 0:
                                        common.logDebug("Adding", lendiff, "at", pos)
                                        pointerdiff[pos - 16] = lendiff
                            if not strreplaced:
                                fin.seek(pos + 2)
                                f.write(fin.read(oldlen + (4 if b1 == 0x95 else 2)))
                        elif (b1, b2) in game.wsbcodes:
                            if (b1, b2) in game.wsbpointers:
                                if b1 == 0x81 and b2 == 0xB9:
                                    f.write(fin.read(2))
                                pointer = fin.readUInt()
                                pointers[f.tell()] = pointer
                                f.writeUInt(pointer)
                            else:
                                f.write(fin.read(game.wsbcodes[(b1, b2)]))
                    # Write code section
                    if codeoffset > 0:
                        newcodeoffset = f.tell()
                        codediff = 0
                        codenum = fin.readUInt()
                        f.writeUInt(codenum)
                        for i in range(codenum):
                            fin.seek(codeoffset + 4 + 4 * i)
                            f.seek(newcodeoffset + 4 + 4 * i)
                            codepointer = fin.readUInt()
                            f.writeUInt(codepointer + codediff)
                            fin.seek(codeoffset + codepointer)
                            f.seek(newcodeoffset + codepointer + codediff)
                            sjis, codelen = game.readShiftJIS(fin, False, True, encoding)
                            strreplaced = False
                            if sjis in section or sjis in commonsection:
                                if sjis in commonsection:
                                    newsjis = commonsection[sjis][0]
                                else:
                                    newsjis = section[sjis].pop(0)
                                    if len(section[sjis]) == 0:
                                        del section[sjis]
                                if newsjis != "":
                                    strreplaced = True
                                    newcodelen = game.writeShiftJIS(f, newsjis, False, True, 0, encoding, firstgame)
                                    if codelen != newcodelen:
                                        codediff += newcodelen - codelen
                            if not strreplaced:
                                fin.seek(codeoffset + codepointer)
                                f.write(fin.read(codelen))
                    f.writeZero(insize - fin.tell())
                    # Write new header offsets
                    f.seek(4)
                    f.writeUInt(common.shiftPointer(codeoffset, pointerdiff))
                    f.seek(8, 1)
                    f.writeUInt(common.shiftPointer(unk, pointerdiff))
                    f.writeUInt(common.shiftPointer(textoffset, pointerdiff))
                    f.writeUInt(common.shiftPointer(codeoffset2, pointerdiff))
                    # Shift pointers
                    for k, v in pointers.items():
                        f.seek(k)
                        f.writeUInt(common.shiftPointer(v, pointerdiff))
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))
