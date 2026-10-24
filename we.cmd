@echo off
setlocal
set "ROOT=%~dp0"
set "JAVA=%ROOT%jdk-25.0.4.1+1-jre\bin\java.exe"
set "JAR=%ROOT%bin\worldedit-cli-7.4.7-SNAPSHOT-dist.jar"
set "LOG4J=%ROOT%bin\log4j2.xml"

if "%~1"=="" goto usage
set "FILE=%~f1"
if not exist "%FILE%" (
    echo [error] schematic not found: %FILE%
    exit /b 1
)

python "%ROOT%tools\ensure_data.py" "%FILE%"
if errorlevel 1 exit /b 1

if "%~2"=="" goto interactive
set "SCRIPT=%~f2"
if not exist "%SCRIPT%" (
    echo [error] command script not found: %SCRIPT%
    exit /b 1
)
goto run

:interactive
set "SCRIPT="

:run
pushd "%ROOT%"
if defined SCRIPT (
    "%JAVA%" "-Dlog4j.configurationFile=%LOG4J%" -jar "%JAR%" -f "%FILE%" -s "%SCRIPT%"
) else (
    "%JAVA%" "-Dlog4j.configurationFile=%LOG4J%" -jar "%JAR%" -f "%FILE%"
)
set "CODE=%ERRORLEVEL%"
popd
exit /b %CODE%

:usage
echo Usage: we.cmd ^<file.schem^> [commands.txt]
echo.
echo   Edits the schematic in place with WorldEdit commands.
echo   Without commands.txt, commands are read from the keyboard.
echo   Type "stop" to save and exit.
exit /b 1
