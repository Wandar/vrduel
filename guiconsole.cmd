@echo off
set curpath=%cd%

cd ..
set KBE_ROOT=%cd%
set KBE_RES_PATH=%KBE_ROOT%/kbe/res/;%curpath%/;%curpath%/scripts/;%curpath%/res/
set KBE_BIN_PATH=%KBE_ROOT%/kbe/bin/server/

set uid=10000

cd %KBE_ROOT%/kbe/tools/server/guiconsole/
taskkill /f /t /im guiconsole.exe
start guiconsole.exe
exit