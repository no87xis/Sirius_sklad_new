@echo off & chcp 65001 >nul
REM Скрипт для коммита изменений

echo Коммит изменений...
echo.

REM Добавляем все файлы
git add .

REM Создаем коммит
git commit -m "feat(dev): add Windows server scripts and fix terminal stability

- Add Windows batch scripts for server management (scripts/win/)
- Create simplified server control scripts (start_simple.cmd, stop_simple.cmd, check_simple.cmd)
- Fix PID handling in serve_dev.cmd and serve_status.cmd
- Add /health endpoint to app/main.py for health checks
- Update documentation with new server management workflow
- Create comprehensive plans for project cleanup and restructuring
- Add technical questions list for project clarification
- Implement Cursor IDE safety rules to prevent terminal hangs
- Update .gitignore to exclude logs and PID files
- Create operational guides and terminal stability tests

Resolves terminal stability issues with long-running processes in Cursor IDE"

echo.
echo Коммит создан успешно!
echo.

REM Показываем статус
echo Статус git:
git status --short

echo.
pause
