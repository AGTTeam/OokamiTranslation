import codecs
import os
import game
from hacktools import common


def writeLine(out, pos, b1, b2, line):
    out.write(str(pos).zfill(5) + " 0x" + common.toHex(b1) + ", 0x" + common.toHex(b2) + ": " + line + "  \n")


def run(firstgame, analyzefile):
    infolder = "data/extract/data/script/"
    outfile = "data/wsb_output.txt"
    commonfile = "data/common.txt"
    analyzeout = "data/wsb_analysis.txt"

    commonstr = {}
    # Read common strings from another file
    if os.path.isfile(commonfile):
        with codecs.open(commonfile, "r", "utf-8") as commonf:
            commonstr = common.getSection(commonf, "COMMON")
    encoding = "shift_jis" if firstgame else "shift_jisx0213"
    common.logMessage("Extracting WSB to", outfile, "...")
    with codecs.open(analyzeout, "w", "utf-8") as a:
        with codecs.open(outfile, "w", "utf-8") as out:
            if len(commonstr) > 0:
                out.write("!FILE:COMMON\n")
                for s in commonstr:
                    out.write(s + "=\n")
            files = common.getFiles(infolder, ".wsb")
            for file in common.showProgress(files):
                analyze = analyzefile != "" and file.endswith(analyzefile)
                first = True
                common.logDebug("Processing", file, "...")
                with common.Stream(infolder + file, "rb") as f:
                    f.seek(4)  # 0x10
                    codeoffset = f.readUInt()
                    f.seek(8, 1)  # all 0xFF
                    unk = f.readUInt()
                    textoffset = f.readUInt()
                    codeoffset2 = f.readUInt()
                    common.logDebug("codeoffset:", codeoffset, "unk:", unk, "textoffset:", textoffset, "codeoffset2:", codeoffset2)
                    f.seek(4, 1)
                    # Parse the various code blocks while looking for strings
                    while f.tell() < codeoffset:
                        pos = f.tell()
                        b1 = f.readByte()
                        b2 = f.readByte()
                        if (b1 == 0x55 and b2 == 0x08) or (b1 == 0x95 and b2 == 0x10):
                            # Found a string pointer
                            if analyze:
                                lenline = f.readBytes(4 if b1 == 0x95 else 2)
                                f.seek(-(4 if b1 == 0x95 else 2), 1)
                            sjis, strlen = game.readShiftJIS(f, b1 == 0x95, False, encoding)
                            if sjis != "" and sjis != ">>" and sjis != "　":
                                sjissplit = sjis.split(">>")
                                for sjisline in sjissplit:
                                    if sjisline != "" and sjisline != "　" and sjisline not in commonstr:
                                        if first:
                                            out.write("!FILE:" + file + "\n")
                                            first = False
                                        out.write(sjisline + "=\n")
                            if analyze:
                                writeLine(a, pos, b1, b2, lenline + sjis)
                        elif (b1, b2) in game.wsbcodes:
                            if analyze:
                                writeLine(a, pos, b1, b2, f.readBytes(game.wsbcodes[(b1, b2)]))
                            else:
                                f.seek(game.wsbcodes[(b1, b2)], 1)
                        else:
                            if analyze:
                                writeLine(a, pos, b1, b2, "Unknown!")
                    if codeoffset > 0:
                        codenum = f.readUInt()
                        for i in range(codenum):
                            f.seek(codeoffset + 4 + 4 * i)
                            codepointer = f.readUInt()
                            f.seek(codeoffset + codepointer)
                            sjis, codelen = game.readShiftJIS(f, False, True, encoding)
                            # Ignore ASCII strings and a particular debug line found in every file
                            if not common.isAscii(sjis) and sjis.find("%d, %d") < 0 and sjis not in commonstr:
                                if first:
                                    out.write("!FILE:" + file + "\n")
                                    first = False
                                out.write(sjis + "=\n")
                            if analyze:
                                writeLine(a, i, 0, 0, str(codepointer) + " " + sjis)
    common.logMessage("Done! Extracted", len(files), "files")
