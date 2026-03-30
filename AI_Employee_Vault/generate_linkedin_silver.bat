@echo off
echo ============================================
echo   Silver Tier - LinkedIn Post Generator
echo ============================================
echo.

cd /d "%~dp0"

echo Options:
echo   1. Generate AI Employee Update post
echo   2. Generate Email Campaign Success post
echo   3. Generate Custom post
echo   4. View existing drafts
echo   5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Generating AI Employee Update post...
    python linkedin_post_generator_silver.py
    pause
    goto :view
)

if "%choice%"=="2" (
    echo.
    echo Generating Email Campaign Success post...
    python -c "from linkedin_post_generator_silver import LinkedInPostGenerator; g = LinkedInPostGenerator(); g.generate_from_email_campaign('AI Employee Launch', ['10,000+ emails sent', '45%% open rate', '12%% CTR'])"
    pause
    goto :view
)

if "%choice%"=="3" (
    echo.
    set /p title="Enter post title: "
    set /p content="Enter post content: "
    python -c "from linkedin_post_generator_silver import LinkedInPostGenerator; g = LinkedInPostGenerator(); g.generate_post_draft('%title%', '%content%', ['AI', 'Automation'], 'Share your thoughts!')"
    pause
    goto :view
)

if "%choice%"=="4" (
    goto :view
)

if "%choice%"=="5" (
    exit /b
)

echo Invalid choice!
pause
exit /b

:view
echo.
echo ============================================
echo   LinkedIn Drafts in Silver_Tier/LinkedIn_Drafts/
echo ============================================
dir /b Silver_Tier\LinkedIn_Drafts\*.md 2>nul || echo No drafts found
echo.
pause
