import os
import click
import game
from hacktools import common, nds, nitro

version = "1.9.0"
romfile = "holo.nds"
rompatch = "data/holo_patched.nds"
headerfile = "data/extract/header.bin"
bannerfile = "data/repack/banner.bin"
patchfile = "data/patch.xdelta"
infolder = "data/extract/"
replacefolder = "data/replace/"
outfolder = "data/repack/"


@common.cli.command()
@click.option("--rom", is_flag=True, default=False)
@click.option("--bin", is_flag=True, default=False)
@click.option("--dat", is_flag=True, default=False)
@click.option("--img", is_flag=True, default=False)
@click.option("--wsb", is_flag=True, default=False)
@click.option("--analyze", default="", hidden=True)
def extract(rom, bin, dat, img, wsb, analyze):
    all = not rom and not bin and not dat and not img and not wsb
    if all or rom:
        nds.extractRom(romfile if os.path.isfile(romfile) else romfile.replace("holo", "holo2"), infolder, outfolder)
    firstgame = nds.getHeaderID(headerfile) == "YU5J2J"
    if all or bin:
        import extract_bin
        extract_bin.run(firstgame)
    if all or dat:
        import extract_dat
        extract_dat.run(firstgame)
    if all or wsb:
        import extract_wsb
        extract_wsb.run(firstgame, analyze)
    if all or img:
        ncgrfolder = "data/extract/data/graphic/" if firstgame else "data/extract/data/graphics/"
        nitro.extractIMG(ncgrfolder, "data/out_IMG/", ".NCGR", game.readImage)
        if not firstgame:
            import extract_kbg
            extract_kbg.run()


@common.cli.command()
@click.option("--no-rom", is_flag=True, default=False, hidden=True)
@click.option("--dat", is_flag=True, default=False)
@click.option("--bin", is_flag=True, default=False)
@click.option("--img", is_flag=True, default=False)
@click.option("--wsb", is_flag=True, default=False)
@click.option("--sub", is_flag=True, default=False)
@click.option("--no-redirect", is_flag=True, default=False, hidden=True)
@click.option("--force", default="", hidden=True)
def repack(no_rom, dat, bin, img, wsb, sub, no_redirect, force):
    all = not sub and not dat and not bin and not img and not wsb
    firstgame = nds.getHeaderID(headerfile) == "YU5J2J"
    if all or dat:
        import repack_dat
        repack_dat.run(firstgame, no_redirect)
    if all or dat or bin:
        import repack_bin
        repack_bin.run(firstgame)
    if all or wsb:
        import repack_wsb
        repack_wsb.run(firstgame)
    if all or dat or sub:
        import repack_sub
        repack_sub.run(firstgame)
    if all or img:
        ncgrfolder = "data/repack/data/graphic/" if firstgame else "data/repack/data/graphics/"
        ncgrfolderin = ncgrfolder.replace("repack", "extract")
        common.copyFolder(ncgrfolderin, ncgrfolder)
        nitro.repackIMG("data/work_IMG/", ncgrfolderin, ncgrfolder, ".NCGR", game.readImage)
        if not firstgame:
            import repack_kbg
            repack_kbg.run()
            # Part of the AP patch
            with common.Stream(ncgrfolder + "doubleinfo/SDLawrence_01.NCGR", "rb+") as f:
                f.seek(0x26f1)
                f.writeByte(0x17)

    if not no_rom:
        if os.path.isdir(replacefolder):
            common.mergeFolder(replacefolder, outfolder)
        if force != "":
            if not force.endswith(".wsb"):
                force += ".wsb"
            if firstgame:
                common.copyFile(outfolder + "data/script/" + force, outfolder + "data/script/event/ev_act/act_010_opening.wsb")
            else:
                common.copyFile(outfolder + "data/script/" + force, outfolder + "data/script/event/ev_main/main_010_prologue.wsb")
        subtitle = "My Year with Holo" if firstgame else "The Wind that Spans the Sea"
        nds.editBannerTitle(bannerfile, "Spice & Wolf\n" + subtitle + "\nASCII MEDIA WORKS")
        romf = romfile if os.path.isfile(romfile) else romfile.replace("holo", "holo2")
        romp = rompatch if os.path.isfile(romfile) else rompatch.replace("holo", "holo2")
        # TODO: we still use ndstool to repack in order to not break the bin_patch INJECT_START behavior
        # nds.repackRom(romf, romp, outfolder, patchfile)
        common.logMessage("Repacking ROM", rompatch, "...")
        ndstool = common.bundledExecutable("ndstool.exe")
        if not os.path.isfile(ndstool):
            common.logError("ndstool not found")
            return
        common.execute(ndstool + " -c {rom} -9 {folder}arm9.bin -7 {folder}arm7.bin -y9 {folder}y9.bin -y7 {folder}y7.bin -t {folder}banner.bin -h {folder}header.bin -d {folder}data -y {folder}overlay".
                    format(rom=romp, folder=outfolder), False)
        common.logMessage("Done!")
        # Create xdelta patch
        if patchfile != "":
            common.xdeltaPatch(patchfile, romf, romp)


@common.cli.command(hidden=True)
def patchdump():
    patchfile = "data/bad_to_good.xdelta"
    ndsfile = romfile if os.path.isfile(romfile) else romfile.replace("holo", "holo2")
    common.xdeltaPatch(patchfile, ndsfile.replace(".nds", "_bad.nds"), ndsfile)


@common.cli.command(hidden=True)
def dupe():
    seen = {}
    sections = common.getSections("data/wsb_output.txt")
    for section in sections:
        for line in sections[section]:
            translation = sections[section][line][0]
            if line not in seen:
                seen[line] = [translation, section, 1]
            else:
                seen[line][2] += 1
                if translation != seen[line][0]:
                    common.logMessage("{}: {}={} ({} @{})".format(section, line, translation, seen[line][0], seen[line][1]))
    for line in seen:
        if seen[line][2] > 2:
            common.logMessage("Dupe", seen[line][2], line + "=")


if __name__ == "__main__":
    common.setupTool("OokamiTranslation", version, "data", romfile if os.path.isfile(romfile) else romfile.replace("holo", "holo2"))
