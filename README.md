# Ookami Translation
This repository is for the tool used to translate the game. If you're looking for the English patch, click [here](http://www.romhacking.net/translations/5967/).
## Setup
Create a "data" folder and copy the rom as "holo.nds" in it.
For the second game, the rom should be called "holo2.nds".
## Run from binary
Download the latest [release](https://github.com/Illidanz/OokamiTranslation/releases) outside the data folder.
Run `tool extract` to extract everything and `tool repack` to repack after editing.
Run `tool extract --help` or `tool repack --help` for more info.
## Run from source
Install [Python 3.8](https://www.python.org/downloads/) and pipenv.
Download [ndstool.exe](https://www.darkfader.net/ds/files/ndstool.exe).
Download [armips.exe](https://github.com/Kingcom/armips/releases).
Download xdelta.exe.
Run `pipenv sync`.
Run the tool with `pipenv run tool.py` or build with `pipenv run pyinstaller tool.spec`.
## Text Editing
Rename the \*\_output.txt files to \*\_input.txt (bin_output.txt to bin_input.txt, etc) and add translations for each line after the `=` sign.
The text in wsb_input is automatically wordwrapped, but a `|` can be used to force a line break.
New textboxes can be added by appending `>>` followed by the new text.
Lines can be automatically centered by putting a `<<` at the beginning of the line.
Control codes are specified as `<XX>` or `UNK(XXXX)`, they should usually be kept.
To blank out a line, use a single `!`. If just left empty, the line will be left untranslated.
Comments can be added at the end of lines by using `#`
A `fontconfig.txt` file in the data folder can be used to define a list of characters and their replacement, separated by `=`, that will be replaced when writing strings.
## Image Editing
Rename the out\_\* folders to work\_\* (out_IMG to work_IMG, etc).
Edit the images in the work folder(s). The palette on the right should be followed but the repacker will try to approximate other colors to the closest one.
If an image doesn't require repacking, it should be deleted from the work folder.
## Scripts Testing
A script can be forced by replacing the new game script using the force parameter while repacking, for example: `--force event/ev_act/test_script2`
