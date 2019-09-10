import os
import click
from hacktools import common, nds

version = "0.9.2"
romfile = "data/rom.nds"
rompatch = "data/rom_patched.nds"
headerfile = "data/extract/header.bin"
bannerfile = "data/repack/banner.bin"
patchfile = "data/patch.xdelta"
infolder = "data/extract/"
outfolder = "data/repack/"


@common.cli.command()
@click.option("--rom", is_flag=True, default=False)
@click.option("--bin", is_flag=True, default=False)
@click.option("--dat", is_flag=True, default=False)
@click.option("--ncgr", is_flag=True, default=False)
@click.option("--wsb", is_flag=True, default=False)
@click.option("--analyze", default="")
def extract(rom, bin, dat, ncgr, wsb, analyze):
    all = not rom and not bin and not dat and not ncgr and not wsb
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
    if all or ncgr:
        import extract_ncgr
        extract_ncgr.run()


@common.cli.command()
@click.option("--no-rom", is_flag=True, default=False)
@click.option("--bin", is_flag=True, default=False)
@click.option("--dat", is_flag=True, default=False)
@click.option("--ncgr", is_flag=True, default=False)
@click.option("--wsb", is_flag=True, default=False)
def repack(no_rom, bin, dat, ncgr, wsb):
    all = not bin and not dat and not ncgr and not wsb
    if all or bin:
        import repack_bin
        repack_bin.run()
    if all or dat:
        import repack_dat
        repack_dat.run()
    if all or wsb:
        import repack_wsb
        repack_wsb.run()
    if all or ncgr:
        import repack_ncgr
        repack_ncgr.run()

    if not no_rom:
        subtitle = "My Year With Holo" if nds.getHeaderID(headerfile) == "YU5J2J" else "The Wind that Spans the Sea"
        nds.editBannerTitle(bannerfile, "Spice & Wolf\n" + subtitle + "\nASCII MEDIA WORKS")
        nds.repackRom(romfile, rompatch, outfolder, patchfile)


if __name__ == "__main__":
    click.echo("OokamiTranslation version " + version)
    if not os.path.isdir("data"):
        common.logError("data folder not found.")
        quit()
    common.cli()
