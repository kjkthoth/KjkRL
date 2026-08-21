@echo off
rem ============================================================================
rem  _rlargs.bat - internal helper for train.bat / play.bat. Do not call directly.
rem
rem  Scans the forwarded args for things the user already specified, and returns
rem  only the missing defaults in IL_ADD. No setlocal here on purpose: the
rem  caller needs to see IL_ADD.
rem
rem  To disable an injection, set the sentinel:  set IL_PHYSICS=off
rem  Clearing the variable does NOT disable it - the caller re-applies its
rem  default. For the visualizer only "off" is a sentinel, because "none" is a
rem  real Isaac Lab value meaning "disable all visualizers".
rem ============================================================================

set "IL_ADD="
set "IL_HAS_PHYSICS="
set "IL_HAS_VIZ="
set "IL_HAS_HEADLESS="

:scan
if "%~1"=="" goto :decide
set "IL_A=%~1"
rem physics= or presets= both mean the user picked the physics backend.
if not "%IL_A%"=="%IL_A:physics=%" set "IL_HAS_PHYSICS=1"
if not "%IL_A%"=="%IL_A:presets=%" set "IL_HAS_PHYSICS=1"
rem --viz is both an alias of and a prefix of --visualizer, so one test does it.
if not "%IL_A%"=="%IL_A:--viz=%" set "IL_HAS_VIZ=1"
if "%IL_A%"=="--headless" set "IL_HAS_HEADLESS=1"
shift
goto :scan

:decide
if defined IL_HAS_PHYSICS goto :viz
if not defined IL_PHYSICS goto :viz
if /I "%IL_PHYSICS%"=="off" goto :viz
set "IL_ADD=%IL_ADD% physics=%IL_PHYSICS%"

:viz
if defined IL_HAS_VIZ goto :eof
if defined IL_HAS_HEADLESS goto :eof
if not defined IL_VISUALIZER goto :eof
if /I "%IL_VISUALIZER%"=="off" goto :eof
set "IL_ADD=%IL_ADD% --visualizer=%IL_VISUALIZER%"
goto :eof
