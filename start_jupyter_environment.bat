::@echo off
set CONDAPATH=C:\ProgramData\Anaconda3
cd /d "C:\Users\Queen's University\Desktop\Detector"
call %CONDAPATH%\Scripts\activate.bat test_env 
::%CONDAPATH% 
::call conda activate test_env
jupyter notebook
pause