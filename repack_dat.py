import codecs
import os
import game
from hacktools import common


def run():
    infolder = "data/extract/data/data/"
    outfolder = "data/repack/data/data/"
    infile = "data/dat_input.txt"
    if not os.path.isfile(infile):
        common.logError("Input file", infile, "not found")
        return
    common.makeFolder(outfolder)
    chartot = transtot = 0

    common.logMessage("Repacking DAT from", infile, "...")
    with codecs.open(infile, "r", "utf-8") as dat:
        files = common.getFiles(infolder, ".dat")
        for file in common.showProgress(files):
            section = common.getSection(dat, file)
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
                        check = game.detectShiftJIS(fin)
                        if check != "":
                            # Found a SJIS string, check if we have to replace it
                            if check in section and section[check][0] != "":
                                common.logDebug("Replacing string at", pos)
                                f.seek(pos)
                                game.writeShiftJIS(f, section[check][0], False, True)
                                # Pad with 0s if the line is shorter
                                while f.tell() < fin.tell():
                                    f.writeByte(0x00)
                            pos = fin.tell() - 1
                        fin.seek(pos + 1)
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))
