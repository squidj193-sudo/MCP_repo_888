# MCP Server + AI agent 分組實作

> 課程：AI Agent 開發 — MCP（Model Context Protocol）
> 主題：旅行助手

---

## Server 功能總覽

> 本 MCP Server 提供三個 Tool、兩個 Resource、兩個 Prompt，讓 AI Agent 能查天氣、搜尋景點美食、並給予旅行建議。

| Tool 名稱                 | 功能說明     | 負責組員 |
| ------------------------- | ------------ | -------- |
| get_weather | 查詢即時天氣 |  吳東霖 |
|  web_search   |  搜尋景點、美食  |  江庭翔 |
| get_advice  | 旅行前的人生建議 |  葉書愷  |

---

## 組員與分工

| 姓名   | 負責功能              | 檔案          | 使用的 API          |
| ------ | --------------------- | ------------- | ------------------- |
| 吳東霖 | 查詢即時天氣          | `tools/`      | wttr.in             |
| 江庭翔 | 搜尋景點、美食        | `tools/`      | DuckDuckGo Search   |
| 葉書愷 | 旅行前的人生建議      | `tools/`      | Advice Slip         |
| 黃元稜 | Resource + Prompt     | `server.py`   | —                   |
| 黃元稜 | Agent（用 AI 產生）   | `agent.py`    | Gemini API          |

---

## 專案架構

```
├── server.py              # MCP Server 主程式
├── agent.py               # MCP Client + Gemini Agent
├── tools/
│   ├── __init__.py
│   ├── advice_tool.py     # 葉書愷：人生建議 Tool
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 使用方式

```bash
# 1. 建立虛擬環境
python -m venv .venv
.venv\Scripts\activate   # Windows

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 設定 API Key
copy .env.example .env
# 編輯 .env，填入你的 GEMINI_API_KEY

# 4. 用 MCP Inspector 測試 Server
mcp dev server.py

# 5. 用 Agent 對話
python agent.py
```

---

## 測試結果

### MCP Inspector 截圖

> 貼上 Inspector 的截圖（Tools / Resources / Prompts 三個分頁都要有）

### Agent 對話截圖

> 貼上 Agent 對話的截圖（顯示 Gemini 呼叫 Tool 的過程，以及使用 /use 呼叫 Prompt 的結果）
<img width="974" height="848" alt="image" src="https://github.com/user-attachments/assets/a3234ea1-394e-4d9b-90c0-4dcbfac42bf0" />

---

## 各 Tool 說明

### `get_weather`（負責：吳東霖）

- **功能**：查詢指定城市的即時天氣，包含溫度、體感溫度、天氣狀況與濕度
- **使用 API**：[wttr.in](https://wttr.in)
- **參數**：`city: str`（城市名稱，支援英文或中文）
- **回傳範例**：

```
📍 城市：Taipei
🌡️ 目前溫度：24°C (體感：26°C)
☁️ 天氣狀況：Partly cloudy
💧 濕度：78%
--- 資料來源：wttr.in ---
```

---

### `search_duckduckgo`（負責：江庭翔）

- **功能**：使用 DuckDuckGo 搜尋景點、美食或任何即時資訊，每次回傳最多 5 筆結果
- **使用 API**：DuckDuckGo Search（`ddgs` 套件）
- **參數**：`query: str`（搜尋關鍵字，例如：「台北 景點」、「台中 美食」）
- **回傳範例**：

```
標題: 台北必去景點推薦
內容: 台北 101、象山、九份...
連結: https://...

---

標題: 台北美食地圖
內容: 士林夜市、饒河夜市...
連結: https://...
```

---

### `get_advice`（負責：葉書愷）

- **功能**：從 Advice Slip API 取得一則隨機英文生活建議，旅行前獲得靈感或心理準備
- **使用 API**：[Advice Slip](https://api.adviceslip.com)
- **參數**：無
- **回傳範例**：

```
💡 Advice #147: "Don't be afraid to start over. It's a brand new opportunity to rebuild what you truly want."
```

---

## 心得

### 吳東霖

在實作 `get_weather` 的過程中，最困難的部分是處理不同城市名稱格式的相容性——中文城市名有時會導致 API 回傳不正確的結果，後來發現改用英文名或加上國家代碼可以提升成功率。這次學到了如何在 MCP Tool 中正確處理外部 API 的例外狀況，讓 Server 不會因單一請求失敗而當機。

### 江庭翔

搜尋工具的挑戰在於結果的格式整理。DuckDuckGo 回傳的資料是 JSON，但每筆資料的完整度不一，有些缺少摘要或連結，需要做防錯處理。透過這次實作更了解如何把外部資料「包裝」成對 AI 友善的格式，讓 LLM 能正確理解並使用搜尋結果。

### 葉書愷

Advice Slip API 本身很簡單，但如何讓 AI 把這個工具用得有趣，靠的是在 docstring 裡寫清楚「什麼情境下該呼叫這個 Tool」。這次實作讓我明白 MCP Tool 的 docstring 不只是說明，更是 AI 的「行為指南」，寫得好不好直接影響 AI 會不會自動選用這個工具。

### 黃元稜

負責 Resource 與 Prompt 的設計，讓我理解到 MCP 的架構比單純的 Tool Calling 更完整。Resource 像是提供靜態的知識庫，讓 AI 在需要時查閱；Prompt 則是預設好的「任務流程」，讓使用者可以一句話觸發複雜的多工具組合。MCP 最大的優勢是把 Tool、Resource、Prompt 統一在標準協定下，讓不同的 AI 客戶端都能共用同一個 Server，這是上週單純 Tool Calling 做不到的事。

---

### MCP 跟上週的 Tool Calling 有什麼不同？

上週的 Tool Calling 是把工具直接綁在單一 LLM 的 API 呼叫裡，每次都要重新定義 schema，換個模型或客戶端就要重寫一遍。MCP 則是把 Server 獨立出來，任何支援 MCP 的客戶端（Claude、Gemini、Inspector…）都可以連進來使用同一組工具，且 Resource 和 Prompt 的設計讓知識管理和工作流程更有條理，大大提升了可重用性與擴展性。
