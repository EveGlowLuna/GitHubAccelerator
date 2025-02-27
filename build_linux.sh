pyinstaller --onefile \
--add-data="*.json:." \
--hidden-import=concurrent.futures \
--clean \
GitHubAccelerator.py -n GitHubAccelerator