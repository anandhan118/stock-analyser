' ═══════════════════════════════════════════════════
'  EdgeScanner.vbs  —  Portable launcher
'  Works on any machine regardless of folder location.
'  Just keep this file in the same folder as edge_scanner.py
' ═══════════════════════════════════════════════════

Set objShell = CreateObject("WScript.Shell")
Set objFSO   = CreateObject("Scripting.FileSystemObject")

' ── Step 1: Find this script's own folder ────────────
appFolder = objFSO.GetParentFolderName(WScript.ScriptFullName)
appFile   = appFolder & "\edge_scanner.py"

' ── Step 2: Find streamlit (tries 4 locations) ───────
streamlitExe = FindStreamlit(appFolder)

If streamlitExe = "" Then
    MsgBox "Could not find streamlit.exe." & vbCrLf & vbCrLf & _
           "Please install it by running:" & vbCrLf & _
           "   pip install streamlit" & vbCrLf & vbCrLf & _
           "Or activate your virtual environment first.", _
           16, "Edge Scanner - Setup Required"
    WScript.Quit
End If

' ── Step 3: Check if already running ─────────────────
Dim isRunning : isRunning = False
Set objWMI   = GetObject("winmgmts:\\.\root\cimv2")
Set colProcs = objWMI.ExecQuery("Select * from Win32_Process Where Name = 'streamlit.exe'")
If colProcs.Count > 0 Then isRunning = True

If isRunning Then
    objShell.Run "http://localhost:8501", 1, False
Else
    cmd = """" & streamlitExe & """ run """ & appFile & """"
    objShell.Run cmd, 0, False
    WScript.Sleep 3500
    objShell.Run "http://localhost:8501", 1, False
End If

' ═══════════════════════════════════════════════════
Function FindStreamlit(baseFolder)
    FindStreamlit = ""
    Dim venvPaths(3)
    venvPaths(0) = baseFolder & "\.venv\Scripts\streamlit.exe"
    venvPaths(1) = baseFolder & "\venv\Scripts\streamlit.exe"
    venvPaths(2) = baseFolder & "\env\Scripts\streamlit.exe"
    venvPaths(3) = baseFolder & "\.env\Scripts\streamlit.exe"
    Dim i
    For i = 0 To 3
        If objFSO.FileExists(venvPaths(i)) Then
            FindStreamlit = venvPaths(i)
            Exit Function
        End If
    Next
    Dim testResult
    testResult = objShell.Run("cmd /c where streamlit >nul 2>&1", 0, True)
    If testResult = 0 Then
        FindStreamlit = "streamlit"
        Exit Function
    End If
    Dim userProfile : userProfile = objShell.ExpandEnvironmentStrings("%USERPROFILE%")
    Dim globalPaths(3)
    globalPaths(0) = userProfile & "\AppData\Local\Programs\Python\Python312\Scripts\streamlit.exe"
    globalPaths(1) = userProfile & "\AppData\Local\Programs\Python\Python311\Scripts\streamlit.exe"
    globalPaths(2) = userProfile & "\AppData\Local\Programs\Python\Python310\Scripts\streamlit.exe"
    globalPaths(3) = userProfile & "\AppData\Roaming\Python\Python312\Scripts\streamlit.exe"
    For i = 0 To 3
        If objFSO.FileExists(globalPaths(i)) Then
            FindStreamlit = globalPaths(i)
            Exit Function
        End If
    Next
End Function
