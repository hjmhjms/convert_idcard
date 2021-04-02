::%~dp0
cd %~dp0
set ROOT_DIR=%~dp0

pyinstaller -F  src/convert_idcard.py


copy %BIN_DIR%src\config.json %BIN_DIR%dist\config.json
copy %BIN_DIR%src\order_white_list.xlsx %BIN_DIR%dist\order_white_list.xlsx
copy %BIN_DIR%src\readme.txt %BIN_DIR%dist\readme.txt


