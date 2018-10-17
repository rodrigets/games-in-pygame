pip install -r ../requirements.txt
pip install -r ./requirements.txt
python build.py
xcopy ..\resources .\dist\resources /e /i /y /s
echo off
set /p DUMMY=Hit ENTER to continue...