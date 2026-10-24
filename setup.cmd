@echo off
setlocal
cd /d "%~dp0"

set "JAR=bin\worldedit-cli-7.4.7-SNAPSHOT-dist.jar"
if exist "%JAR%" goto jar_done
echo [setup] downloading WorldEdit CLI...
curl.exe -L --retry 5 --retry-delay 5 --connect-timeout 30 --max-time 900 -o "%JAR%" "https://ci.enginehub.org/repository/download/bt10/30360:id/worldedit-cli-7.4.7-SNAPSHOT-dist.jar?branch=version/7.4.x&guest=1"
if errorlevel 1 (
    echo [setup] CLI download failed.
    exit /b 1
)
:jar_done

if exist "jdk-25.0.4.1+1-jre\bin\java.exe" goto jre_done
echo [setup] downloading Temurin JRE 25...
set "ZIP=%TEMP%\OpenJDK25U-jre.zip"
curl.exe -L --retry 5 --retry-delay 5 --connect-timeout 30 --max-time 900 -o "%ZIP%" "https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.4.1%%2B1/OpenJDK25U-jre_x64_windows_hotspot_25.0.4.1_1.zip"
if errorlevel 1 (
    echo [setup] JRE download failed.
    exit /b 1
)
powershell -NoProfile -Command "Expand-Archive -LiteralPath '%ZIP%' -DestinationPath '%~dp0' -Force"
if errorlevel 1 (
    echo [setup] JRE extract failed.
    exit /b 1
)
del "%ZIP%"
:jre_done

if exist "assets\client.jar" goto assets_done
echo [setup] downloading Minecraft assets...
python tools\fetch_assets.py
if errorlevel 1 echo [setup] asset download failed; run setup-assets.cmd later (fallback colors will be used)
:assets_done

echo [setup] ready. Run web.cmd
