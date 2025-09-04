# План очистки дублирующихся файлов

## Файлы для удаления (дубликаты и устаревшие):

### 1. Дублирующиеся скрипты запуска сервера:
- `start_server_simple.py` (дублирует scripts/win/start_simple.cmd)
- `start_server_stable.bat` (дублирует scripts/win/serve_dev.cmd)
- `start_server_stable.ps1` (дублирует scripts/win/serve_dev.cmd)
- `start_server_ULTRA_STABLE.bat` (дублирует scripts/win/serve_dev.cmd)
- `start_server_ULTRA_STABLE.ps1` (дублирует scripts/win/serve_dev.cmd)
- `start_server.bat` (дублирует scripts/win/serve_dev.cmd)
- `start_server.ps1` (дублирует scripts/win/serve_dev.cmd)

### 2. Дублирующиеся скрипты деплоя:
- `deploy_working_code.sh` (дублирует scripts/)
- `deploy.bat` (дублирует scripts/)
- `deploy.sh` (дублирует scripts/)
- `quick_deploy.sh` (дублирует scripts/)
- `simple_deploy.sh` (дублирует scripts/)
- `step_by_step_deploy.sh` (дублирует scripts/)
- `update_server_complete.sh` (дублирует scripts/)
- `update_server.sh` (дублирует scripts/)

### 3. Дублирующиеся скрипты настройки:
- `perfect_full_server_setup.sh` (дублирует scripts/)
- `perfect_server_setup.sh` (дублирует scripts/)
- `proper_server_setup.sh` (дублирует scripts/)
- `simple_server_setup.sh` (дублирует scripts/)
- `server_setup.sh` (дублирует scripts/)
- `ULTRA_PERFECT_server_setup.sh` (дублирует scripts/)
- `working_server_setup.sh` (дублирует scripts/)

### 4. Дублирующиеся скрипты исправления:
- `fix_init.py` (дублирует scripts/)
- `fix_server.sh` (дублирует scripts/)
- `quick_fix.sh` (дублирует scripts/)
- `quick_update.sh` (дублирует scripts/)
- `server_fix.sh` (дублирует scripts/)

### 5. Дублирующиеся скрипты диагностики:
- `check_server.py` (дублирует scripts/win/check_simple.cmd)
- `debug_server.py` (дублирует scripts/win/test_server.cmd)
- `diagnose_and_fix.py` (дублирует scripts/)
- `imple_test.py` (дублирует tests/)
- `run_diagnosis.ps1` (дублирует scripts/win/test_server.cmd)
- `simple_test.py` (дублирует tests/)
- `test_runner.py` (дублирует tests/)

### 6. Дублирующиеся скрипты утилит:
- `clean_and_update.sh` (дублирует scripts/)
- `sync_from_github.sh` (дублирует scripts/)
- `transfer_db.bat` (дублирует scripts/)
- `transfer_db.sh` (дублирует scripts/)

### 7. Дублирующиеся файлы документации:
- `DEPLOY_INSTRUCTIONS.md` (дублирует doc/)
- `DEPLOY_STANDARD.md` (дублирует doc/)
- `DEPLOYMENT_COMPLETE.md` (дублирует doc/)
- `DEPLOYMENT_FINAL.md` (дублирует doc/)
- `DEPLOYMENT_GUIDE.md` (дублирует doc/)
- `DEPLOYMENT.md` (дублирует doc/)
- `GITHUB_DEPLOYMENT.md` (дублирует doc/)
- `PHOTO_UPLOAD_FIXES.md` (дублирует doc/)
- `PHOTO_UPLOAD_TEST.md` (дублирует doc/)
- `QUICK_FIX_CHECKLIST.md` (дублирует doc/)
- `README_DELIVERY.md` (дублирует README.md)
- `SAFE_DEVELOPMENT_GUIDE.md` (дублирует doc/)
- `SERVER_INSTRUCTIONS.md` (дублирует doc/)
- `SERVER_ISSUES_SOLVED.md` (дублирует doc/)
- `SERVER_STARTUP_GUIDE.md` (дублирует doc/)
- `SIMPLE_DEPLOY_INSTRUCTIONS.md` (дублирует doc/)
- `SIMPLE_INSTRUCTIONS.md` (дублирует doc/)
- `SIRIUS_CHANGES_SUMMARY.md` (дублирует doc/)
- `SIRIUS_CHECKLIST.md` (дублирует doc/)
- `UPGRADE_INSTRUCTIONS.md` (дублирует doc/)

### 8. Тестовые файлы:
- `test_analytics.db` (тестовые данные)
- `test_orders.db` (тестовые данные)
- `test_products.db` (тестовые данные)
- `test.db` (тестовые данные)
- `tests_archive` (архив тестов)

### 9. Временные файлы:
- `e` (неизвестный файл)
- `debug_page_load.txt` (временный файл)
- `shoporder-success-fixed.html apptemplatesshoporder-success.html` (временный файл)

## Файлы для сохранения:
- `README.md` (основная документация)
- `requirements.txt` (зависимости)
- `pyproject.toml` (конфигурация проекта)
- `alembic.ini` (конфигурация миграций)
- `Dockerfile` (контейнеризация)
- `Makefile` (сборка)
- `env.example` (пример переменных окружения)
- `sirius.db` (основная база данных)
- `CURSOR_TERMINAL_ISSUE_REPORT.md` (важный отчет)
- `add_delivery_fields_migration.py` (миграция)
- `app_minimal.py` (минимальная версия приложения)
- `get-pip.py` (утилита pip)
