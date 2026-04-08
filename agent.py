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
# 使用最新支援 Tool Use 的模型
MODEL_ID = "gemini-2.5-flash"

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
            
            # 1. 獲取初始工具清單
            tools_resp = await session.list_tools()
            print(f"已連接！可用工具：{[t.name for t in tools_resp.tools]}")
            
            # 將 MCP 工具轉換為 Gemini 的 FunctionDeclaration
            function_declarations = []
            if tools_resp.tools:
                for tool in tools_resp.tools:
                    function_declarations.append(
                        types.FunctionDeclaration(
                            name=tool.name,
                            description=tool.description,
                            parameters=tool.inputSchema
                        )
                    )
            
            # 配置 Gemini 工具
            config = types.GenerateContentConfig(
                tools=[types.Tool(function_declarations=function_declarations)] if function_declarations else []
            )
            chat = client.chats.create(model=MODEL_ID, config=config)
            
            print("\n=== Gemini MCP Agent 已就緒 ===")
            print("可用指令：")
            print(" - /tools     : 列出可用工具")
            print(" - /resources : 列出可用資源")
            print(" - /prompts   : 列出可用提示詞模板")
            print(" - /read <uri>: 讀取資源內容")
            print(" - /use <name> [參數]: 使用提示詞模板")
            print(" - 直接輸入文字與 Agent 對話，輸入 'exit' 結束。")
            
            while True:
                try:
                    user_input = input("\n你：").strip()
                    if not user_input: continue
                    if user_input.lower() in ["exit", "quit"]: break
                    
                    # 處理互動指令
                    if user_input.startswith("/"):
                        cmd_parts = user_input.split(" ", 2)
                        cmd = cmd_parts[0].lower()
                        
                        if cmd == "/tools":
                            tl = await session.list_tools()
                            print("\n[可用工具]")
                            for t in tl.tools: print(f"- {t.name}: {t.description}")
                            continue
                        elif cmd == "/resources":
                            rl = await session.list_resources()
                            print("\n[可用資源]")
                            for r in rl.resources: print(f"- {r.uri}: {r.name}")
                            continue
                        elif cmd == "/prompts":
                            pl = await session.list_prompts()
                            print("\n[可用提示詞模板]")
                            for p in pl.prompts: print(f"- {p.name}: {p.description}")
                            continue
                        elif cmd == "/read":
                            if len(cmd_parts) < 2: 
                                print("用法: /read <uri>")
                                continue
                            res = await session.read_resource(cmd_parts[1])
                            print(f"\n--- 內容 [{cmd_parts[1]}] ---")
                            for c in res.contents: print(c.text)
                            print("--------------------------")
                            continue
                        elif cmd == "/use":
                            if len(cmd_parts) < 2:
                                print("用法: /use <name> [參數]")
                                continue
                            p_name = cmd_parts[1]
                            p_args = {"city": cmd_parts[2], "topic": cmd_parts[2]} if len(cmd_parts) == 3 else {}
                            pr = await session.get_prompt(p_name, p_args)
                            user_input = "".join([m.content.text for m in pr.messages if m.content.type == "text"])
                            print(f"DEBUG: 載入模板內容...\n")

                    # 發送訊息至 Gemini 並處理 Tool Calling
                    response = chat.send_message(user_input)
                    
                    while True:
                        parts = []
                        found_fc = False
                        
                        if response.candidates and response.candidates[0].content.parts:
                            for part in response.candidates[0].content.parts:
                                if part.function_call:
                                    found_fc = True
                                    name = part.function_call.name
                                    args = part.function_call.args
                                    
                                    print(f" -> 🤖 執行工具: {name}({args})")
                                    try:
                                        result = await session.call_tool(name, args)
                                        text_res = "\n".join([c.text for c in result.content if c.type == "text"])
                                        parts.append(types.Part.from_function_response(
                                            name=name, response={"result": text_res}
                                        ))
                                    except Exception as err:
                                        parts.append(types.Part.from_function_response(
                                            name=name, response={"error": str(err)}
                                        ))
                        
                        if not found_fc:
                            if response.text:
                                print(f"\nAgent：{response.text}")
                            break
                        else:
                            # 將工具結果回傳給模型以獲得最終答案
                            response = chat.send_message(parts)

                except Exception as e:
                    print(f"對話錯誤: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n對話終止。")
