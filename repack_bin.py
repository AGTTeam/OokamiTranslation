import os
import game
from hacktools import common, nds


def run():
    binin = "data/extract/arm9.bin"
    header = "data/extract/header.bin"
    binout = "data/repack/arm9.bin"
    binfile = "data/bin_input.txt"
    if not os.path.isfile(binfile):
        common.logError("Input file", binfile, "not found")
        return

    # Set the appropriate range depending on the game
    if nds.getHeaderID(header) == "YU5J2J":
        binrange = game.binrange[0]
    else:
        binrange = game.binrange[1]
        binin = binin.replace(".bin", "_dec.bin")
        binout = binout.replace(".bin", "_dec.bin")

    nds.repackBIN(binrange, game.detectShiftJIS, game.writeBINShiftJIS, "cp932", binin, binout)
    if nds.getHeaderID(header) != "YU5J2J":
        compfile = binout.replace("_dec.bin", ".bin")
        common.logMessage("Compressing BIN ...")
        nds.compressBinary(binout, compfile)
