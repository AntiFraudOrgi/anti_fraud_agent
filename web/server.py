from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn
import os

# 建立 FastAPI 應用實例
app = FastAPI(
    title="FastAPI 網站",
    description="提供三個主要頁面的簡單 FastAPI 網站",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源，實際部署時應限制為特定網域
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent


# 掛載靜態文件目錄
app.mount("/static", StaticFiles(directory="web/static"), name="static")

@app.get("/")
async def root():
    # 回傳首頁 index.html
    return FileResponse(BASE_DIR / "index.html")

# 添加兩種可能的路由模式
@app.get("/consultation")
@app.get("/consultation.html")
async def consultation_page():
    # 回傳諮詢頁面 consultation.html
    return FileResponse(BASE_DIR / "consultation.html")

@app.get("/knowledge")
@app.get("/knowledge.html")
async def knowledge_page():
    # 回傳知識庫頁面 knowledge.html
    return FileResponse(BASE_DIR / "knowledge.html")

# 啟動服務器
if __name__ == "__main__":
    # 直接傳遞 app 實例
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=False)