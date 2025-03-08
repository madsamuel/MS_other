1. Install Python from the store by opening command promts and typing
    winget install -e --id Python.Python.3.10
2. Open PowerShell
3. Get the file from the repo https://github.com/madsamuel/MS_other/tree/master/perf_tools/nvidia_decoder_encoder_utilization    
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/madsamuel/MS_other/master/perf_tools/nvidia_decoder_encoder_utilization/nvidia_encoder_utilization_gui.py" -OutFile "nvidia_encoder_utilization_gui.py"

    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/madsamuel/MS_other/master/perf_tools/nvidia_decoder_encoder_utilization/icon.ico" -OutFile "icon.ico"

    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/madsamuel/MS_other/master/perf_tools/nvidia_decoder_encoder_utilization/req.txt" -OutFile "req.txt"
4. Go to command prompt as Administrator and run
    python3 -m pip install -r req.txt
5. Run 
    python3 nvidia_encoder_utilization_gui.py