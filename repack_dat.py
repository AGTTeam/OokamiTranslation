import codecs
import os
import game
from hacktools import common, nitro


def run(firstgame):
    infolder = "data/extract/data/data/"
    outfolder = "data/repack/data/data/"
    infile = "data/dat_input.txt"
    fontfile = "data/replace/data/font/lcfont12.NFTR"
    if not os.path.isfile(infile):
        common.logError("Input file", infile, "not found")
        return
    common.makeFolder(outfolder)
    chartot = transtot = 0

    encoding = "shift_jis" if firstgame else "shift_jisx0213"
    common.logMessage("Repacking DAT from", infile, "...")
    # Read the glyph size from the font
    if not os.path.isfile(fontfile):
        fontfile = fontfile.replace("replace/", "extract/")
    glyphs = nitro.readNFTR(fontfile).glyphs
    # Copy this txt file
    if not firstgame and os.path.isfile(infolder + "facilityhelp.txt"):
        common.copyFile(infolder + "facilityhelp.txt", outfolder + "facilityhelp.txt")
    with codecs.open(infile, "r", "utf-8") as dat:
        files = common.getFiles(infolder, ".dat")
        for file in common.showProgress(files):
            section = common.getSection(dat, file, fixchars=game.fixchars)
            # If there are no lines, just copy the file
            if len(section) == 0:
                common.copyFile(infolder + file, outfolder + file)
                continue
            chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
            common.logDebug("Processing", file, "...")
            size = os.path.getsize(infolder + file)
            with common.Stream(infolder + file, "rb") as fin:
                with common.Stream(outfolder + file, "wb") as f:
                    f.write(fin.read())
                    fin.seek(0)
                    # Loop the file and replace strings as needed
                    while fin.tell() < size - 2:
                        pos = fin.tell()
                        check = game.detectShiftJIS(fin, encoding)
                        if check != "":
                            # Found a SJIS string, check if we have to replace it
                            if check in section and section[check][0] != "":
                                common.logDebug("Replacing string at", pos)
                                f.seek(pos)
                                newsjis = section[check][0]
                                maxlen = 0
                                if file == "goods.dat":
                                    newsjis = common.wordwrap(newsjis, glyphs, 170)
                                elif file == "gossip.dat":
                                    newsjis = common.wordwrap(newsjis, glyphs, 190)
                                elif file == "entrance_icon.dat":
                                    maxlen = fin.tell() - pos
                                newlen = game.writeShiftJIS(f, newsjis, False, True, maxlen, encoding)
                                if newlen < 0:
                                    common.logError("String {} is too long ({}/{}).".format(newsjis, len(newsjis), maxlen))
                                # Pad with 0s if the line is shorter
                                while f.tell() < fin.tell():
                                    f.writeByte(0x00)
                            pos = fin.tell() - 1
                        fin.seek(pos + 1)
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))
