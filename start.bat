cd %~dp0

set PYTHONPATH=%~dp0src;%PYTHONPATH%


python %~dp0src/main.py
pause
