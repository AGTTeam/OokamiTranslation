import os
import game
from hacktools import common, nds, nitro


def run():
    binin = "data/extract/arm9.bin"
    header = "data/extract/header.bin"
    binout = "data/repack/arm9.bin"
    binfile = "data/bin_input.txt"
    patchfile = ""
    if not os.path.isfile(binfile):
        common.logError("Input file", binfile, "not found")
        return

    # Set the appropriate range depending on the game
    if nds.getHeaderID(header) == "YU5J2J":
        binrange = game.binrange[0]
        patchfile = "bin_patch.asm"
        fontfile = "data/replace/data/font/lcfont12.NFTR"
        injectfile = "data/extract/data/font/digit8.NFTR"
    else:
        binrange = game.binrange[1]
        binin = binin.replace(".bin", "_dec.bin")
        binout = binout.replace(".bin", "_dec.bin")

    nds.repackBIN(binrange, None, game.detectShiftJIS, game.writeBINShiftJIS, "cp932", "#", binin, binout)
    if patchfile != "":
        if not os.path.isfile(fontfile):
            fontfile = fontfile.replace("replace/", "extract/")
        common.copyFile(injectfile, injectfile.replace("extract/", "repack/"))
        nitro.extractFontData(fontfile, "data/font_data.bin")
        common.armipsPatch(patchfile)
    if nds.getHeaderID(header) != "YU5J2J":
        compfile = binout.replace("_dec.bin", ".bin")
        common.logMessage("Compressing BIN ...")
        nds.compressBinary(binout, compfile)
