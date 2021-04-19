::%~dp0
cd %~dp0
set ROOT_DIR=%~dp0

pyinstaller -F  src/main_yunji.py
::pyinstaller   src/main.py -w



echo f | xcopy  /f /y  ".\src\http_proxy.py" ".\dist\src\http_proxy.py"
copy /y "./order_list.xlsx" "./dist/order_list.xlsx"
copy /y "./config.json" "./dist/config.json"
xcopy  /e /y /i  "tools" "./dist/tools"
copy /y "./readme.txt" "./dist/readme.txt"

pause
