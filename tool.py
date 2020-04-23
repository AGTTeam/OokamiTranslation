import os
import click
import game
from hacktools import common, nds, nitro

version = "1.0.0"
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
        nds.extractRom(romfile, infolder, outfolder)
    if all or bin:
        import extract_bin
        extract_bin.run()
    if all or dat:
        import extract_dat
        extract_dat.run()
    if all or wsb:
        import extract_wsb
        extract_wsb.run(analyze)
    if all or img:
        ncgrfolder = "data/extract/data/graphic/"
        if not os.path.isdir(ncgrfolder):
            ncgrfolder = "data/extract/data/graphics/"
        nitro.extractIMG(ncgrfolder, "data/out_IMG/", ".NCGR", game.readImage)


@common.cli.command()
@click.option("--no-rom", is_flag=True, default=False)
@click.option("--bin", is_flag=True, default=False)
@click.option("--dat", is_flag=True, default=False)
@click.option("--img", is_flag=True, default=False)
@click.option("--wsb", is_flag=True, default=False)
def repack(no_rom, bin, dat, img, wsb):
    all = not bin and not dat and not img and not wsb
    if all or bin:
        import repack_bin
        repack_bin.run()
    if all or dat:
        import repack_dat
        repack_dat.run()
    if all or wsb:
        import repack_wsb
        repack_wsb.run()
    if all or img:
        ncgrfolder = "data/repack/data/graphic/"
        if not os.path.isdir(ncgrfolder):
            ncgrfolder = "data/repack/data/graphics/"
        ncgrfolderin = ncgrfolder.replace("repack", "extract")
        common.copyFolder(ncgrfolderin, ncgrfolder)
        nitro.repackIMG("data/work_IMG/", ncgrfolderin, ncgrfolder, ".NCGR", game.readImage)

    if not no_rom:
        if os.path.isdir(replacefolder):
            common.mergeFolder(replacefolder, outfolder)
        subtitle = "My Year With Holo" if nds.getHeaderID(headerfile) == "YU5J2J" else "The Wind that Spans the Sea"
        nds.editBannerTitle(bannerfile, "Spice & Wolf\n" + subtitle + "\nASCII MEDIA WORKS")
        nds.repackRom(romfile, rompatch, outfolder, patchfile)


if __name__ == "__main__":
    click.echo("OokamiTranslation version " + version)
    if not os.path.isdir("data"):
        common.logError("data folder not found.")
        quit()
    common.cli()
