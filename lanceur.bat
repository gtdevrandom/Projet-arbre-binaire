@echo off
title Installateur et Lanceur de Tournoi
echo ===========================================
echo   Installation des dependances...
echo ===========================================
echo.

pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERREUR] Un probleme est survenu lors de l'installation.
    echo Verifiez que Python et pip sont bien installes et bloques dans le PATH.
    pause
    exit /b 1
)

echo.
echo ===========================================
echo   Lancement du tournoi...
echo ===========================================
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERREUR] Le script Python s'est arrete de maniere imprevue.
    pause
)

pause