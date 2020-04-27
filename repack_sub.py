import codecs
import math
import os
import ass
import ndstextgen
from hacktools import common, nitro


def deltaToFrame(delta):
    return int((delta.seconds * 30) + math.ceil(delta.microseconds / (1000 * 1000 / 30)))


def run(firstgame):
    subin = "data/opening.ass"
    if firstgame:
        subfile = "data/repack/data/data/opsub.dat"
        fontfile = "data/replace/data/font/lcfont12.NFTR"
        palfile = "data/extract/data/graphic/title/logo.NCLR"

    if not os.path.isfile(subin):
        common.logError("Input file", subin, "not found")
        return

    if not os.path.isfile(fontfile):
        fontfile = fontfile.replace("/replace", "/extract")

    common.logMessage("Generating OP subs from", subin, "...")
    # Read the sub lines and timecodes
    subdata = []
    text = ""
    with codecs.open(subin, "r", "utf-8-sig") as f:
        doc = ass.parse(f)
    for event in doc.events:
        linestart = deltaToFrame(event.start)
        lineend = deltaToFrame(event.end)
        subdata.append({"start": linestart, "end": lineend, "pos": 0})
        text += event.text.strip() + "\n"
    text = text.strip()
    sublen = len(subdata)
    # Create the sub image
    img = ndstextgen.gen(fontfile, text, out="", vert=5, color="#480818", bg="#F8F8F8", no_crop=True, center=True, height=sublen * 16)
    # Read the palette and create some dummy ncgr data
    palette = nitro.readNCLR(palfile)[0]
    ncgr = nitro.NCGR()
    ncgr.bpp = 8
    ncgr.tilesize = 8
    ncgr.width = 256
    ncgr.height = 16
    with common.Stream(subfile, "wb") as f:
        # Offset of the first timecode
        f.writeUInt(4)
        # Write the timecodes
        for i in range(sublen):
            f.writeUInt(subdata[i]["start"])
            subdata[i]["pos"] = f.tell()
            # Make some room for the offset
            f.writeUInt(0)
            # Write a 0 offset for the last line or if there's a gap between lines to clear the screen
            if i == sublen - 1 or subdata[i+1]["start"] != subdata[i]["end"]:
                f.writeUInt(subdata[i]["end"])
                f.writeUInt(0)
        # Write a 0 for the subtitles end
        f.writeUInt(0)
        for i in range(sublen):
            # Write the tile offset
            currentoff = f.tell()
            f.seek(subdata[i]["pos"])
            f.writeUInt(currentoff)
            f.seek(currentoff)
            # Crop the line from the image
            line = img.crop((0, i * ncgr.height, ncgr.width, i * ncgr.height + ncgr.height))
            pixels = line.load()
            # Write the tile data
            for i in range(ncgr.height // ncgr.tilesize):
                for j in range(ncgr.width // ncgr.tilesize):
                    nitro.writeNCGRTile(f, pixels, 256, ncgr, i, j, palette)
    common.logMessage("Done!")
