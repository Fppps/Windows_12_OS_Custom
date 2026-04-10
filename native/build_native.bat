@echo off
setlocal
cd /d "%~dp0"
if not exist build mkdir build
where gcc >nul 2>nul
if %errorlevel%==0 (
    echo Building w12native.dll with gcc...
    gcc -shared -O2 -std=c11 -Wall -Wextra -Iinclude src\w12_native_core.c src\w12_window_effects.c src\w12_wallpaper_fx.c -o build\w12native.dll
    if %errorlevel% neq 0 goto :fail
    echo Native library built: build\w12native.dll
    exit /b 0
)
where clang >nul 2>nul
if %errorlevel%==0 (
    echo Building w12native.dll with clang...
    clang -shared -O2 -std=c11 -Wall -Wextra -Iinclude src\w12_native_core.c src\w12_window_effects.c src\w12_wallpaper_fx.c -o build\w12native.dll
    if %errorlevel% neq 0 goto :fail
    echo Native library built: build\w12native.dll
    exit /b 0
)

echo No C compiler found. Install MinGW-w64 or LLVM clang to build the optional native layer.
exit /b 1

:fail
echo Build failed.
exit /b 1
