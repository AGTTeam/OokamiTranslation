import codecs
import os
import game
from hacktools import common, nds, nitro


def run(firstgame):
    binin = "data/extract/arm9.bin"
    binout = "data/repack/arm9.bin"
    binfile = "data/bin_input.txt"
    patchfile = ""
    if not os.path.isfile(binfile):
        common.logError("Input file", binfile, "not found")
        return
    fixchars = game.getFixChars()

    patchfile = "bin_patch.asm"
    fontfile = "data/replace/data/font/lcfont12.NFTR"
    injectfile = "data/extract/data/font/digit8.NFTR"
    # Set the appropriate range depending on the game
    if firstgame:
        binrange = game.binrange[0]
        freeranges = game.freeranges[0]
        game.monthsection = game.monthsection[0]
        game.skipsection = game.skipsection[0]
    else:
        binrange = game.binrange[1]
        freeranges = game.freeranges[1]
        game.monthsection = game.monthsection[1]
        game.skipsection = game.skipsection[1]
        binin = binin.replace(".bin", "_dec.bin")
        binout = binout.replace(".bin", "_dec.bin")

    nds.repackBIN(binrange, freeranges, game.detectShiftJIS, game.writeBINShiftJIS, "cp932", "#", binin, binout, fixchars=fixchars)
    # Check that the redirects file is created, or create an empty one
    redfile = "data/redirects.asm"
    if not os.path.isfile(redfile):
        with codecs.open(redfile, "w", "utf-8") as f:
            f.write(".ascii \"NDSC\"\n\n")
            f.write("REDIRECT_START:\n\n")
    # Extract font data
    if not os.path.isfile(fontfile):
        fontfile = fontfile.replace("replace/", "extract/")
    common.copyFile(injectfile, injectfile.replace("extract/", "repack/"))
    nitro.extractFontData(fontfile, "data/font_data.bin")
    # Run armips
    common.armipsPatch(common.bundledFile(patchfile))
    # Compress the binary for the 2nd game
    if not firstgame:
        compfile = binout.replace("_dec.bin", ".bin")
        common.logMessage("Compressing BIN ...")
        nds.compressBinary(binout, compfile)
