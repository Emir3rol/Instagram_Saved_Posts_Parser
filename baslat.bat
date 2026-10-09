@echo off
rem Instagram Kaydedilenler - tek tuşla kurulum ve çalıştırma (Windows). Her seferinde bunu çalıştır:
rem Python yoksa kurar, .venv + paketler, İndirilenler'deki saved.json'ı alır, yenileri analiz eder, raporu açar.
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
title Kaydedilenler

set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY python --version >nul 2>nul && set "PY=python"
if not defined PY (
  echo Python bulunamadı, kuruluyor...
  winget install -e --id Python.Python.3.12 --scope user
  echo.
  echo Kurulum bitince bu pencereyi kapatıp baslat.bat'ı yeniden çalıştır.
  pause
  exit /b
)

if not exist .venv\Scripts\python.exe (
  echo İlk kurulum: sanal ortam hazırlanıyor...
  %PY% -m venv .venv || goto hata
)
.venv\Scripts\python.exe -m pip install -q --disable-pip-version-check -r requirements.txt || goto hata

rem Tarayıcının indirdiği en yeni saved*.json → data\saved.json (yeniden çekince yalnız yeni kayıtlar analiz edilir)
set "INDIR="
for /f "usebackq delims=" %%d in (`powershell -NoProfile -Command "(New-Object -ComObject Shell.Application).NameSpace('shell:Downloads').Self.Path"`) do set "INDIR=%%d"
if not defined INDIR set "INDIR=%USERPROFILE%\Downloads"
for /f "delims=" %%f in ('dir /b /o-d "%INDIR%\saved*.json" 2^>nul') do (
  if not exist data mkdir data
  move /y "%INDIR%\%%f" data\saved.json >nul && echo İndirilenler'deki %%f alındı.
  goto alindi
)
:alindi

if not exist data\saved.json (
  powershell -NoProfile -Command "Get-Content -Raw -Encoding UTF8 scrape.js | Set-Clipboard"
  start "" https://www.instagram.com/
  echo.
  echo  ADIM 1 - Kaydedilenlerini çek
  echo  ------------------------------
  echo  1. Tarayıcıda Instagram açıldı. Hesabına giriş yapılı olmalı.
  echo  2. F12'ye bas, "Console" sekmesine geç.
  echo  3. Çekme kodu panoya kopyalandı: Ctrl+V ile yapıştır, Enter'a bas.
  echo     Chrome yapıştırmayı engellerse önce allow pasting yazıp Enter'a bas, sonra tekrar Ctrl+V.
  echo  4. Bitince saved.json iner. Sonra baslat.bat'ı yeniden çalıştır.
  echo.
  pause
  exit /b
)

.venv\Scripts\python.exe analiz.py
.venv\Scripts\python.exe build.py || goto hata
echo.
echo Rapor tarayıcıda açılıyor. Kullandığın sürece bu pencereyi açık bırak.
.venv\Scripts\python.exe izle.py
exit /b

:hata
echo.
echo Bir hata oldu, yukarıdaki mesaja bak.
pause
