Set objShell = CreateObject("WScript.Shell")
objShell.Run "taskkill /f /im streamlit.exe", 0, True
MsgBox "Edge Scanner stopped.", 64, "Edge Scanner"
