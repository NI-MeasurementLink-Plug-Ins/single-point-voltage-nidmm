pause
cd ../../source
pause
poetry run pyinstaller --noconfirm --onedir --console --clean --contents-directory "." --distpath "../pyinstaller/dist" --workpath "../pyinstaller/temp" --name singlePointVoltage --add-data "singlePointVoltage.measui;." --add-data "singlePointVoltage.serviceconfig;."  "singlePointVoltage_measurement.py"
pause