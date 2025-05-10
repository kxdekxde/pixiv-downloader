@echo off

:: Loop to keep asking the user for content type selection
:select_content
echo Select the type of content to download
echo 1) Images
echo 2) Animations
set /p content_type="Input the number: "

if "%content_type%"=="1" (
    call "0_images.bat"
) else if "%content_type%"=="2" (
    call "0_animations.bat"
) else (
    echo Invalid selection. Please enter 1 or 2.
    goto select_content
)

:: After completing the selected script, loop back to ask for selection again
goto select_content
