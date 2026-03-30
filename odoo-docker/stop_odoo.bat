@echo off
echo Stopping Odoo containers...
cd /d "%~dp0odoo-docker"
docker-compose down
echo.
echo Odoo stopped successfully!
echo.
pause
