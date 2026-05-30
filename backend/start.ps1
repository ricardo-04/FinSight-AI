Push-Location $PSScriptRoot
& C:\Users\ra-pombo\Desktop\FinSight-AI\.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000
Pop-Location
