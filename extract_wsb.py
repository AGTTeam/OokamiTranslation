import codecs
import game
from hacktools import common


def writeLine(out, pos, b1, b2, line):
    out.write(str(pos).zfill(5) + " 0x" + common.toHex(b1) + ", 0x" + common.toHex(b2) + ": " + line + "  \n")


def run(firstgame, analyzefile):
    infolder = "data/extract/data/script/"
    outfile = "data/wsb_output.txt"
    analyzeout = "data/wsb_analysis.txt"

    foundstr = {}
    checkstr = {}
    commonstr = []
    common.logMessage("Extracting WSB to", outfile, "...")
    with codecs.open(analyzeout, "w", "utf-8") as a:
        with codecs.open(outfile, "w", "utf-8") as out:
            files = common.getFiles(infolder, ".wsb")
            for file in common.showProgress(files):
                analyze = file.endswith(analyzefile)
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
                            sjis, strlen = game.readShiftJIS(f, b1 == 0x95)
                            if sjis != "" and sjis != ">>" and sjis != "　":
                                if file not in foundstr:
                                    foundstr[file] = []
                                sjissplit = sjis.split(">>")
                                for sjisline in sjissplit:
                                    if sjisline != "" and sjisline != "　":
                                        foundstr[file].append(sjisline)
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
                            sjis, codelen = game.readShiftJIS(f, False, True)
                            # Ignore ASCII strings and a particular debug line found in every file
                            if not common.isAscii(sjis) and sjis.find("%d, %d") < 0:
                                foundstr[file].append(sjis)
                            if analyze:
                                writeLine(a, i, 0, 0, str(codepointer) + " " + sjis)
            # Check duplicates
            for k, v in foundstr.items():
                for s in v:
                    if s not in checkstr:
                        checkstr[s] = 1
                    else:
                        checkstr[s] += 1
                        if checkstr[s] == 10:
                            commonstr.append(s)
            # Write the output file
            if len(commonstr) > 0:
                out.write("!FILE:COMMON\n")
                for s in commonstr:
                    out.write(s + "=\n")
            for k, v in foundstr.items():
                first = True
                for s in v:
                    if s not in commonstr:
                        if first:
                            out.write("!FILE:" + k + "\n")
                            first = False
                        out.write(s + "=\n")
    common.logMessage("Done! Extracted", len(files), "files")
