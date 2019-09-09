import game
from hacktools import common, nds


def run():
    infile = "data/extract/arm9.bin"
    header = "data/extract/header.bin"
    outfile = "data/bin_output.txt"

    # Set the appropriate range depending on the game
    if nds.getHeaderID(header) == "YU5J2J":
        binrange = game.binrange[0]
    else:
        binrange = game.binrange[1]
        # Decompress binary
        decompfile = infile.replace(".bin", "_dec.bin")
        common.logMessage("Decompressing BIN ...")
        nds.decompressBinary(infile, decompfile)
        infile = decompfile

    common.logMessage("Extracting BIN to", outfile, "...")
    foundstrings = nds.extractBinaryStrings(infile, outfile, binrange, game.detectShiftJIS, "cp932")
    common.logMessage("Done! Extracted", len(foundstrings), "lines")
