@echo off
echo Installing faker dependencies...
pip install -r faker_requirements.txt

echo.
echo Running faker script...
python faker_data.py

echo.
echo Press any key to exit...
pause