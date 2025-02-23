Random experiments and tests. Safe to ignore :).

1. Move all your files, including icon in one folder.
2. Navigate to the folder
2. Create env 
	python -m venv myenv
3. Set execution policy for the environment 
	Set-ExecutionPolicy -ExecutionPolicy AllSigned -Scope Process
4. Run the activate script
	.\myenv\Scripts\activate
    When prompted press R for Run once 
5. Install PyInstaller
	pip install pyinstaller
    (optional) install all modules your code uses
6. Create the Executable with PyInstaller
	pyinstaller --onefile --icon=icon.ico main.py
