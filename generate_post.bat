@echo off
chcp 65001 >nul
cls
echo ============================================================
echo    AI POST GENERATOR - NO TOKENS
echo ============================================================
echo.

cd /d C:\Users\AA\Desktop\gold_tier

REM Generate timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%"
set "DD=%dt:~6,2%" & set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%"
set "Sec=%dt:~12,2%"

set "timestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

REM Create posts folder
if not exist "posts" mkdir posts

REM Generate post based on time
set /a hour=%HH%
if %hour% LSS 12 set "greeting=Good Morning"
if %hour% GEQ 12 if %hour% LSS 17 set "greeting=Good Afternoon"
if %hour% GEQ 17 set "greeting=Good Evening"

REM Random post templates
set /a rand=%random% %% 10
if %rand%==0 set "post=Welcome to Gold Tier! Transforming businesses with innovative solutions."
if %rand%==1 set "post=Success is not final, failure is not fatal - it is the courage to continue."
if %rand%==2 set "post=Exciting updates coming soon! Stay tuned for amazing announcements."
if %rand%==3 set "post=Grateful for our amazing community! Thank you for your support."
if %rand%==4 set "post=Focus on your goals, stay dedicated, and watch yourself grow."
if %rand%==5 set "post=Innovation distinguishes between a leader and a follower."
if %rand%==6 set "post=Excellence is not a skill, it is an attitude."
if %rand%==7 set "post=Building relationships, creating opportunities."
if %rand%==8 set "post=Growth happens when we embrace challenges."
if %rand%==9 set "post=Your trusted partner in business excellence worldwide."

echo ============================================================
echo   GENERATED POST
echo ============================================================
echo.
echo %greeting%!
echo.
echo %post%
echo.
echo #GoldTier #Business #Success
echo ============================================================
echo.

REM Save to file
echo ============================================================ > posts\post_%timestamp%.txt
echo Generated: %YYYY%-%MM%-%DD% %HH%:%Min% >> posts\post_%timestamp%.txt
echo ============================================================ >> posts\post_%timestamp%.txt
echo. >> posts\post_%timestamp%.txt
echo %greeting%! >> posts\post_%timestamp%.txt
echo. >> posts\post_%timestamp%.txt
echo %post% >> posts\post_%timestamp%.txt
echo. >> posts\post_%timestamp%.txt
echo #GoldTier #Business #Success >> posts\post_%timestamp%.txt
echo. >> posts\post_%timestamp%.txt
echo ============================================================ >> posts\post_%timestamp%.txt

echo Post saved to: posts\post_%timestamp%.txt
echo.
echo NEXT STEP:
echo 1. Copy the post above
echo 2. Open: https://www.facebook.com/profile.php?id=61578524116357
echo 3. Paste and Post!
echo.
echo ============================================================
pause
