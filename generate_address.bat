@echo off
echo ============================================================
echo Philippine Address Data Generator
echo ============================================================
echo.
echo This script will:
echo 1. Fetch all regions, provinces, cities, and barangays
echo 2. Generate a complete address.js file with 42,000+ barangays
echo 3. File size will be approximately 5-10 MB
echo.
echo This process may take 10-30 minutes depending on your internet speed.
echo.
pause

echo.
echo Installing required Python package (requests)...
pip install requests

echo.
echo Starting data generation...
python generate_complete_address.py

echo.
echo ============================================================
echo Process Complete!
echo ============================================================
echo.
echo If successful, you should see 'address_complete.js' file.
echo.
echo Next steps:
echo 1. Backup your current address.js:
echo    copy app\static\Javascript\registration\address.js app\static\Javascript\registration\address_old.js
echo.
echo 2. Replace with the new file:
echo    copy address_complete.js app\static\Javascript\registration\address.js
echo.
echo 3. Clear browser cache and test
echo.
pause
