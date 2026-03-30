@echo off
echo Starting Odoo containers...
cd /d "%~dp0odoo-docker"
docker-compose up -d
echo.
echo Waiting for Odoo to start (30 seconds)...
timeout /t 30 /nobreak >nul
echo.
echo Odoo started successfully!
echo Open: http://localhost:8069
echo.
pause
