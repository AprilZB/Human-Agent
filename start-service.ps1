# start-service.ps1
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "   甲丁智能体 (Human-Agent) 启动脚本" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan

# 启动后端服务
Write-Host "[1/2] 正在独立窗口中启动 FastAPI 后端服务 (端口 8100)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit -Command `"cd backend; if (!(Test-Path venv)) { Write-Host 'Creating virtual environment...'; python -m venv venv }; .\venv\Scripts\activate; Write-Host 'Installing requirements...'; pip install -r requirements.txt; Write-Host 'Starting server...'; python -m app.main`"" -WindowStyle Normal

# 启动前端服务
Write-Host "[2/2] 正在独立窗口中启动 Vue3 前端服务 (端口 8101)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit -Command `"cd frontend; Write-Host 'Installing NPM packages...'; npm install; Write-Host 'Starting dev server...'; npm run dev`"" -WindowStyle Normal

Write-Host "启动指令已下发！请在弹出的新窗口中查看运行日志。" -ForegroundColor Green
Write-Host "后端 API 文档: http://localhost:8100/docs" -ForegroundColor Cyan
Write-Host "前端访问地址: http://localhost:8101" -ForegroundColor Cyan
