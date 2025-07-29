@echo off
setlocal enabledelayedexpansion
title Supermarket Management System - Complete Setup

echo.
echo ================================================
echo  SUPERMARKET MANAGEMENT SYSTEM - COMPLETE SETUP
echo ================================================
echo.
echo This script will automatically:
echo   - Check Python installation
echo   - Install required dependencies
echo   - Set up MySQL database
echo   - Create admin user account
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found

REM Check if MySQL is accessible
echo.
echo Checking MySQL availability...
mysql --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  MySQL command line tools not found in PATH
    echo MySQL server should still be accessible via Python
    echo.
) else (
    echo ✅ MySQL tools found
)

echo.
echo Starting automated setup...
echo.

REM Run the automated setup script
python automated_setup.py

if errorlevel 1 (
    echo.
    echo ❌ Setup failed! Please check the error messages above.
    echo.
    echo Common solutions:
    echo   - Make sure MySQL server is running
    echo   - Check your MySQL credentials
    echo   - Ensure you have proper permissions
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ✅ Setup completed successfully!
    echo.
    echo 🚀 You can now run the application with:
    echo    python main.py
    echo.
    echo 🔐 Use the login credentials shown above
    echo.
    pause
)

endlocal
