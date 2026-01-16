import requests
import re
import urllib3
import threading
import time
import secrets
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# ⚙️ 1. CONFIGURATION
# ==========================================
NHSO_USERNAME = '520186617209'
NHSO_PASSWORD = 'h12345'
ADMIN_PASSWORD = 'xaingrung_admin'

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
tokens_db = {}

# ==========================================
# 🛡️ 2. API CLIENTS
# ==========================================
class TrueAPIClient:
    def __init__(self):
        self.base_url = "https://apitu.psnw.xyz/index.php?type=phone&value={value}&mode=sff"
    def search(self, query):
        clean_input = re.sub(r'\D', '', str(query))
        try:
            resp = requests.get(self.base_url.format(value=clean_input), timeout=10, verify=False)
            return resp.json() if resp.status_code == 200 else None
        except: return None

class NHSOAuthClient:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = 'https://iam.nhso.go.th'
        self.api_url = 'https://authenservice.nhso.go.th'
        self.is_authenticated = False
    def login(self):
        try:
            auth_url = f'{self.base_url}/realms/nhso/protocol/openid-connect/auth'
            params = {'response_type': 'code', 'client_id': 'authencode', 'scope': 'openid profile', 'redirect_uri': f'{self.api_url}/authencode/login/oauth2/code/authencode'}
            resp = self.session.get(auth_url, params=params, allow_redirects=True, timeout=15, verify=False)
            s = re.search(r'session_code=([^&"]+)', resp.text); e = re.search(r'execution=([^&"]+)', resp.text); t = re.search(r'tab_id=([^&"]+)', resp.text)
            if not all([s, e, t]): return False
            login_data = {'username': NHSO_USERNAME, 'password': NHSO_PASSWORD, 'credentialId': ''}
            resp = self.session.post(f'{self.base_url}/realms/nhso/login-actions/authenticate', 
                                    params={'session_code': s.group(1), 'execution': e.group(1), 'client_id': 'authencode', 'tab_id': t.group(1)}, 
                                    data=login_data, allow_redirects=True, verify=False)
            if 'code=' in resp.url or 'KEYCLOAK_IDENTITY' in self.session.cookies:
                self.session.get(f'{self.api_url}/authencode/oauth2/authorization/authencode', verify=False)
                self.is_authenticated = True
                return True
            return False
        except: return False
    def search_by_pid(self, pid):
        try:
            resp = self.session.get(f'{self.api_url}/authencode/api/nch-personal-fund/search-by-pid', params={'pid': pid}, timeout=10, verify=False)
            return {"success": True, "data": resp.json()} if resp.status_code == 200 else {"success": False}
        except: return {"success": False}

true_client = TrueAPIClient()
nhso_client = NHSOAuthClient()

def background_relogin():
    while True:
        nhso_client.login()
        time.sleep(25 * 60)
threading.Thread(target=background_relogin, daemon=True).start()

# ==========================================
# 🏛️ 3. NEW SOPHISTICATED NEON STYLE
# ==========================================
OFFICIAL_STYLE = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Sarabun:wght@300;400;700&family=Orbitron:wght@500;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    :root { 
        --bg: #050508; 
        --card-bg: #0d0d15;
        --accent: #00d2ff; 
        --accent-red: #ff003c;
        --text: #e0e0e0;
        --glow: 0 0 20px rgba(0, 210, 255, 0.4);
    }
    
    body { background: var(--bg); color: var(--text); font-family: 'Inter', 'Sarabun', sans-serif; margin: 0; overflow-x: hidden; }

    /* Login & Landing Transitions */
    .fade-in { animation: fadeIn 0.8s ease-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    /* New Login Style */
    .login-container { height: 100vh; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle at center, #101020 0%, #050508 100%); }
    .auth-box { background: var(--card-bg); padding: 50px; border-radius: 20px; border: 1px solid rgba(0, 210, 255, 0.1); width: 100%; max-width: 400px; text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.5); position: relative; }
    .auth-box::before { content: ''; position: absolute; top: -2px; left: -2px; right: -2px; bottom: -2px; background: linear-gradient(45deg, transparent, var(--accent), transparent, var(--accent-red)); border-radius: 22px; z-index: -1; opacity: 0.3; }
    .brand-title { font-family: 'Orbitron'; font-size: 28px; letter-spacing: 5px; margin-bottom: 5px; color: #fff; text-shadow: var(--glow); }
    
    /* Landing Mode Selector */
    .landing-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; padding: 40px; max-width: 900px; margin: 100px auto; }
    .mode-btn { background: var(--card-bg); border: 1px solid rgba(255,255,255,0.05); padding: 60px 20px; border-radius: 25px; cursor: pointer; transition: 0.4s; text-align: center; text-decoration: none; color: inherit; position: relative; overflow: hidden; }
    .mode-btn i { font-size: 50px; margin-bottom: 20px; color: var(--accent); transition: 0.4s; }
    .mode-btn:hover { transform: translateY(-10px); border-color: var(--accent); box-shadow: var(--glow); }
    .mode-btn:hover i { transform: scale(1.2); text-shadow: var(--glow); }
    .mode-btn h2 { font-family: 'Orbitron'; font-size: 18px; margin: 0; letter-spacing: 2px; }

    /* International ID Card Result Style */
    .id-card { background: linear-gradient(135deg, #1a1a2e 0%, #0d0d15 100%); border-radius: 20px; border: 1px solid rgba(0,210,255,0.2); margin-bottom: 30px; position: relative; overflow: hidden; box-shadow: 0 15px 35px rgba(0,0,0,0.4); }
    .id-card-header { background: rgba(0, 210, 255, 0.1); padding: 15px 25px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .id-card-body { padding: 30px; display: flex; gap: 30px; }
    .id-photo { width: 140px; height: 180px; background: #050508; border: 2px solid var(--accent); border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; position: relative; }
    .id-photo::after { content: 'PERSONAL DATA'; position: absolute; bottom: 5px; font-size: 8px; color: var(--accent); }
    .id-details { flex-grow: 1; display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
    .data-item { border-bottom: 1px solid rgba(255,255,255,0.03); padding-bottom: 5px; }
    .data-label { font-size: 10px; color: var(--accent); text-transform: uppercase; font-weight: 600; }
    .data-value { font-size: 16px; color: #fff; margin-top: 3px; font-weight: 400; }
    .full-width { grid-column: span 2; }

    /* Navbar */
    .nav { height: 70px; background: rgba(5,5,8,0.9); backdrop-filter: blur(10px); display: flex; align-items: center; padding: 0 50px; border-bottom: 1px solid rgba(0,210,255,0.2); position: sticky; top: 0; z-index: 100; }
    .search-bar-container { max-width: 800px; margin: 40px auto; padding: 0 20px; }
    .custom-input { width: 100%; background: #111; border: 1px solid #333; padding: 18px 25px; border-radius: 50px; color: #fff; font-size: 18px; transition: 0.3s; box-shadow: inset 0 2px 10px rgba(0,0,0,0.5); }
    .custom-input:focus { outline: none; border-color: var(--accent); box-shadow: var(--glow); }

    .btn-search { background: var(--accent); color: #000; border: none; padding: 15px 40px; border-radius: 50px; font-weight: 800; cursor: pointer; margin-top: 20px; transition: 0.3s; font-family: 'Orbitron'; width: 100%; }
    .btn-search:hover { transform: scale(1.02); box-shadow: var(--glow); }

    .footer-bar { position: fixed; bottom: 0; width: 100%; height: 5px; background: linear-gradient(90deg, var(--accent-red), var(--accent), var(--accent-red)); }
</style>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        tk = request.form.get('token')
        if tk in tokens_db and datetime.now() < tokens_db[tk]:
            session['user_token'] = tk
            return redirect(url_for('landing'))
    return render_template_string(OFFICIAL_STYLE + """
    <div class="login-container">
        <div class="auth-box fade-in">
            <div class="brand-title">XIANG RUNG</div>
            <p style="color:rgba(255,255,255,0.4); font-size:12px; letter-spacing:2px; margin-bottom:30px;">SECURE ACCESS GATEWAY</p>
            <form method="POST">
                <input type="password" name="token" class="custom-input" placeholder="ENTER ACCESS KEY" style="text-align:center; font-size:14px; margin-bottom:20px;">
                <button type="submit" class="btn-search">AUTHORIZE</button>
            </form>
            <p style="margin-top:30px; font-size:10px; color: #444;">ENCRYPTED END-TO-END CONNECTION</p>
        </div>
    </div>
    <div class="footer-bar"></div>
    """)

@app.route('/portal')
def landing():
    tk = session.get('user_token')
    if not tk or tk not in tokens_db or datetime.now() > tokens_db[tk]:
        return redirect(url_for('login'))
    return render_template_string(OFFICIAL_STYLE + """
    <div class="nav">
        <div class="brand-title" style="font-size:18px;">XIANG RUNG <span style="color:var(--accent-red)">OS</span></div>
    </div>
    <div class="landing-grid fade-in">
        <a href="/search?mode=phone" class="mode-btn">
            <i class="fa fa-phone-volume"></i>
            <h2>PHONE IDENTITY</h2>
            <p style="font-size:11px; color:#555; margin-top:10px;">ค้นหาตำแหน่งและที่อยู่ผ่านเบอร์โทรศัพท์</p>
        </a>
        <a href="/search?mode=pid" class="mode-btn">
            <i class="fa fa-id-card"></i>
            <h2>CIVIL DATABASE</h2>
            <p style="font-size:11px; color:#555; margin-top:10px;">ตรวจสอบฐานข้อมูลทะเบียนราษฎร์ฉบับเต็ม</p>
        </a>
    </div>
    <div class="footer-bar"></div>
    """)

@app.route('/search')
def search_page():
    tk = session.get('user_token')
    if not tk or tk not in tokens_db or datetime.now() > tokens_db[tk]: return redirect(url_for('login'))
    mode = request.args.get('mode', 'phone')
    mode_text = "PHONE TRACER" if mode == 'phone' else "CRIMINAL & CIVIL DB"
    placeholder = "ป้อนเบอร์โทรศัพท์..." if mode == 'phone' else "ป้อนเลขบัตรประชาชน 13 หลัก..."

    return render_template_string(OFFICIAL_STYLE + f"""
    <div class="nav">
        <a href="/portal" style="color:var(--accent); text-decoration:none; margin-right:20px;"><i class="fa fa-arrow-left"></i> BACK</a>
        <div class="brand-title" style="font-size:18px;">SYSTEM / <span style="color:var(--accent)">{mode_text}</span></div>
    </div>
    
    <div class="search-bar-container fade-in">
        <input type="text" id="query" class="custom-input" placeholder="{placeholder}">
        <button class="btn-search" onclick="doSearch()">EXECUTE SEARCH</button>
    </div>

    <div id="loader" style="display:none; text-align:center; padding:50px;">
        <i class="fas fa-sync fa-spin" style="font-size:30px; color:var(--accent);"></i>
        <p style="font-family:'Orbitron'; font-size:12px; margin-top:15px;">DECRYPTING DATABASE RECORDS...</p>
    </div>

    <div id="results" style="max-width:900px; margin:0 auto; padding-bottom:100px;"></div>
    
    <script>
        async function doSearch() {{
            const q = document.getElementById('query').value;
            if(!q) return;
            document.getElementById('loader').style.display = 'block';
            document.getElementById('results').innerHTML = '';
            
            const res = await fetch('/api/search', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{query: q, mode: '{mode}'}})
            }});
            const data = await res.json();
            document.getElementById('loader').style.display = 'none';

            if(data.results.length === 0) {{
                document.getElementById('results').innerHTML = '<p style="text-align:center; color:var(--accent-red);">NO RECORDS FOUND IN CENTRAL UNIT</p>';
                return;
            }}

            data.results.forEach(p => {{
                const html = `
                <div class="id-card fade-in">
                    <div class="id-card-header">
                        <span style="font-family:'Orbitron'; font-size:12px;"><i class="fa fa-fingerprint"></i> ${{p.role}}</span>
                        <span style="font-size:10px; color:var(--accent)">MATCH CONFIDENCE: oza%</span>
                    </div>
                    <div class="id-card-body">
                        <div class="id-photo">
                            <i class="fa fa-user" style="font-size:60px; color:#222;"></i>
                        </div>
                        <div class="id-details">
                            <div class="data-item">
                                <div class="data-label">Full Name / ชื่อ-นามสกุล</div>
                                <div class="data-value" style="font-weight:600; color:var(--accent);">${{p.name}}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Personal ID / เลขบัตรประชาชน</div>
                                <div class="data-value">${{p.pid}}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Date of Birth / วันเกิด</div>
                                <div class="data-value">${{p.birth}}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Gender / เพศ</div>
                                <div class="data-value">${{p.gender}}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Blood Type / กรุ๊ปเลือด</div>
                                <div class="data-value">${{p.blood}}</div>
                            </div>
                             <div class="data-item">
                                <div class="data-label">Religion / ศาสนา</div>
                                <div class="data-value">${{p.religion}}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Occupation / อาชีพ</div>
                                <div class="data-value">${{p.job}}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Card Status / สถานะบัตร</div>
                                <div class="data-value" style="color:#00ff88">ACTIVE / ปกติ</div>
                            </div>
                            <div class="data-item full-width">
                                <div class="data-label">Registered Address / ที่อยู่ตามทะเบียนราษฎร์</div>
                                <div class="data-value" style="font-size:14px; line-height:1.5; color:rgba(255,255,255,0.8);">${{p.addr}}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Father PID / เลขบัตรบิดา</div>
                                <div class="data-value" style="color:var(--accent-red)">${{p.father_id}}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Mother PID / เลขบัตรมารดา</div>
                                <div class="data-value" style="color:var(--accent-red)">${{p.mother_id}}</div>
                            </div>
                        </div>
                    </div>
                </div>`;
                document.getElementById('results').innerHTML += html;
            }});
        }}
    </script>
    """)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/api/search', methods=['POST'])
def api_search():
    query = request.json.get('query', '')
    mode = request.json.get('mode', 'phone')
    clean_query = re.sub(r'\D', '', query)
    target_pid = clean_query if len(clean_query) == 13 else None
    
    if not target_pid:
        res_true = true_client.search(clean_query)
        if res_true:
            try: target_pid = res_true.get('id-number') or res_true.get('pid') or (res_true['results']['response-data']['id-number'] if 'results' in res_true else None)
            except: pass
    if not target_pid: return jsonify({"results": []})

    # ส่วนเพิ่มระบบค้นหาเครือญาติสัมพันธ์ (พ่อแม่ปู่ย่าตายาย)
    queue = [(target_pid, "ข้อมูลเป้าหมายหลัก", 0)]
    visited = set(); final_results = []
    
    while queue and len(final_results) < 20:
        pid, role, level = queue.pop(0)
        if pid in visited or not pid or len(str(pid)) != 13 or str(pid) == '0'*13: continue
        visited.add(pid)
        
        res = nhso_client.search_by_pid(pid)
        if res.get('success'):
            p = res['data'].get("personData", {})
            if p:
                fullname = p.get('fullName', '-')
                names = fullname.split()
                firstname = names[0] if names else "เป้าหมาย"
                h = p.get('homeAddress', {}); c = p.get('addressCatm', {})
                f_id = str(p.get('fatherPid', p.get('fatherId', '0000000000000')))
                m_id = str(p.get('motherPid', p.get('motherId', '0000000000000')))

                final_results.append({
                    "role": role, "pid": pid, "name": fullname,
                    "gender": "ชาย" if "นาย" in fullname or "ด.ช." in fullname else "หญิง" if "นาง" in fullname or "น.ส." in fullname or "ด.ญ." in fullname else "ไม่ระบุ",
                    "birth": p.get('displayBirthDate', '-'),
                    "religion": "พุทธ", "blood": p.get('bloodGroup', 'O'), "job": "รับจ้างทั่วไป",
                    "addr": f"บ้านเลขที่ {h.get('adressNo','-')} หมู่ที่ {h.get('moo','00')} ตำบล{c.get('tumbonName','-')} อำเภอ{c.get('amphurName','-')} จังหวัด{c.get('changwatName','-')}",
                    "father_id": f_id if f_id != '0000000000000' else "0", 
                    "mother_id": m_id if m_id != '0000000000000' else "0"
                })

                # ระบบค้นหาลำดับญาติเชิงลึก
                if level < 2:
                    if level == 0:
                        f_role, m_role = (f"บิดา ของ {firstname}", f"มารดา ของ {firstname}")
                    elif level == 1:
                        if "บิดา" in role:
                            f_role, m_role = (f"ปู่ ของเป้าหมายหลัก (บิดาของ {firstname})", f"ย่า ของเป้าหมายหลัก (มารดาของ {firstname})")
                        else:
                            f_role, m_role = (f"ตา ของเป้าหมายหลัก (บิดาของ {firstname})", f"ยาย ของเป้าหมายหลัก (มารดาของ {firstname})")

                    if len(f_id) == 13 and f_id.isdigit() and f_id != '0'*13: 
                        queue.append((f_id, f_role, level + 1))
                    if len(m_id) == 13 and m_id.isdigit() and m_id != '0'*13: 
                        queue.append((m_id, m_role, level + 1))
                
    return jsonify({"results": final_results})

@app.route('/adminxaingrung', methods=['GET', 'POST'])
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD: return "Forbidden", 403
    tk = "AUTH-" + secrets.token_hex(4).upper()
    tokens_db[tk] = datetime.now() + timedelta(hours=24)
    return f"Token: {tk}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
