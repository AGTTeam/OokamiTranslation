import codecs
import os
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
        print("Decompressing BIN ...")
        nds.decompressBinary(infile, decompfile)
        infile = decompfile

    common.logMessage("Extracting BIN to", outfile, "...")
    with codecs.open(outfile, "w", "utf-8") as out:
        foundstrings = []
        insize = os.path.getsize(infile)
        with common.Stream(infile, "rb") as f:
            # Skip the beginning and end of the file to avoid false-positives
            f.seek(binrange[0])
            while f.tell() < binrange[1] and f.tell() < insize - 2:
                pos = f.tell()
                check = game.detectShiftJIS(f, "cp932")
                if check != "":
                    if check not in foundstrings:
                        common.logDebug("Found string at", pos)
                        foundstrings.append(check)
                        out.write(check + "=\n")
                    pos = f.tell() - 1
                f.seek(pos + 1)
    common.logMessage("Done! Extracted", len(foundstrings), "lines")
