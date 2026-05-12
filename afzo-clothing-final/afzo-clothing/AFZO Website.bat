@echo off
cd /d "C:\Users\Afreen\Downloads\afzo-clothing-final\afzo-clothing"
cls
echo.
echo ============================================
echo        AFZO CLOTHING WEBSITE
echo ============================================
echo.
echo Starting server... Please wait...
echo.
start /B python app.py >nul 2>&1
timeout /t 3 /nobreak >nul
start http://127.0.0.1:5000
echo.
echo ============================================
echo Server started! Website opened in browser.
echo Press any key to close server
echo ============================================
pause >nul