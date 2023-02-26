@echo off
taskkill /t /im machine.exe
taskkill /t /im logger.exe
taskkill /t /im dbmgr.exe
taskkill /t /im baseappmgr.exe
taskkill /t /im cellappmgr.exe
taskkill /t /im baseapp.exe
taskkill /t /im cellapp.exe
taskkill /t /im loginapp.exe
taskkill /t /im interfaces.exe
taskkill /t /im bots.exe
exit
