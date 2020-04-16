pipenv run pyinstaller --clean --icon=icon.ico --add-binary "ndstool.exe;." --add-binary "xdelta.exe;." --distpath . -F --hidden-import="pkg_resources.py2_warn" tool.py
