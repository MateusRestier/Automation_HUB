' Fecha todas as instâncias do Excel abertas
On Error Resume Next
Dim objExcelApp
Set objExcelApp = GetObject(, "Excel.Application")
If Not objExcelApp Is Nothing Then
    objExcelApp.Quit
    Set objExcelApp = Nothing
End If
On Error GoTo 0

Dim objExcel
Dim objFSO
Dim strScriptPath
Dim strFilePath

' Obter o caminho completo do script .vbs
Set objFSO = CreateObject("Scripting.FileSystemObject")
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Concatenar o caminho da pasta com o nome da planilha
strFilePath = strScriptPath & "\Piloto.xlsm"

' Criar o objeto Excel e abrir a planilha dinamicamente
Set objExcel = CreateObject("Excel.Application")
objExcel.Workbooks.Open strFilePath
objExcel.Application.Run "Piloto.xlsm!CMV.CMV"
objExcel.DisplayAlerts = False
