# Ookami Translation
## Setup
Create a "data" folder and copy the rom as "rom.nds" in it.  
## Run from binary
Download the latest [release](https://github.com/Illidanz/OokamiTranslation/releases) outside the data folder.  
Run "tool extract" to extract everything and "tool repack" to repack after editing.  
Run "tool extract --help" or "tool repack --help" for more info.  
## Run from source
Install [Python 3.7](https://www.python.org/downloads/), pip and virtualenv.  
Download [ndstool.exe](https://www.darkfader.net/ds/files/ndstool.exe).  
Download xdelta.exe.  
Pull [hacktools](https://github.com/Illidanz/hacktools) in the parent folder.  
```
virtualenv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -e ../hacktools
```
Run tool.py or build with build.bat  
## Text Editing
Rename the \*\_output.txt files to \*\_input.txt (bin_output.txt to bin_input.txt, etc) and add translations for each line after the "=" sign.  
The text in wsb_input is automatically wordwrapped, but a "|" can be used to force a line break.  
New textboxes can be added by appending ">>" followed by the new text.  
Control codes are specified as \<XX\> or UNK(XXXX), they should usually be kept. Line breaks are specified as "|" or "<0A>" depending on the file.  
To blank out a line, use a single "!". If just left empty, the line will be left untranslated.  
Comments can be added at the end of lines by using #  
## Image Editing
Rename the out\_\* folders to work\_\* (out_NCGR to work_NCGR, etc).  
Edit the images in the work folder(s). The palette on the right should be followed but the repacker will try to approximate other colors to the closest one.  
If an image doesn't require repacking, it should be deleted from the work folder.  
