# Ookami Translation
This repository is for the tool used to translate the game. If you're looking for the English patch, click [here](http://www.romhacking.net/translations/5967/).  
## Setup
Install [Python 3](https://www.python.org/downloads/).  
Install [ImageMagick](https://imagemagick.org/script/download.php). For Windows, check "Add application directory to your system path" while installing.  
Download this repository by downloading and extracting it, or cloning it.  
Download [ndstool.exe](https://www.darkfader.net/ds/files/ndstool.exe) in the same folder.  
Copy the original Japanese rom into the same folder and rename it as `holo.nds`.  
For the second game, the rom should be called `holo2.nds`.  
Run `run_windows.bat` (for Windows) or `run_bash` (for OSX/Linux) to run the tool.  
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
## Run from command line
This is not recommended if you're not familiar with Python and the command line.  
After following the Setup section, run `pipenv sync` to install dependencies.  
Run `pipenv run python tool.py extract` to extract everything, and `pipenv run python tool.py repack` to repack.  
You can use switches like `pipenv run python tool.py repack --bin` to only repack certain parts to speed up the process.  
