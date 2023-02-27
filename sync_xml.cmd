@echo off
set curpath=%cd%
cd ..
set KBE_ROOT=%cd%
set KBE_RES_PATH=%KBE_ROOT%/kbe/res/;%curpath%/;%curpath%/scripts/;%curpath%/res/;
set KBE_BIN_PATH=%KBE_ROOT%/kbe/bin/server/
set uid=10000

cd %curpath%

set clientpath=0

for /f %%i in (clientPath.txt) do set clientpath=%%i

IF %clientpath% EQU 0 (
	echo "no client path"
	pause
)

python cmd/genXml.py


echo clientPath=%clientpath%\Assets\Plugins\client_plugins
start %KBE_BIN_PATH%/kbcmd --clientsdk=unity --outpath=%clientpath%\Assets\Scripts\client_plugins