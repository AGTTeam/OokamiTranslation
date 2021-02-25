import os
import game
from hacktools import common, nitro


def run():
    infolder = "data/extract/data/graphics/"
    outfolder = "data/repack/data/graphics/"
    workfolder = "data/work_IMG/"

    common.logMessage("Repacking KBG from", workfolder, "...")
    files = common.getFiles(infolder, ".kbg")
    for file in common.showProgress(files):
        pngfile = workfolder + file.replace(".kbg", ".png")
        if not os.path.isfile(pngfile):
            continue
        common.logDebug("Processing", file, "...")
        with common.Stream(infolder + file, "rb") as fin:
            with common.Stream(outfolder + file, "wb") as f:
                palettes, ncgr = game.readKBG(fin)
                fin.seek(0)
                f.write(fin.read(ncgr.tileoffset))
        nitro.writeNCGR(outfolder + file, ncgr, pngfile, palettes)
    common.logMessage("Done!")
