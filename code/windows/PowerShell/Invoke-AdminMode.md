Place this at the very top of your `.ps1` script. It does the following:

- Checks if you're running as administrator.
- If not, it restarts the same script with elevated privileges via `Start-Process -Verb RunAs`.
- Then it exits the unelevated instance.
