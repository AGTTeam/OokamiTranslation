import os
import game
from hacktools import common, nitro


def run():
    infolder = "data/extract/data/graphics/"
    outfolder = "data/out_IMG/"

    common.logMessage("Extracting KBG to", outfolder, "...")
    files = common.getFiles(infolder, ".kbg")
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        with common.Stream(infolder + file, "rb") as f:
            palettes, ncgr = game.readKBG(f)
            tiledata = f.read(ncgr.tilelen)
            nitro.readNCGRTiles(ncgr, tiledata)
            # Export img
            common.makeFolders(outfolder + os.path.dirname(file))
            outfile = outfolder + file.replace(".kbg", ".png")
            nitro.drawNCGR(outfile, None, ncgr, palettes, ncgr.width, ncgr.height)
    common.logMessage("Done! Extracted", len(files), "files")
