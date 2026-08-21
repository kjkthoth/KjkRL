@echo off
rem ============================================================================
rem  smoke.bat - does the pipeline run end to end? Policy quality is not the
rem  point. 16 envs / 10 iterations finishes in minutes.
rem
rem  This is the verification command from the 3.0.0-beta2 kitless install docs,
rem  copied as-is. Extra args are appended, so you can add --headless.
rem
rem  Pass = no crash, and a checkpoint appears under logs\rsl_rl\.
rem ============================================================================

setlocal
call "%~dp0il.bat" train --rl_library rsl_rl --task=Isaac-Cartpole-Direct-v0 --num_envs=16 --max_iterations=10 physics=newton_mjwarp --visualizer newton %*
set "RC=%ERRORLEVEL%"
endlocal & exit /b %RC%
