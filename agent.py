import asyncio
import os
import json
from dotenv import load_dotenv
from mcp.client.sse import sse_client
from google import genai
from google.genai import types

load_dotenv()

# Gemini API 設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = "gemini-2.0-flash-exp"

async def main():
    if not GEMINI_API_KEY:
        print("請在 .env 檔案中設定 GEMINI_API_KEY")
        return

    print("正在連線到 MCP Server...")
    # 使用 sse_client 連接
    async with sse_client("http://localhost:8000/sse") as (read, write):
        from mcp import ClientSession
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 1. 獲取工具並轉換為 Gemini Tools
            tools_resp = await session.list_tools()
            
            gemini_tools = []
            if tools_resp.tools:
                function_declarations = []
                for tool in tools_resp.tools:
                    # 將 MCP 的 inputSchema (JSON Schema) 轉為 Gemini 格式
                    function_declarations.append(
                        types.FunctionDeclaration(
                            name=tool.name,
                            description=tool.description,
                            parameters=tool.inputSchema
                        )
                    )
                gemini_tools.append(types.Tool(function_declarations=function_declarations))

            print(f"已連接！伺服器名稱: {session.server_capabilities}")
            print(f"可用工具：{[t.name for t in tools_resp.tools]}")
            
            # 2. 開始對話
            # 建立 chat session，關閉自動執行工具 (因為我們要透過 MCP session 執行)
            chat = client.chats.create(
                model=MODEL_ID, 
                config=types.GenerateContentConfig(
                    tools=gemini_tools,
                )
            )
            
            print("\n=== Gemini MCP Agent 已就緒 ===")
            print("輸入 'exit' 或 'quit' 結束對話。")
            
            while True:
                user_input = input("\n你：")
                if not user_input.strip():
                    continue
                if user_input.lower() in ["exit", "quit"]:
                    break
                
                try:
                    # 發送訊息
                    response = chat.send_message(user_input)
                    
                    while True:
                        # 檢查是否有 function call
                        # 舊版 SDK 可能在 parts[0]，新版 SDK 在候選人中
                        has_fc = False
                        if response.candidates and response.candidates[0].content.parts:
                            for part in response.candidates[0].content.parts:
                                if part.function_call:
                                    has_fc = True
                                    name = part.function_call.name
                                    args = part.function_call.args
                                    
                                    print(f"DEBUG: 呼叫工具 [{name}] 參數: {args}")
                                    
                                    # 透過 MCP 呼叫工具
                                    try:
                                        tool_result = await session.call_tool(name, args)
                                        result_content = ""
                                        for content in tool_result.content:
                                            if content.type == "text":
                                                result_content += content.text
                                        
                                        print(f"DEBUG: 工具回傳結果: {result_content[:100]}...")
                                        
                                        # 將結果送回 Gemini
                                        response = chat.send_message(
                                            types.Part.from_function_response(
                                                name=name,
                                                response={'result': result_content}
                                            )
                                        )
                                    except Exception as tool_err:
                                        print(f"工具執行失敗: {tool_err}")
                                        response = chat.send_message(
                                            types.Part.from_function_response(
                                                name=name,
                                                response={'error': str(tool_err)}
                                            )
                                        )
                        
                        if not has_fc:
                            break
                    
                    # 顯示最終回答
                    if response.text:
                        print(f"\nAgent：{response.text}")
                        
                except Exception as e:
                    print(f"對話發生錯誤：{e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n用戶終止。")
