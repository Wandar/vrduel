@echo off
set curpath=%cd%
cd ..
set KBE_ROOT=%cd%
set KBE_RES_PATH=%KBE_ROOT%/kbe/res/;%curpath%/;%curpath%/scripts/;%curpath%/res/;
set KBE_BIN_PATH=%KBE_ROOT%/kbe/bin/server/
set uid=10000

cd %curpath%

echo KBE_ROOT = %KBE_ROOT%
echo KBE_RES_PATH = %KBE_RES_PATH%
echo KBE_BIN_PATH = %KBE_BIN_PATH%
echo UID=%uid


SET status=1
(TASKLIST|FIND /I "loginapp.exe"||SET status=0) 2>nul 1>nul
IF %status% EQU 1 (
	@echo off
	taskkill /t /im dbmgr.exe
    taskkill /t /im baseappmgr.exe
    taskkill /t /im cellappmgr.exe
    taskkill /t /im baseapp.exe
    taskkill /t /im cellapp.exe
    taskkill /t /im loginapp.exe
    taskkill /t /im interfaces.exe
    taskkill /t /im bots.exe
)

if "%1"=="1" (
  set HIDE=0
) else (
  set HIDE=1
)


SET hasmachine=1
(TASKLIST|FIND /I "machine.exe"||SET hasmachine=0) 2>nul 1>nul
IF %hasmachine% EQU 0 (
	@echo off
	copy .\res\server\email_serviceOrigin.xml .\res\server\email_service.xml
	copy .\res\server\kbengineOrigin.xml .\res\server\kbengine.xml
	start %KBE_BIN_PATH%/logger.exe --cid=1000 --gus=100 --hide=0
	start %KBE_BIN_PATH%/machine.exe --cid=2000 --gus=200 --hide=0
)
start %KBE_BIN_PATH%/interfaces.exe --cid=3000 --gus=300 --hide=%HIDE%
start %KBE_BIN_PATH%/dbmgr.exe --cid=4000 --gus=400 --hide=%HIDE%
start %KBE_BIN_PATH%/baseappmgr.exe --cid=5000 --gus=500 --hide=%HIDE%
start %KBE_BIN_PATH%/cellappmgr.exe --cid=6000 --gus=600 --hide=%HIDE%
start %KBE_BIN_PATH%/baseapp.exe --cid=1 --gus=2 --hide=0
start %KBE_BIN_PATH%/cellapp.exe --cid=8000 --gus=800 --hide=0
start %KBE_BIN_PATH%/loginapp.exe --cid=9000 --gus=900 --hide=%HIDE%


set multiopen=0
IF %multiopen% EQU 1 (
start %KBE_BIN_PATH%/baseapp.exe --cid=7000 --gus=700 --hide=0
start %KBE_BIN_PATH%/baseapp.exe --cid=7001 --gus=701 --hide=0
start %KBE_BIN_PATH%/baseapp.exe --cid=7002 --gus=702 --hide=0
start %KBE_BIN_PATH%/cellapp.exe --cid=8002  --gus=802 --hide=0
start %KBE_BIN_PATH%/cellapp.exe --cid=8003  --gus=803 --hide=0
start %KBE_BIN_PATH%/cellapp.exe --cid=8004  --gus=804 --hide=0
)


SET hasguiconsole=1
(TASKLIST|FIND /I "guiconsole.exe"||SET hasguiconsole=0) 2>nul 1>nul
IF %hasguiconsole% EQU 0 (
	@echo off
	start %KBE_ROOT%/kbe/tools/server/guiconsole/guiconsole.exe
)

exit