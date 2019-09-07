import os
import codecs
import game
from hacktools import common


def run():
    infolder = "data/extract/data/data/"
    outfile = "data/dat_output.txt"
    ignorefiles = ["route.dat", "debttable.dat", "errandgossip.dat", "market.dat", "traderexptable.dat"]

    common.logMessage("Extracting DAT to", outfile, "...")
    with codecs.open(outfile, "w", "utf-8") as out:
        files = common.getFiles(infolder, ".dat")
        for file in common.showProgress(files):
            if file in ignorefiles:
                continue
            common.logDebug("Processing", file, "...")
            first = True
            foundstrings = []
            size = os.path.getsize(infolder + file)
            # The file contains several strings, padded with 0s
            with common.Stream(infolder + file, "rb") as f:
                while f.tell() < size - 2:
                    pos = f.tell()
                    check = game.detectShiftJIS(f)
                    if check != "":
                        # Check for repeated strings, only within a single file
                        if check not in foundstrings:
                            common.logDebug("Found string at", pos)
                            if first:
                                out.write("!FILE:" + file + "\n")
                                first = False
                            out.write(check + "=\n")
                            foundstrings.append(check)
                        pos = f.tell() - 1
                    f.seek(pos + 1)
    common.logMessage("Done! Extracted", len(files), "files")
