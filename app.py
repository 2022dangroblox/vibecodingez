import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os

app = FastAPI()

# Lấy API Key từ biến môi trường ẩn trên Render để bảo mật
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

class ChatPayload(BaseModel):
    prompt: str
    effort: str # 'medium' hoặc 'xhigh'

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VibeCodingEz</title>
    <script src="https://jsdelivr.net"></script>
    <style>
        .loading-dots:after {
            content: ' .';
            animation: dots 1.5s steps(5, end) infinite;
        }
        @keyframes dots {
            0%, 20% { content: ' .'; }
            40% { content: ' . .'; }
            60% { content: ' . . .'; }
            80%, 100% { content: ''; }
        }
    </style>
</head>
<body class="bg-zinc-950 text-zinc-100 min-h-screen flex flex-col justify-between font-sans antialiased selection:bg-emerald-500/30 p-4">
    
    <!-- Navbar -->
    <header class="max-w-3xl w-full mx-auto border-b border-zinc-800 pb-4 mb-4 flex justify-between items-center bg-zinc-950/80 backdrop-blur sticky top-0 z-10">
        <h1 class="text-lg font-bold tracking-tight text-white">VibeCodingEz</h1>
        <div class="flex gap-2">
            <span class="bg-zinc-900 text-zinc-400 text-xs px-2.5 py-1 rounded border border-zinc-800 font-mono">Free: Medium Effort</span>
            <span class="bg-emerald-500/10 text-emerald-400 text-xs px-2.5 py-1 rounded border border-emerald-500/20 font-mono">Premium: xHigh Effort</span>
        </div>
    </header>
    
    <!-- Main Chat Workspace -->
    <main class="flex-1 max-w-3xl w-full mx-auto bg-zinc-900/20 border border-zinc-800 rounded-xl p-4 flex flex-col justify-between overflow-hidden">
        <!-- Messages Container -->
        <div id="chat-box" class="flex-1 overflow-y-auto space-y-4 min-h-[450px] mb-4 pr-2 scrollbar-thin">
            <div class="bg-zinc-900/60 p-3.5 rounded-lg border border-zinc-800 max-w-[85%]">
                <p class="text-xs text-zinc-500 font-mono mb-1">System</p>
                <p class="text-sm text-zinc-300">Hệ thống đã sẵn sàng. Vui lòng nhập câu hỏi của bạn.</p>
            </div>
        </div>
        
        <!-- Processing Indicator -->
        <div id="status" class="hidden text-xs text-zinc-500 font-mono mb-3 px-1">
            <span class="loading-dots">Đang xử lý dữ liệu và suy luận</span>
        </div>
        
        <!-- Input Group -->
        <div class="flex gap-2 bg-zinc-900/40 p-1.5 border border-zinc-800 rounded-xl focus-within:border-zinc-700 transition-colors">
            <input type="text" id="msg" placeholder="Nhập câu hỏi hoặc đoạn mã cần xử lý..." class="flex-1 bg-transparent rounded-lg px-3 py-2 text-sm focus:outline-none placeholder:text-zinc-600">
            <select id="effort" class="bg-zinc-900 border border-zinc-800 rounded-lg px-2 text-xs font-mono text-zinc-400 focus:outline-none cursor-pointer">
                <option value="medium">Bản Free (Nhanh)</option>
                <option value="xhigh">Bản Pro (xHigh)</option>
            </select>
            <button onclick="send()" class="bg-zinc-100 hover:bg-white text-zinc-950 font-medium px-5 rounded-lg text-sm transition-colors cursor-pointer">Gửi</button>
        </div>
    </main>

    <!-- Footer Credit -->
    <footer class="text-center text-[11px] text-zinc-600 font-mono mt-4">
        &copy; 2026 VibeCodingEz. Powered by RooneyHub.
    </footer>

    <script>
        async function send() {
            const msgInput = document.getElementById('msg');
            const effort = document.getElementById('effort').value;
            const chatBox = document.getElementById('chat-box');
            const status = document.getElementById('status');
            const text = msgInput.value.trim();
            if(!text) return;
            
            // Render User Message
            chatBox.innerHTML += `<div class="bg-zinc-800/80 p-3 rounded-lg border border-zinc-700 max-w-[85%] ml-auto text-right"><p class="text-sm">${text}</p></div>`;
            msgInput.value = '';
            status.classList.remove('hidden');
            chatBox.scrollTop = chatBox.scrollHeight;
            
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: text, effort: effort})
                });
                const data = await res.json();
                status.classList.add('hidden');
                
                // Render AI Response
                chatBox.innerHTML += `<div class="bg-zinc-900/60 p-3.5 rounded-lg border border-zinc-800 max-w-[85%]"><p class="text-xs text-zinc-500 font-mono mb-1">AI Assistant</p><p class="text-sm text-zinc-300">${data.reply}</p></div>`;
            } catch {
                status.classList.add('hidden');
                chatBox.innerHTML += `<div class="text-xs text-red-400/80 font-mono p-1">[Lỗi]: Không thể kết nối với máy chủ hoặc hết hạn mức API.</div>`;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_interface():
    return HTML_TEMPLATE

@app.post("/chat")
async def chat_endpoint(payload: ChatPayload):
    if not OPENROUTER_API_KEY:
        return {"reply": "[Lỗi]: Chưa cấu hình OPENROUTER_API_KEY hệ thống."}
        
    url = "https://openrouter.ai"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": payload.prompt}],
        "provider": {"reasoning_effort": payload.effort}
    }
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                reply = result['choices']['message']['content']
                return {"reply": reply}
            else:
                return {"reply": f"Lỗi kết nối (Mã lỗi: {response.status_code})."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
