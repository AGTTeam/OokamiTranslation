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
    subfile = "data/repack/data/data/opsub.dat"
    fontfile = "data/replace/data/font/lcfont12.NFTR"
    if firstgame:
        palfile = "data/extract/data/graphic/title/logo.NCLR"
        bgcolor = "#F8F8F8"
    else:
        palfile = "data/extract/data/graphics/systemmenu/BottomBG.NCLR"
        bgcolor = "transparent"

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
    img = ndstextgen.gen(fontfile, text, out="", vert=5, color="#480818", bg=bgcolor, no_crop=True, center=True, height=sublen * 16)
    # Read the palette and create some dummy ncgr data
    palette = nitro.readNCLR(palfile)[0]
    ncgr = nitro.NCGR()
    ncgr.bpp = 8
    ncgr.tilesize = 8
    ncgr.width = 256
    ncgr.height = 16
    clearoffsets = []
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
                clearoffsets.append(f.tell())
                f.writeUInt(0)
        # Write a 0 for the subtitles end
        f.writeUInt(0)
        # Write the clear tile
        clearoffset = f.tell()
        f.writeUShort(0x1)
        f.writeUShort(0x40)
        pixels = img.crop((0, 0, 8, 8)).load()
        nitro.writeNCGRTile(f, pixels, 8, ncgr, 0, 0, palette)
        f.writeUInt(0)
        # Write the other tiles
        for i in range(sublen):
            # Write the tile offset
            currentoff = f.tell()
            f.seek(subdata[i]["pos"])
            f.writeUInt(currentoff)
            f.seek(currentoff)
            with common.Stream() as memf:
                # Crop the line from the image and write the data in memory
                line = img.crop((0, i * ncgr.height, ncgr.width, i * ncgr.height + ncgr.height))
                pixels = line.load()
                for i in range(ncgr.height // ncgr.tilesize):
                    for j in range(ncgr.width // ncgr.tilesize):
                        nitro.writeNCGRTile(memf, pixels, ncgr.width, ncgr, i, j, palette)
                # Write the first tile and loop all the rest with a simple compression
                tilenum = (ncgr.height // ncgr.tilesize) * (ncgr.width // ncgr.tilesize)
                memf.seek(0)
                cmppos = f.tell()
                f.writeUInt(0)
                cmpbyte = 0
                cmprep = True
                lasttile = None
                for i in range(tilenum):
                    tile = memf.read(0x40)
                    if tile != lasttile:
                        if cmpbyte == 0:
                            # First tile, just write it
                            f.write(tile)
                            cmpbyte += 1
                        elif cmprep:
                            # Different tile, start a new series
                            f.writeUShortAt(cmppos, 1)
                            f.writeUShortAt(cmppos + 2, cmpbyte)
                            cmppos = f.tell()
                            f.writeUInt(0)
                            cmprep = memf.peek(0x40) == tile
                            cmpbyte = 1
                            f.write(tile)
                        else:
                            # Already doing a non-repeating series, increase the counter and write it
                            cmpbyte += 1
                            f.write(tile)
                        lasttile = tile
                    elif cmprep:
                        # Already doing a repeating series, just increase the counter
                        cmpbyte += 1
                    else:
                        # Go back and start a new repeating series
                        f.writeUShortAt(cmppos + 2, cmpbyte - 1)
                        f.seek(-0x40, 1)
                        cmppos = f.tell()
                        f.writeUInt(0)
                        f.write(tile)
                        cmpbyte = 2
                        cmprep = True
                # Write the last cmpbyte and a 0
                f.writeUShortAt(cmppos, (1 if cmprep else 0))
                f.writeUShortAt(cmppos + 2, cmpbyte)
                f.writeUInt(0)
        # Write the clear offsets
        for offset in clearoffsets:
            f.seek(offset)
            f.writeUInt(clearoffset)
    common.logMessage("Done!")
