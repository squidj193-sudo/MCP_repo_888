"""
取得隨機建議
"""

import requests

# Tool 資訊
TOOL_INFO = {
    "name": "get_advice",
    "api": "https://api.adviceslip.com/advice",
    "author": "Antigravity",
}


def get_advice_data() -> str:
    """呼叫 Advice Slip API，回傳一則建議（英文）"""
    resp = requests.get("https://api.adviceslip.com/advice", timeout=10)
    resp.raise_for_status()
    # 回傳的 JSON 格式為 {"slip": { "id": 123, "advice": "..." }}
    return resp.json().get("slip", {}).get("advice", "No advice found.")


# 單獨測試
if __name__ == "__main__":
    print(get_advice_data())
