@echo off
echo 📊 Перенос базы данных Sirius Group...

REM Проверяем наличие файла БД
if not exist "sirius_sklad.db" (
    echo ❌ Файл sirius_sklad.db не найден!
    echo Убедитесь, что вы находитесь в папке с проектом
    pause
    exit /b 1
)

echo ✅ Найден файл базы данных: sirius_sklad.db
for %%A in (sirius_sklad.db) do echo 📁 Размер файла: %%~zA байт

echo.
echo 🚀 Инструкции по переносу на сервер:
echo.
echo 1. Загрузите файл sirius_sklad.db на сервер:
echo    scp sirius_sklad.db root@your-server-ip:/root/
echo.
echo 2. На сервере выполните:
echo    cd /root/sirius-project/Sirius_sklad_new
echo    cp /root/sirius_sklad.db .
echo    chown www-data:www-data sirius_sklad.db
echo    chmod 644 sirius_sklad.db
echo.
echo 3. Перезапустите сервер:
echo    pkill -f uvicorn
echo    source venv/bin/activate
echo    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
echo.
echo ✅ База данных будет перенесена со всеми данными!
pause
