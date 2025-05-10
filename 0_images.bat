@echo off
echo Running Python Script...

REM Run download_images.py
python download_images.py
if %errorlevel% neq 0 (
    echo download_images.py failed
    pause
    exit /b %errorlevel%
)
echo download_images.py ran successfully





echo Script completed successfully.
exit /b