@echo off
echo Running Animation Processing Scripts...

REM Run download_ugoira.py
python download_ugoira.py
if %errorlevel% neq 0 (
    echo download_ugoira.py failed
    pause
    exit /b %errorlevel%
)
echo download_ugoira.py ran successfully

REM Run extract_zip_files.py
python extract_zip_files.py
if %errorlevel% neq 0 (
    echo extract_zip_files.py failed
    pause
    exit /b %errorlevel%
)
echo extract_zip_files.py ran successfully

REM Run make_video_mp4.py
python make_video_mp4.py
if %errorlevel% neq 0 (
    echo make_video_mp4.py failed
    pause
    exit /b %errorlevel%
)
echo make_video_mp4.py ran successfully


echo All animation processing scripts completed successfully.
exit /b