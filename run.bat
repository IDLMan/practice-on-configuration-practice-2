@echo off
cd /d "%~dp0"
py -m src.main --config config\test.ini %*
