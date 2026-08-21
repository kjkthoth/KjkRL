@echo off
rem ============================================================================
rem  play.bat - short form of "il play --rl_library rsl_rl". Newton by default.
rem
rem    play --task=Isaac-Cartpole-Direct-v0
rem    play --task=Isaac-Cartpole-Direct-v0 --checkpoint logs\rsl_rl\...\model_9.pt
rem
rem  Without --checkpoint it searches logs\, so cwd must match the training run.
rem  That is why this wrapper, like il.bat, does not change cwd.
rem
rem  Unlike train.bat the visualizer is ON here - the point is to look at it.
rem  Defaults and overrides otherwise match train.bat.
rem ============================================================================

setlocal
if not defined RL_LIBRARY set "RL_LIBRARY=rsl_rl"
if not defined IL_PHYSICS set "IL_PHYSICS=newton_mjwarp"
if not defined IL_VISUALIZER set "IL_VISUALIZER=newton"
if "%~1"=="" goto :usage
if /I "%~1"=="play" goto :dup
if /I "%~1"=="train" goto :wrongcmd

call "%~dp0_rlargs.bat" %*
call "%~dp0il.bat" play --rl_library %RL_LIBRARY% %*%IL_ADD%
set "RC=%ERRORLEVEL%"
endlocal & exit /b %RC%

:dup
echo [play] ERROR: drop the leading "play" - this file already is it. 1>&2
exit /b 1

:wrongcmd
echo [play] ERROR: use train.bat for training. 1>&2
exit /b 1

:usage
echo. 1>&2
echo Usage: play ^<play.py args^> 1>&2
echo   play --task=Isaac-Cartpole-Direct-v0 1>&2
echo. 1>&2
echo Defaults: --rl_library %RL_LIBRARY%  physics=%IL_PHYSICS%  --visualizer=%IL_VISUALIZER% 1>&2
exit /b 1
