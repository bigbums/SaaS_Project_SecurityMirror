@echo off
chcp 65001 >nul

:: Default to emojis
set "SYM_FLUSH=🔄"
set "SYM_SEED=🌱"
set "SYM_DUMP=💾"
set "SYM_LOAD=📥"
set "SYM_DONE=✅"

:: Test emoji support
echo %SYM_FLUSH% >nul
if errorlevel 1 (
    set "SYM_FLUSH=[>]"
    set "SYM_SEED=[>]"
    set "SYM_DUMP=[>]"
    set "SYM_LOAD=[>]"
    set "SYM_DONE=[✓]"
)
