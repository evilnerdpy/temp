@echo off

call %~dp0venv\Scripts\activate

cd %~dp0bot_app

set PYTHONPATH=%PYTHONPATH%;%~dp0
set DATABASE_VERSION=1
python bot.py

pause