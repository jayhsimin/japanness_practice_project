# Japanese Vocabulary Practice

一個用於日文單字學習與練習的全端 Web 應用程式，整合 AI 助理功能，幫助使用者更有效率地記憶日文單字。

## 功能介紹

### 單字管理
- **新增單字**：輸入中文與對應日文，儲存至資料庫
- **搜尋單字**：透過中文或日文關鍵字搜尋已儲存的單字
- **編輯 / 刪除**：對已存在的單字進行修改或移除

### 隨機測驗
- 從單字庫隨機抽取 10 題
- 顯示中文，由使用者輸入對應的日文
- 送出後即時比對答案，顯示正確與錯誤結果

### AI 助理
- 點擊「AI 建議」按鈕，AI 會根據輸入的中文 / 日文單字：
  - 產生包含該單字的自然日文例句
  - 提供例句的繁體中文翻譯
  - 檢查使用者輸入的日文是否正確對應中文（拼寫檢查）
- 使用 Hugging Face Qwen2.5-7B-Instruct 模型

## 技術架構

| 層級 | 技術 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vue Router |
| 後端 | Python FastAPI |
| 資料庫 | MySQL（SQLAlchemy ORM） |
| AI 模型 | Hugging Face Inference API（Qwen2.5-7B-Instruct） |

### 專案結構

```
japanness_project/
├── backend/
│   ├── main.py          # FastAPI 主程式（API 路由 + AI 端點 + SPA 靜態服務）
│   ├── db.py            # 資料庫連線設定
│   ├── models.py        # SQLAlchemy 資料模型
│   ├── schemas.py       # Pydantic 請求 / 回應 schema
│   ├── requirements.txt # Python 套件清單
│   └── .env             # 環境變數（不納入版控）
├── jp-front/
│   ├── src/
│   │   ├── views/
│   │   │   ├── AddVocab.vue  # 主頁：單字管理 + AI 助理
│   │   │   └── Quiz.vue      # 隨機測驗頁
│   │   ├── router.ts         # 前端路由設定
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
├── start.bat            # 一鍵啟動伺服器並開啟瀏覽器
├── build.bat            # 建置前端靜態檔案
├── CLAUDE.md
└── .gitignore
```

## 環境需求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Hugging Face API Key（免費申請）

## 安裝與設定

### 1. 安裝後端套件

```bash
cd backend
pip install -r requirements.txt
```

### 2. 安裝前端套件

```bash
cd jp-front
npm install
```

### 3. 設定環境變數

在 `backend/` 目錄下建立 `.env` 檔案：

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的MySQL密碼
MYSQL_DB=japanese
HF_API_KEY=你的HuggingFace_API_Key
```

### 4. 建立 MySQL 資料庫

```sql
CREATE DATABASE japanese CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

資料表會在首次啟動時由 SQLAlchemy 自動建立。

## 啟動方式

### 方法一：雙擊 start.bat（推薦）

直接雙擊 `start.bat`，程式會自動：
1. 啟動 FastAPI 後端伺服器
2. 等待伺服器就緒
3. 開啟瀏覽器進入應用程式

> 可將 `start.bat` 建立桌面捷徑，方便日後使用。

### 方法二：手動啟動

```bash
# 建置前端
cd jp-front && npm run build

# 啟動後端（同時服務前端靜態檔案）
cd backend && uvicorn main:app --reload --port 8000
```

然後開啟瀏覽器前往 http://127.0.0.1:8000

## API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| POST | `/vocab` | 新增單字 |
| GET | `/vocab` | 取得單字列表（支援 `?keyword=` 搜尋） |
| PUT | `/vocab/{id}` | 更新單字 |
| DELETE | `/vocab/{id}` | 刪除單字 |
| GET | `/quiz/random10` | 隨機取得 10 題測驗 |
| POST | `/quiz/submit` | 提交測驗答案並取得結果 |
| POST | `/ai/suggest` | AI 產生例句、翻譯與拼寫檢查 |
