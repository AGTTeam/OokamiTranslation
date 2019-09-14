import os
from hacktools import common, nitro


def run():
    workfolder = "data/work_NCGR/"
    infolder = "data/repack/data/graphic/"
    if not os.path.isdir(infolder):
        infolder = "data/repack/data/graphics/"
    common.copyFolder(infolder.replace("repack", "extract"), infolder)

    common.logMessage("Repacking NCGR from", infolder, "...")
    files = common.getFiles(infolder, ".NCGR")
    for file in common.showProgress(files):
        pngfile = file.replace(".NCGR", ".psd")
        if not os.path.isfile(workfolder + pngfile):
            pngfile = file.replace(".NCGR", ".png")
            if not os.path.isfile(workfolder + pngfile):
                continue
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
        # Import img
        if nscr is None and ncer is None:
            nitro.writeNCGR(infolder + file, ncgr, workfolder + pngfile, palettes, width, height)
        elif ncer is None:
            nitro.writeNSCR(infolder + file, ncgr, nscr, workfolder + pngfile, palettes, width, height)
        else:
            nitro.writeNCER(infolder + file, ncgr, ncer, workfolder + pngfile, palettes)
    common.logMessage("Done!")
