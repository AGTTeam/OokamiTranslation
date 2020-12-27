import os
import click
import game
from hacktools import common, nds, nitro

version = "1.4.6"
romfile = "data/holo.nds"
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
@click.option("--analyze", default="")
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


@common.cli.command()
@click.option("--no-rom", is_flag=True, default=False)
@click.option("--bin", is_flag=True, default=False)
@click.option("--dat", is_flag=True, default=False)
@click.option("--img", is_flag=True, default=False)
@click.option("--wsb", is_flag=True, default=False)
@click.option("--sub", is_flag=True, default=False)
@click.option("--force", default="")
def repack(no_rom, bin, dat, img, wsb, sub, force):
    all = not sub and not bin and not dat and not img and not wsb
    firstgame = nds.getHeaderID(headerfile) == "YU5J2J"
    if all or dat:
        import repack_dat
        repack_dat.run(firstgame)
    if all or bin:
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

    if not no_rom:
        if os.path.isdir(replacefolder):
            common.mergeFolder(replacefolder, outfolder)
        if force != "":
            if not force.endswith(".wsb"):
                force += ".wsb"
            common.copyFile(outfolder + "data/script/" + force, outfolder + "data/script/event/ev_act/act_010_opening.wsb")
        subtitle = "My Year with Holo" if firstgame else "The Wind that Spans the Sea"
        nds.editBannerTitle(bannerfile, "Spice & Wolf\n" + subtitle + "\nASCII MEDIA WORKS")
        romf = romfile if os.path.isfile(romfile) else romfile.replace("holo", "holo2")
        romp = rompatch if os.path.isfile(romfile) else rompatch.replace("holo", "holo2")
        nds.repackRom(romf, romp, outfolder, patchfile)


@common.cli.command()
def patchdump():
    patchfile = "data/bad_to_good.xdelta"
    ndsfile = romfile if os.path.isfile(romfile) else romfile.replace("holo", "holo2")
    common.xdeltaPatch(patchfile, ndsfile.replace(".nds", "_bad.nds"), ndsfile)


@common.cli.command()
def dupe():
    seen = {}
    sections = common.getSections("data/wsb_input.txt", fixchars=game.fixchars)
    for section in sections:
        for line in sections[section]:
            translation = sections[section][line][0]
            if line not in seen:
                seen[line] = (translation, section)
            elif translation != seen[line][0]:
                common.logMessage("{}: {}={} ({} @{})".format(section, line, translation, seen[line][0], seen[line][1]))


if __name__ == "__main__":
    click.echo("OokamiTranslation version " + version)
    if not os.path.isdir("data"):
        common.logError("data folder not found.")
        quit()
    common.cli()
