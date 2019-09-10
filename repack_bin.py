import codecs
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

    section = {}
    with codecs.open(binfile, "r", "utf-8") as bin:
        section = common.getSection(bin, "")
    chartot, transtot = common.getSectionPercentage(section)

    # Set the appropriate range depending on the game
    if nds.getHeaderID(header) == "YU5J2J":
        binrange = game.binrange[0]
    else:
        binrange = game.binrange[1]
        # Decompress binary
        decompfile = binin.replace("arm9.bin", "arm9_dec.bin")
        common.logMessage("Decompressing BIN ...")
        nds.decompressBinary(binin, decompfile)
        binin = decompfile
        binout = binout.replace(".bin", "_dec.bin")

    common.copyFile(binin, binout)
    common.logMessage("Repacking BIN from", binfile, "...")
    with common.Stream(binin, "rb") as fi:
        with common.Stream(binout, "r+b") as fo:
            # Skip the beginning and end of the file to avoid false-positives
            fi.seek(binrange[0])
            while fi.tell() < binrange[1]:
                pos = fi.tell()
                check = game.detectShiftJIS(fi, "cp932")
                if check in section and section[check][0] != "":
                    common.logDebug("Replacing string at", pos)
                    fo.seek(pos)
                    endpos = fi.tell() - 1
                    newlen = game.writeShiftJIS(fo, section[check][0], False, True, endpos - pos + 1, "cp932")
                    if newlen < 0:
                        fo.writeZero(1)
                        common.logError("String", section[check][0], "is too long.")
                    else:
                        fo.writeZero(endpos - fo.tell())
                fi.seek(pos + 1)
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))
    if nds.getHeaderID(header) != "YU5J2J":
        compfile = binout.replace("_dec.bin", ".bin")
        common.logMessage("Compressing BIN ...")
        nds.compressBinary(binout, compfile)
