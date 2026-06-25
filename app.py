import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os

app = FastAPI()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

class ChatPayload(BaseModel):
    prompt: str
    effort: str  # 'low', 'medium', 'high', 'xhigh'

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>VibeCodingEz – Freemium AI Code</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🚀</text></svg>">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Inter', sans-serif; }
        .font-mono, code, pre { font-family: 'JetBrains Mono', monospace !important; }

        body {
            background: #07070c;
            background-image:
                radial-gradient(ellipse at 15% 10%, rgba(99,102,241,0.07) 0%, transparent 50%),
                radial-gradient(ellipse at 85% 90%, rgba(168,85,247,0.05) 0%, transparent 50%);
            background-attachment: fixed;
        }

        .glass {
            background: rgba(18, 18, 24, 0.6);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid rgba(255,255,255,0.06);
        }

        .bubble-user {
            background: linear-gradient(145deg, #4f46e5, #7c3aed);
            box-shadow: 0 8px 24px rgba(124,58,237,0.2);
        }

        .bubble-ai {
            background: rgba(28, 28, 34, 0.85);
            border: 1px solid rgba(255,255,255,0.05);
        }

        @keyframes fadeSlideIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in { animation: fadeSlideIn 0.35s ease-out; }

        .loading-dots span {
            display: inline-block;
            animation: dotPulse 1.4s ease-in-out infinite;
        }
        .loading-dots span:nth-child(2) { animation-delay: 0.2s; }
        .loading-dots span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes dotPulse {
            0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
            40% { opacity: 1; transform: scale(1); }
        }

        .code-block { position: relative; }
        .code-block .copy-btn {
            position: absolute; top: 6px; right: 6px;
            opacity: 0; transition: opacity 0.2s;
        }
        .code-block:hover .copy-btn { opacity: 1; }

        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #3f3f46; border-radius: 8px; }

        #msg:focus { outline: none; }

        .quick-btn { transition: all 0.2s; }
        .quick-btn:hover {
            border-color: rgba(99,102,241,0.4);
            color: #c7d2fe;
            background: rgba(99,102,241,0.08);
        }
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between p-3 sm:p-4">

    <header class="max-w-4xl w-full mx-auto glass rounded-2xl p-3 sm:p-4 mb-4 flex items-center justify-between sticky top-3 z-20">
        <div class="flex items-center gap-3">
            <div class="w-9 h-9 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <span class="text-white font-extrabold text-lg">V</span>
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

    <main class="flex-1 max-w-4xl w-full mx-auto glass rounded-2xl p-3 sm:p-5 flex flex-col">
        <div id="chat-box" class="flex-1 overflow-y-auto space-y-4 min-h-[420px] sm:min-h-[520px] mb-4 pr-1">
            <div id="welcome" class="h-full flex flex-col items-center justify-center text-center gap-4 py-10">
                <div class="w-16 h-16 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 rounded-2xl flex items-center justify-center border border-indigo-500/20">
                    <span class="text-3xl">🚀</span>
                </div>
                <div>
                    <h2 class="text-xl font-bold text-white mb-2">Xin chào! Mình là VibeCodingEz</h2>
                    <p class="text-sm text-zinc-500 max-w-md">Hỏi bất cứ gì về code — debug, giải thích, viết mới — mình sẽ giúp bạn.</p>
                </div>
                <div class="flex flex-wrap justify-center gap-2 mt-2">
                    <button onclick="quickSend('Viết hàm sắp xếp mảng bằng Python')" class="quick-btn px-3 py-1.5 rounded-lg bg-zinc-800/60 border border-zinc-700/50 text-xs text-zinc-400 cursor-pointer">Sắp xếp mảng Python</button>
                    <button onclick="quickSend('Giải thích closure trong JavaScript')" class="quick-btn px-3 py-1.5 rounded-lg bg-zinc-800/60 border border-zinc-700/50 text-xs text-zinc-400 cursor-pointer">Closure JS</button>
                    <button onclick="quickSend('Tạo REST API bằng FastAPI')" class="quick-btn px-3 py-1.5 rounded-lg bg-zinc-800/60 border border-zinc-700/50 text-xs text-zinc-400 cursor-pointer">REST API FastAPI</button>
                    <button onclick="quickSend('Tạo component React đếm số')" class="quick-btn px-3 py-1.5 rounded-lg bg-zinc-800/60 border border-zinc-700/50 text-xs text-zinc-400 cursor-pointer">React Counter</button>
                </div>
            </div>
        </div>

        <div id="status" class="hidden glass rounded-xl p-3 mb-3 flex items-center gap-3">
            <div class="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
            <span class="text-xs text-zinc-400 font-mono loading-dots">Đang suy luận<span>.</span><span>.</span><span>.</span></span>
        </div>

        <div class="flex flex-col sm:flex-row gap-2 bg-zinc-900/70 p-2 border border-zinc-700/40 rounded-xl focus-within:border-indigo-500/50 transition-all">
            <input type="text" id="msg" placeholder="Nhập câu hỏi hoặc code..." class="flex-1 bg-transparent rounded-lg px-3 py-2.5 text-sm text-zinc-100 placeholder:text-zinc-500" onkeypress="if(event.key==='Enter')send()">
            <div class="flex gap-2">
                <select id="effort" class="bg-zinc-800 border border-zinc-700 rounded-lg px-2 py-2 text-xs font-mono text-zinc-300 cursor-pointer hover:border-zinc-500 transition-colors">
                    <option value="low">🟢 Low</option>
                    <option value="medium" selected>🟡 Medium</option>
                    <option value="high">🟠 High</option>
                    <option value="xhigh">🔴 xHigh</option>
                </select>
                <button onclick="send()" id="send-btn" class="bg-indigo-500 hover:bg-indigo-600 active:scale-95 text-white font-medium px-5 py-2 rounded-lg text-sm transition-all shadow-lg shadow-indigo-500/20 cursor-pointer">
                    Gửi
                </button>
            </div>
        </div>
    </main>

    <footer class="text-center text-[10px] sm:text-xs text-zinc-600 font-mono mt-4">
        &copy; 2025 VibeCodingEz &middot; openai/gpt-oss-120b &middot; Freemium
    </footer>

    <script>
        function formatReply(text) {
            var s = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

            s = s.replace(/```(\w+)?\n([\s\S]*?)```/g, function(_, lang, code) {
                var label = lang || 'code';
                var id = 'cb_' + Math.random().toString(36).substr(2, 9);
                return '<div class="code-block my-3 rounded-lg overflow-hidden border border-zinc-800">'
                    + '<div class="flex items-center justify-between bg-zinc-800/80 px-3 py-1.5">'
                    + '<span class="text-[10px] text-zinc-500 font-mono uppercase">' + label + '</span>'
                    + '<button onclick="copyCode(\'' + id + '\')" class="copy-btn text-[10px] text-zinc-400 hover:text-zinc-100 transition-colors cursor-pointer px-2 py-0.5 rounded bg-zinc-700/60 hover:bg-zinc-600/60">Copy</button>'
                    + '</div>'
                    + '<pre class="bg-black/50 p-3 overflow-x-auto"><code id="' + id + '" class="font-mono text-sm text-emerald-400">' + code.trim() + '</code></pre>'
                    + '</div>';
            });

            s = s.replace(/`([^`]+)`/g, '<code class="bg-zinc-800 text-blue-300 px-1.5 py-0.5 rounded text-xs font-mono">$1</code>');
            s = s.replace(/\*\*([^*]+)\*\*/g, '<strong class="text-white font-semibold">$1</strong>');
            s = s.replace(/\n/g, '<br>');
            return s;
        }

        function copyCode(id) {
            var el = document.getElementById(id);
            if (!el) return;
            navigator.clipboard.writeText(el.textContent).then(function() {
                var btn = el.closest('.code-block').querySelector('.copy-btn');
                btn.textContent = 'Done!';
                btn.classList.add('text-emerald-400');
                setTimeout(function() {
                    btn.textContent = 'Copy';
                    btn.classList.remove('text-emerald-400');
                }, 1500);
            });
        }

        function quickSend(text) {
            document.getElementById('msg').value = text;
            send();
        }

        async function send() {
            var msgInput = document.getElementById('msg');
            var effort = document.getElementById('effort').value;
            var chatBox = document.getElementById('chat-box');
            var status = document.getElementById('status');
            var sendBtn = document.getElementById('send-btn');
            var welcome = document.getElementById('welcome');
            var text = msgInput.value.trim();
            if (!text) return;

            if (welcome) welcome.remove();

            var safeText = text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
            chatBox.innerHTML += '<div class="bubble-user p-3 sm:p-4 rounded-2xl max-w-[85%] ml-auto shadow-md animate-fade-in">'
                + '<p class="text-[10px] text-white/60 font-mono mb-1">You &middot; ' + effort.toUpperCase() + '</p>'
                + '<p class="text-sm text-white leading-relaxed">' + safeText + '</p>'
                + '</div>';

            msgInput.value = '';
            msgInput.disabled = true;
            sendBtn.disabled = true;
            sendBtn.classList.add('opacity-50');
            status.classList.remove('hidden');
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                var res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: text, effort: effort })
                });
                if (!res.ok) throw new Error('HTTP ' + res.status);
                var data = await res.json();

                status.classList.add('hidden');
                msgInput.disabled = false;
                sendBtn.disabled = false;
                sendBtn.classList.remove('opacity-50');

                chatBox.innerHTML += '<div class="bubble-ai p-3 sm:p-4 rounded-2xl max-w-[85%] animate-fade-in">'
                    + '<p class="text-[10px] text-zinc-500 font-mono mb-2">AI &middot; ' + effort.toUpperCase() + '</p>'
                    + '<div class="text-sm text-zinc-200 leading-relaxed">' + formatReply(data.reply) + '</div>'
                    + '</div>';
            } catch (e) {
                status.classList.add('hidden');
                msgInput.disabled = false;
                sendBtn.disabled = false;
                sendBtn.classList.remove('opacity-50');
                chatBox.innerHTML += '<div class="glass rounded-xl p-3 border border-red-500/30 bg-red-500/5 max-w-[85%] animate-fade-in">'
                    + '<p class="text-xs text-red-400 font-mono">&#9888;&#65039; Lỗi kết nối hoặc hệ thống đang bận. Vui lòng thử lại.</p>'
                    + '</div>';
            }
            chatBox.scrollTop = chatBox.scrollHeight;
            msgInput.focus();
        }

        window.addEventListener('load', function() {
            document.getElementById('msg').focus();
        });
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
        return {"reply": "[Lỗi] Chưa cấu hình biến môi trường OPENROUTER_API_KEY."}

    # SỬA 1: URL đúng endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://vibecodingez.onrender.com",
        "X-Title": "VibeCodingEz"
    }

    # Giữ nguyên model của bạn
    data = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "system", "content": "Bạn là VibeCodingEz, trợ lý lập trình AI. Trả lời rõ ràng, dùng Markdown cho code block."},
            {"role": "user", "content": payload.prompt}
        ],
        "provider": {"reasoning_effort": payload.effort}
    }

    try:
        # SỬA 2: timeout hợp lệ
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            response = await client.post(url, headers=headers, json=data)

            if response.status_code == 200:
                result = response.json()
                # SỬA 3: choices là mảng -> [0]
                reply = result["choices"][0]["message"]["content"]
                return {"reply": reply}
            else:
                return {"reply": f"Lỗi từ OpenRouter (HTTP {response.status_code}): {response.text[:300]}"}

    except httpx.TimeoutException:
        return {"reply": "[Timeout] Model phản hồi quá chậm. Thử lại hoặc giảm effort."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
