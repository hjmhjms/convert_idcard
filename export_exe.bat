::%~dp0
cd %~dp0
set ROOT_DIR=%~dp0

pyinstaller -F src/convert_idcard.py


copy %BIN_DIR%src\config.json %BIN_DIR%dist\config.json
copy %BIN_DIR%src\订单白名单.xlsx %BIN_DIR%dist\订单白名单.xlsx
copy %BIN_DIR%src\使用说明.txt %BIN_DIR%dist\使用说明.txt


