@echo off
setlocal

REM Pfad zum Hauptanwendungsordner im AppData\Roaming Verzeichnis
set "FULL_APP_FOLDER=%APPDATA%\USZ-RAO-App_old"

REM Name des Python-Skripts
set "PYTHON_SCRIPT=main.py"

REM --- Wichtig: In das Verzeichnis des Skripts wechseln ---
REM Dies stellt sicher, dass relative Pfade innerhalb von main.py korrekt funktionieren
cd /d "%FULL_APP_FOLDER%"
if errorlevel 1 (
    echo FEHLER: Konnte nicht in das Anwendungsverzeichnis wechseln:
    echo %FULL_APP_FOLDER%
    echo Bitte stellen Sie sicher, dass der Ordner USZ-RAO-App im Verzeichnis %APPDATA% existiert.
    pause
    exit /b 1
)

REM --- Python-Skript ohne wartendes CMD-Fenster starten ---
REM Der erste leere "" ist für den Fenstertitel, den START erwartet, wenn Pfade Anführungszeichen enthalten
REM Verwenden Sie pythonw.exe für GUI-Anwendungen, um das Konsolenfenster von Python selbst zu vermeiden
START "" /B pythonw.exe "%PYTHON_SCRIPT%"
REM Falls es eine reine Konsolenanwendung ist und Sie python.exe verwenden müssen:
REM START "" /B python.exe "%PYTHON_SCRIPT%"

endlocal
exit /b 0