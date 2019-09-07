import os
from hacktools import common, nitro


def run():
    infolder = "data/extract/data/graphic/"
    if not os.path.isdir(infolder):
        infolder = "data/extract/data/graphics/"
    outfolder = "data/out_NCGR/"
    common.makeFolder(outfolder)

    common.logMessage("Extracting NCGR to", outfolder, "...")
    files = common.getFiles(infolder, ".NCGR")
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        palettefile = infolder + file.replace(".NCGR", ".NCLR")
        mapfile = infolder + file.replace(".NCGR", ".NSCR")
        cellfile = infolder + file.replace(".NCGR", ".NCER")
        # Fix palette name for shared palettes
        if file.startswith("goodsinstance/"):
            palettefile = infolder + "goodsinstance/goodsinstance.NCLR"
        # Read image
        palettes, ncgr, nscr, ncer, width, height = nitro.readNitroGraphic(palettefile, infolder + file, mapfile, cellfile)
        if ncgr is None:
            continue
        # Ignore map for this particular file
        if file == "cg/cg_shita.NCGR":
            nscr = None
            width = ncgr.width
            height = ncgr.height
        # Export img
        common.makeFolders(outfolder + os.path.dirname(file))
        outfile = outfolder + file.replace(".NCGR", ".png")
        if ncer is not None:
            nitro.drawNCER(outfile, ncer, ncgr, palettes, True, True)
        else:
            nitro.drawNCGR(outfile, nscr, ncgr, palettes, width, height)
    common.logMessage("Done! Extracted", len(files), "files")
