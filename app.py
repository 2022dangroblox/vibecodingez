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
    effort: str # 'low', 'medium', 'high', 'xhigh'

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>VibeCodingEz – Freemium AI Code</title>
    
    <!-- NHÚNG BIỂU TƯỢNG TÊN LỬA LÀM ẢNH ĐẠI DIỆN WEB -->
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://w3.org viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🚀</text></svg>">
    
    <script src="https://tailwindcss.com"></script>
    <link href="https://googleapis.com" rel="stylesheet">
    <style>
        * { font-family: 'Inter', sans-serif; }
        .font-mono, code, pre { font-family: 'JetBrains Mono', monospace !important; }

        body {
            background: radial-gradient(ellipse at 20% 20%, #0f0f17 0%, #07070c 100%);
            background-attachment: fixed;
        }

        .glass {
            background: rgba(18, 18, 24, 0.65);
            backdrop-filter: blur(24px);
            border: 1px solid rgba(255, 255, 255, 0.06);
        }

        .bubble-user {
            background: linear-gradient(145deg, #4f46e5, #7c3aed);
            box-shadow: 0 8px 20px rgba(124, 58, 237, 0.25);
        }

        .bubble-ai {
            background: rgba(28, 28, 34, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .loading-dots:after {
            content: '';
            animation: dots 1.5s steps(5, end) infinite;
        }
        @keyframes dots {
            0%, 20% { content: ' .'; }
            40% { content: ' . .'; }
            60% { content: ' . . .'; }
            80%, 100% { content: ''; }
        }

        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #3f3f46; border-radius: 8px; }
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between p-3 sm:p-4">

    <!-- Header – chỉ 1 badge Freemium -->
    <header class="max-w-4xl w-full mx-auto glass rounded-2xl p-3 sm:p-4 mb-4 flex items-center justify-between sticky top-3 z-20">
        <div class="flex items-center gap-3">
            <div class="w-9 h-9 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <span class="text-white font-bold text-lg">V</span>
            </div>
            <div>
                <h1 class="text-lg sm:text-xl font-bold text-white tracking-tight">VibeCodingEz</h1>
                <p class="text-[10px] text-zinc-500 font-mono">AI Code Assistant</p>
            </div>
        </div>
        <span class="px-3 py-1.5 rounded-lg bg-gradient-to-r from-indigo-500/10 to-purple-500/10 text-indigo-400 border border-indigo-500/30 text-xs font-mono tracking-wide">
            ⚡ FREEMIUM
        </span>
    </header>

    <!-- Chat workspace -->
    <main class="flex-1 max-w-4xl w-full mx-auto glass rounded-2xl p-3 sm:p-5 flex flex-col">
        <!-- Chat box – bắt đầu trống -->
        <div id="chat-box" class="flex-1 overflow-y-auto space-y-4 min-h-[420px] sm:min-h-[520px] mb-4 pr-1"></div>

        <!-- Trạng thái đang xử lý -->
        <div id="status" class="hidden glass rounded-xl p-3 mb-3 flex items-center gap-3">
            <div class="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
            <span class="text-xs text-zinc-400 font-mono loading-dots">Đang suy luận</span>
        </div>

        <!-- Thanh nhập liệu -->
        <div class="flex flex-col sm:flex-row gap-2 bg-zinc-900/70 p-2 border border-zinc-700/40 rounded-xl focus-within:border-indigo-500/50 transition-all">
            <input type="text" id="msg" placeholder="Nhập câu hỏi hoặc code..." class="flex-1 bg-transparent rounded-lg px-3 py-2.5 text-sm text-zinc-100 focus:outline-none placeholder:text-zinc-500" onkeypress="if(event.key==='Enter') send()">
            <div class="flex gap-2">
                <select id="effort" class="bg-zinc-800 border border-zinc-700 rounded-lg px-2 py-2 text-xs font-mono text-zinc-300 focus:outline-none cursor-pointer hover:border-zinc-500 transition-colors">
                    <option value="low">🟢 Low</option>
                    <option value="medium" selected>🟡 Medium</option>
                    <option value="high">🟠 High</option>
                    <option value="xhigh">🔴 xHigh</option>
                </select>
                <button onclick="send()" class="bg-indigo-500 hover:bg-indigo-600 text-white font-medium px-4 py-2 rounded-lg text-sm transition-colors shadow-lg shadow-indigo-500/20 cursor-pointer">
                    Gửi
                </button>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="text-center text-[10px] sm:text-xs text-zinc-600 font-mono mt-4">
        &copy; 2026 VibeCodingEz · Model: openai/gpt-oss-120b · Freemium
    </footer>

    <script>
        function formatReply(text) {
            let escaped = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            escaped = escaped.replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang, code) => {
                return `<pre class="bg-black/40 rounded-lg p-3 my-2 overflow-x-auto font-mono text-emerald-400"><code class="font-mono">${code.trim()}</code></pre>`;
            });
            escaped = escaped.replace(/`([^`]+)`/g, '<code class="bg-zinc-800 text-blue-300 px-1 py-0.5 rounded text-xs font-mono">$1</code>');
            escaped = escaped.replace(/\n/g, '<br>');
            return escaped;
        }

        async function send() {
            const msgInput = document.getElementById('msg');
            const effort = document.getElementById('effort').value;
            const chatBox = document.getElementById('chat-box');
            const status = document.getElementById('status');
            const text = msgInput.value.trim();
            if (!text) return;

            chatBox.innerHTML += `
                <div class="bubble-user p-3 sm:p-4 rounded-2xl max-w-[85%] ml-auto shadow-md">
                    <p class="text-xs text-white/70 font-mono mb-1">You · ${effort.toUpperCase()}</p>
                    <p class="text-sm text-white">${text}</p>
                </div>
            `;
            msgInput.value = '';
            msgInput.disabled = true;
            status.classList.remove('hidden');
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: text, effort: effort })
                });
                if (!res.ok) throw new Error(`HTTP \${res.status}`);
                const data = await res.json();

                status.classList.add('hidden');
                msgInput.disabled = false;
                chatBox.innerHTML += `
                    <div class="bubble-ai p-3 sm:p-4 rounded-2xl max-w-[85%] animate-fade-in">
                        <p class="text-xs text-zinc-500 font-mono mb-1">AI · \${effort.toUpperCase()}</p>
                        <div class="text-sm text-zinc-200 leading-relaxed font-sans">\${formatReply(data.reply)}</div>
                    </div>
                `;
            } catch (e) {
                status.classList.add('hidden');
                msgInput.disabled = false;
                chatBox.innerHTML += `
                    <div class="glass rounded-xl p-3 border-red-500/30 bg-red-500/5 max-w-[85%]">
                        <p class="text-xs text-red-400 font-mono">⚠️ Lỗi kết nối hoặc hệ thống đang bận.</p>
                    </div>
                `;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
            msgInput.focus();
        }

        window.addEventListener('load', () => document.getElementById('msg').focus());
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
                return {"reply": f"Lỗi kết nối từ OpenRouter API (Mã lỗi: {response.status_code})."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
