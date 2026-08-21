@echo off
rem ============================================================================
rem  il.bat - bridge from this repo to the IsaacLab checkout.
rem
rem  Wraps isaaclab.bat so paths line up even though the repo and the checkout
rem  live in different places. Arguments are forwarded verbatim.
rem
rem    il -i
rem    il train --rl_library rsl_rl --task=Isaac-Cartpole-Direct-v0
rem    il -p scripts\tutorials\00_sim\create_empty.py --viz kit
rem    il --where      resolve paths, print them, exit
rem
rem  Does NOT change cwd, so logs/ stays where you called from.
rem  ASCII only on purpose: cmd reads .bat in the console OEM codepage, so
rem  non-ASCII text here turns into garbage commands. Korean docs: README.md.
rem  Never hardcode a path here - put machine values in isaaclab.local.bat.
rem ============================================================================

setlocal

set "REPO_DIR=%~dp0"
if "%REPO_DIR:~-1%"=="\" set "REPO_DIR=%REPO_DIR:~0,-1%"

rem --- 1. per-machine override ------------------------------------------------
if exist "%REPO_DIR%\isaaclab.local.bat" call "%REPO_DIR%\isaaclab.local.bat"

rem --- 2. locate the IsaacLab checkout ---------------------------------------
if not defined ISAACLAB_PATH goto :scan_root
if exist "%ISAACLAB_PATH%\isaaclab.bat" goto :root_ok
echo [il] ERROR: ISAACLAB_PATH = %ISAACLAB_PATH% 1>&2
echo [il]        no isaaclab.bat there. 1>&2
exit /b 2

:scan_root
call :try_root "%REPO_DIR%\IsaacLab"
call :try_root "%REPO_DIR%\..\IsaacLab"
call :try_root "%~d0\rl\IsaacLab"
call :try_root "%~d0\IsaacLab"
call :try_root "%USERPROFILE%\IsaacLab"
if defined ISAACLAB_PATH goto :root_ok

echo [il] ERROR: no IsaacLab checkout found. Looked in: 1>&2
echo [il]          %REPO_DIR%\IsaacLab 1>&2
echo [il]          %REPO_DIR%\..\IsaacLab 1>&2
echo [il]          %~d0\rl\IsaacLab 1>&2
echo [il]          %~d0\IsaacLab 1>&2
echo [il]          %USERPROFILE%\IsaacLab 1>&2
echo [il]        Fix: put one line in %REPO_DIR%\isaaclab.local.bat 1>&2
echo [il]          set "ISAACLAB_PATH=D:\IsaacLab" 1>&2
exit /b 2

:root_ok

rem --- 3. python environment -------------------------------------------------
rem isaaclab.bat checks VIRTUAL_ENV before CONDA_PREFIX. Pin VIRTUAL_ENV here
rem so which python gets used is decided by this file, not by shell state.
if defined ISAACLAB_VENV goto :venv_check
call :try_venv "%VIRTUAL_ENV%"
call :try_venv "%REPO_DIR%\env_isaaclab"
call :try_venv "%REPO_DIR%\.venv"
call :try_venv "%ISAACLAB_PATH%\.venv"
if defined ISAACLAB_VENV goto :venv_check

if defined CONDA_PREFIX goto :report
echo [il] WARN: no venv found; leaving python choice to isaaclab.bat. 1>&2
goto :report

:venv_check
if exist "%ISAACLAB_VENV%\Scripts\python.exe" goto :venv_ok
echo [il] ERROR: ISAACLAB_VENV = %ISAACLAB_VENV% 1>&2
echo [il]        no Scripts\python.exe there. 1>&2
exit /b 2

:venv_ok
set "VIRTUAL_ENV=%ISAACLAB_VENV%"
set "PATH=%ISAACLAB_VENV%\Scripts;%PATH%"
set "PYTHONHOME="
if defined CONDA_PREFIX echo [il] WARN: conda is active; venv wins. Do not mix - see README 5.2. 1>&2

rem --- 4. make sure uv is reachable -----------------------------------------
rem "isaaclab.bat --install" prefers uv and silently falls back to pip when it
rem cannot find it. uv installs itself to %USERPROFILE%\.local\bin, which is
rem not always on PATH, so the same repo would install two different ways on
rem two machines. Put it back on PATH here instead.
where uv >nul 2>nul
if not errorlevel 1 goto :report
if not exist "%USERPROFILE%\.local\bin\uv.exe" goto :report
set "PATH=%USERPROFILE%\.local\bin;%PATH%"
set "IL_UV_ADDED=%USERPROFILE%\.local\bin"
rem --- 5. force UTF-8 for Python file I/O ------------------------------------
rem Warp writes generated CUDA source with open() and no explicit encoding, so
rem on a non-UTF-8 locale (cp949 here) any kernel source containing a non-ASCII
rem character dies with UnicodeEncodeError before it compiles. The kamino
rem solvers hit this. PYTHONUTF8=1 makes open() default to UTF-8 and fixes it.
if not defined PYTHONUTF8 set "PYTHONUTF8=1"
:report
call :warn_cwd
if "%IL_QUIET%"=="1" goto :dispatch
echo [il] IsaacLab : %ISAACLAB_PATH% 1>&2
if defined VIRTUAL_ENV echo [il] venv     : %VIRTUAL_ENV% 1>&2
if not defined VIRTUAL_ENV if defined CONDA_PREFIX echo [il] conda    : %CONDA_PREFIX% 1>&2
echo [il] cwd      : %CD% 1>&2
if defined IL_UV_ADDED echo [il] uv       : put %IL_UV_ADDED% on PATH 1>&2

:dispatch
if "%~1"=="--where" exit /b 0
if "%~1"=="-w" exit /b 0
if "%~1"=="" goto :usage

call "%ISAACLAB_PATH%\isaaclab.bat" %*
set "RC=%ERRORLEVEL%"
endlocal & exit /b %RC%

:usage
echo. 1>&2
echo Usage: il ^<isaaclab.bat args^> 1>&2
echo   il -i                      install 1>&2
echo   il train --rl_library ...   train  - train.bat is shorter 1>&2
echo   il --where                 show resolved paths 1>&2
exit /b 1

rem --- subroutines -----------------------------------------------------------
:warn_cwd
rem If cwd is inside the checkout, logs/ pile up in a disposable folder.
set "CWD_CHK=%CD%"
call set "CWD_CHK=%%CWD_CHK:%ISAACLAB_PATH%=%%"
if "%CWD_CHK%"=="%CD%" goto :eof
echo [il] WARN: cwd is inside the IsaacLab checkout; logs/ would land there. 1>&2
echo [il]       Call from the repo root instead: %REPO_DIR% 1>&2
goto :eof

:try_root
if defined ISAACLAB_PATH goto :eof
if "%~1"=="" goto :eof
if exist "%~f1\isaaclab.bat" set "ISAACLAB_PATH=%~f1"
goto :eof

:try_venv
if defined ISAACLAB_VENV goto :eof
if "%~1"=="" goto :eof
if exist "%~f1\Scripts\python.exe" set "ISAACLAB_VENV=%~f1"
goto :eof
