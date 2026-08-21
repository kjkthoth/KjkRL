@echo off
rem ============================================================================
rem  train.bat - short form of "il train --rl_library rsl_rl". Newton by default.
rem
rem    train --task=Isaac-Cartpole-Direct-v0
rem    train --task=Isaac-Cartpole-Direct-v0 --num_envs=1024 --headless
rem
rem  Note: no "train" word of your own. This file already is the train command.
rem
rem  Injected defaults - skipped when you pass your own:
rem    physics=newton_mjwarp     skipped if you pass physics= or presets=
rem    --visualizer=<x>          only if IL_VISUALIZER is set; skipped on --headless
rem
rem  Overrides:
rem    train --task=... physics=physx     your argument wins
rem    set IL_PHYSICS=off                 turn the injection off
rem    set IL_VISUALIZER=newton           show the Newton viewer while training
rem    set RL_LIBRARY=skrl                instead of rsl_rl
rem
rem  Does NOT change cwd, so logs\rsl_rl\... lands where you called from.
rem  ASCII only - see the note in il.bat. Korean docs: README.md.
rem ============================================================================

setlocal
if not defined RL_LIBRARY set "RL_LIBRARY=rsl_rl"
if not defined IL_PHYSICS set "IL_PHYSICS=newton_mjwarp"
if "%~1"=="" goto :usage
if /I "%~1"=="train" goto :dup
if /I "%~1"=="play" goto :wrongcmd

call "%~dp0_rlargs.bat" %*
call "%~dp0il.bat" train --rl_library %RL_LIBRARY% %*%IL_ADD%
set "RC=%ERRORLEVEL%"
endlocal & exit /b %RC%

:dup
echo [train] ERROR: drop the leading "train" - this file already is it. 1>&2
echo [train]        you typed : train.bat train --task=... 1>&2
echo [train]        use       : train.bat --task=... 1>&2
exit /b 1

:wrongcmd
echo [train] ERROR: use play.bat for playing back a checkpoint. 1>&2
exit /b 1

:usage
echo. 1>&2
echo Usage: train ^<train.py args^> 1>&2
echo   train --task=Isaac-Cartpole-Direct-v0 --num_envs=16 --max_iterations=10 1>&2
echo   train --task=Isaac-Cartpole-Direct-v0 --num_envs=1024 --headless 1>&2
echo. 1>&2
echo Defaults: --rl_library %RL_LIBRARY%  physics=%IL_PHYSICS% 1>&2
echo First run? Use smoke.bat. Full arg list: train --help 1>&2
exit /b 1
