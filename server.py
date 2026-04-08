"""
W8 分組實作：MCP Server
主題：（填入你們選的主題）

分工說明：
- 各組員在 tools/ 建立自己的 Tool，import 到這裡用 @mcp.tool() 註冊
- 指定一位組員負責 @mcp.resource()
- 指定一位組員負責 @mcp.prompt()
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("第X組-server")


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


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        mcp.run(transport="stdio")
    else:
        print("MCP Server 啟動中... http://localhost:8000")
        mcp.run(transport="sse")
