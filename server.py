"""
W8 分組實作：MCP Server
主題：（填入你們選的主題）

分工說明：
- 各組員在 tools/ 建立自己的 Tool，import 到這裡用 @mcp.tool() 註冊
- 指定一位組員負責 @mcp.resource()
- 指定一位組員負責 @mcp.prompt()
"""

from mcp.server.fastmcp import FastMCP
from ddgs import DDGS
import requests

mcp = FastMCP("第8組-server")


# ════════════════════════════════
#  Tools：各組員各自負責一個 Tool
# ════════════════════════════════

from tools.advice_tool import get_advice_data

@mcp.tool()
def get_advice() -> str:
    """取得一則隨機建議。
    當使用者需要生活建議或尋求解惑時使用。"""
    return get_advice_data()


@mcp.tool()
def search_duckduckgo(query: str) -> str:
    """使用 DuckDuckGo 搜尋資訊。可以用來搜尋景點、美食或其他即時資訊。
    例如：搜尋「台北 景點」或「台中 美食」。"""
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=5)
        if not results:
            return "找不到相關結果。"
        
        output = []
        for r in results:
            output.append(f"標題: {r['title']}\n內容: {r['body']}\n連結: {r['href']}")
        
        return "\n\n---\n\n".join(output)
import requests

@mcp.tool()
def get_weather(city: str) -> str:
    """取得指定城市的即時天氣資訊。
    當使用者詢問天氣、溫度、降雨機率、或是是否該出門/帶傘時使用。"""
    try:
        # 直接在 Server 中實作呼叫 wttr.in API
        url = f"https://wttr.in/{city}?format=j1"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        
        data = resp.json()
        current = data['current_condition'][0]
        temp_c = current['temp_C']
        desc = current['weatherDesc'][0]['value']
        humidity = current['humidity']
        feels_like = current['FeelsLikeC']
        
        return (
            f"📍 城市：{city}\n"
            f"🌡️ 目前溫度：{temp_c}°C (體感：{feels_like}°C)\n"
            f"☁️ 天氣狀況：{desc}\n"
            f"💧 濕度：{humidity}%\n"
            f"--- 資料來源：wttr.in ---"
        )
    except Exception as e:
        return f"無法取得 {city} 的天氣資訊。錯誤：{str(e)}"


@mcp.tool()
def hello(name: str) -> str:
    """跟使用者打招呼。測試用，確認 MCP Server 正常運作。"""
    return f"你好，{name}！MCP Server 運作正常 🎉"


# ════════════════════════════════
#  Resource：提供靜態參考資料
#  URI 格式：info://名稱 或 docs://名稱
# ════════════════════════════════

@mcp.resource("info://advice-tips")
def get_advice_tips() -> str:
    """關於尋求建議的提示"""
    return (
        "實用小提示：\n"
        "- 保持開放的心態來面對建議\n"
        "- 每則建議都可能有它背後的智慧\n"
        "- 也可以多試著詢問不同的人事物"
    )


@mcp.resource("info://travel-tips")
def get_travel_tips() -> str:
    """旅行必帶物品與注意事項清單"""
    return (
        "旅行必帶物品：\n"
        "- 護照 / 身分證\n"
        "- 當地貨幣或信用卡\n"
        "- 備用藥品\n"
        "- 充電器與轉接頭\n\n"
        "出發前注意：\n"
        "- 確認當地天氣，準備適當衣物\n"
        "- 查詢當地緊急電話\n"
        "- 備份重要文件"
    )


@mcp.resource("info://search-guide")
def get_search_guide() -> str:
    """如何更有效率地使用 DuckDuckGo 搜尋"""
    return (
        "搜尋小秘訣：\n"
        "- 使用引號 '...' 搜尋精確詞組\n"
        "- 使用 site:website.com 限制搜尋範圍\n"
        "- 嘗試使用不同的關鍵字組合來獲得更多結果"
    )


# ════════════════════════════════
#  Prompt：整合多個 Tool 的提示詞模板
#  使用者透過 /use <名稱> [參數] 呼叫
# ════════════════════════════════

@mcp.prompt()
def advice_plan(topic: str) -> str:
    """產生針對特定主題獲取建議的提示詞"""
    return (
        f"請幫我針對 {topic} 給予一些啟發：\n"
        f"1. 先使用 get_advice 工具取得一則隨機的英文建議\n"
        f"2. 把這則英文建議翻譯成繁體中文\n"
        f"3. 結合這則建議，寫出 3 個可以應用在 {topic} 上的具體行動方案\n"
        f"請用繁體中文回答且語氣要溫暖幽默。"
    )


@mcp.prompt()
def plan_trip(city: str) -> str:
    """產生旅遊行前規劃的提示詞"""
    return (
        f"我要去 {city} 旅行，請幫我準備一份完整的旅遊指南：\n"
        f"1. 先使用 get_weather 查詢 {city} 的即時天氣\n"
        f"2. 使用 search_duckduckgo 搜尋 {city} 的 3 個熱門景點與美食\n"
        f"3. 使用 get_advice 取得一則隨機建議作為我的『旅行錦囊』\n"
        f"4. 請根據以上資訊，規劃一份 1 天的行程建議，並提醒需要帶的衣物。\n"
        f"請全程使用繁體中文回答。"
    )


@mcp.prompt()
def explore_topic(topic: str) -> str:
    """深入探索一個主題的提示詞"""
    return (
        f"我想要深入了解關於 {topic} 的資訊：\n"
        f"1. 使用 search_duckduckgo 搜尋關於 {topic} 的最新發展或相關背景\n"
        f"2. 總結搜尋結果中最關鍵的 3 個重點\n"
        f"3. 如果這是一個生活上的課題，請使用 get_advice 給我一則建議\n"
        f"請以條列式方式回答，並確保資訊來源可靠。"
    )


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        mcp.run(transport="stdio")
    else:
        print("MCP Server 啟動中... http://localhost:8000")
        mcp.run(transport="sse")
