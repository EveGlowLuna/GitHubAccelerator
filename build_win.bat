pyinstaller --onefile --icon=github-mark.png --version-file=version_info.txt ^
--hidden-import=concurrent.futures ^
--hidden-import=ctypes.wintypes ^
--uac-admin ^
--clean ^
GitHubAccelerator.py