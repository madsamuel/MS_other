# requirements
Manually addint this files to the env didn't work 
    pip install pynvml
    pip install pyinstaller
    pip install pystray

Modifying the pyinstaller input fixed the error 'File "nvidia_encoder_utilization_gui.py", line 1, in <module>'
    pyinstaller --onefile --icon=icon.ico --hidden-import pynvml nvidia_encoder_utilization_gui.py
New error 
    Error: Icon file not found at C:\Users\madsa\AppData\Local\Temp\_MEI1153322\icon.ico
    Traceback (most recent call last):
    File "nvidia_encoder_utilization_gui.py", line 143, in <module>
    File "nvidia_encoder_utilization_gui.py", line 122, in create_icon
    NameError: name 'exit' is not defined
    [PYI-6492:ERROR] Failed to execute script 'nvidia_encoder_utilization_gui' due to unhandled exception!