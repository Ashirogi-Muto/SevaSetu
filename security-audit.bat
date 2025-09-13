@echo off
echo ========================================
echo SEVASETU - Security Audit for GitHub
echo ========================================
echo.

echo Checking for security issues before GitHub deployment...
echo.

echo [1/6] Checking for .env files with real credentials...
if exist "backend\.env" (
    echo ❌ WARNING: backend\.env exists - contains real credentials
    echo    Action: Delete or move to secure location before GitHub push
) else (
    echo ✅ backend\.env not found - good
)

if exist "admin-portal\.env" (
    echo ❌ WARNING: admin-portal\.env exists
    echo    Action: Delete before GitHub push
) else (
    echo ✅ admin-portal\.env not found - good
)

if exist "citizen-portal\.env.local" (
    echo ❌ WARNING: citizen-portal\.env.local exists
    echo    Action: Delete before GitHub push
) else (
    echo ✅ citizen-portal\.env.local not found - good
)

echo.
echo [2/6] Checking for .env.example files...
if exist "backend\.env.example" (
    echo ✅ backend\.env.example exists
) else (
    echo ❌ Missing backend\.env.example
)

if exist "admin-portal\.env.example" (
    echo ✅ admin-portal\.env.example exists
) else (
    echo ❌ Missing admin-portal\.env.example
)

if exist "citizen-portal\.env.example" (
    echo ✅ citizen-portal\.env.example exists
) else (
    echo ❌ Missing citizen-portal\.env.example
)

if exist "ai_model_server\.env.example" (
    echo ✅ ai_model_server\.env.example exists
) else (
    echo ❌ Missing ai_model_server\.env.example
)

echo.
echo [3/6] Checking for hardcoded credentials in code...
findstr /s /i "password.*=" admin-portal\src\pages\Login.tsx | findstr "admin123" >nul 2>&1
if errorlevel 1 (
    echo ✅ No hardcoded passwords found in Login.tsx
) else (
    echo ❌ Hardcoded password found in Login.tsx
)

echo.
echo [4/6] Checking for AI tool references...
findstr /s /i "lovable" admin-portal\package.json citizen-portal\package.json >nul 2>&1
if errorlevel 1 (
    echo ✅ No lovable references in package.json files
) else (
    echo ❌ Found lovable references - cleanup incomplete
)

echo.
echo [5/6] Checking for proper .gitignore coverage...
findstr "\.env" .gitignore >nul 2>&1
if errorlevel 1 (
    echo ❌ .gitignore missing .env protection
) else (
    echo ✅ .gitignore properly excludes .env files
)

findstr "node_modules" .gitignore >nul 2>&1
if errorlevel 1 (
    echo ❌ .gitignore missing node_modules protection
) else (
    echo ✅ .gitignore properly excludes node_modules
)

echo.
echo [6/6] Checking for essential documentation...
if exist "LICENSE" (
    echo ✅ LICENSE file exists
) else (
    echo ❌ Missing LICENSE file
)

if exist "DEPLOYMENT.md" (
    echo ✅ DEPLOYMENT.md exists
) else (
    echo ❌ Missing DEPLOYMENT.md
)

if exist "README.md" (
    echo ✅ README.md exists
) else (
    echo ❌ Missing README.md
)

echo.
echo ========================================
echo Security Audit Complete!
echo ========================================
echo.
echo IMPORTANT: Before pushing to GitHub:
echo 1. Review any ❌ warnings above
echo 2. Delete any .env files with real credentials
echo 3. Ensure all secrets are in .env.example format
echo 4. Test with clean environment setup
echo.
echo ✅ If all checks passed, project is ready for GitHub!
echo.
pause