@echo off

set /p folder="enter project folder > "

cd %folder%

mkdir user

copy *.py user

..\7za a ..\robot.zip user

rmdir user /S /Q