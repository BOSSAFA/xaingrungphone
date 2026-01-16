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
            
            print(f">>> DEBUG LOGIN: {resp.status_code} | {resp.url}")

            if 'code=' in resp.url or 'KEYCLOAK_IDENTITY' in self.session.cookies:
                self.session.get(f'{self.api_url}/authencode/oauth2/authorization/authencode', verify=False)
                self.is_authenticated = True
                return True
            return False
        except: return False
    def search_by_pid(self, pid):
        try:
            resp = self.session.get(f'{self.api_url}/authencode/api/nch-personal-fund/search-by-pid', params={'pid': pid}, timeout=10, verify=False)
            print(f">>> DEBUG NHSO RESULT: {resp.status_code} | PID: {pid}")
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
# 🏛️ 3. STYLE & UI
# ==========================================
OFFICIAL_STYLE = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Sarabun:wght@300;400;700&family=Orbitron:wght@500;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    :root { 
        --bg: #050508; --card-bg: #0d0d15; --accent: #00d2ff; --accent-red: #ff003c; --text: #e0e0e0; --glow: 0 0 20px rgba(0, 210, 255, 0.4);
    }
    body { background: var(--bg); color: var(--text); font-family: 'Inter', 'Sarabun', sans-serif; margin: 0; }
    .fade-in { animation: fadeIn 0.8s ease-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .login-container { height: 100vh; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle at center, #101020 0%, #050508 100%); }
    .auth-box { background: var(--card-bg); padding: 50px; border-radius: 20px; border: 1px solid rgba(0, 210, 255, 0.1); width: 100%; max-width: 400px; text-align: center; }
    .brand-title { font-family: 'Orbitron'; font-size: 28px; letter-spacing: 5px; color: #fff; text-shadow: var(--glow); }
    .landing-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; padding: 40px; max-width: 900px; margin: 100px auto; }
    .mode-btn { background: var(--card-bg); border: 1px solid rgba(255,255,255,0.05); padding: 60px 20px; border-radius: 25px; cursor: pointer; text-align: center; text-decoration: none; color: inherit; transition: 0.4s; }
    .mode-btn:hover { transform: translateY(-10px); border-color: var(--accent); box-shadow: var(--glow); }
    .id-card { background: linear-gradient(135deg, #1a1a2e 0%, #0d0d15 100%); border-radius: 20px; border: 1px solid rgba(0,210,255,0.2); margin-bottom: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.4); overflow: hidden; }
    .id-card-header { background: rgba(0, 210, 255, 0.1); padding: 15px 25px; display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .id-card-body { padding: 30px; display: flex; gap: 30px; }
    .id-photo { width: 140px; height: 180px; background: #050508; border: 2px solid var(--accent); border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
    .id-details { flex-grow: 1; display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
    .data-item { border-bottom: 1px solid rgba(255,255,255,0.03); }
    .data-label { font-size: 10px; color: var(--accent); text-transform: uppercase; font-weight: 600; }
    .data-value { font-size: 16px; color: #fff; margin-top: 3px; }
    .full-width { grid-column: span 2; }
    .nav { height: 70px; background: rgba(5,5,8,0.9); display: flex; align-items: center; padding: 0 50px; border-bottom: 1px solid rgba(0,210,255,0.2); }
    .custom-input { width: 100%; background: #111; border: 1px solid #333; padding: 18px 25px; border-radius: 50px; color: #fff; font-size: 18px; }
    .btn-search { background: var(--accent); color: #000; border: none; padding: 15px 40px; border-radius: 50px; font-weight: 800; cursor: pointer; width: 100%; font-family: 'Orbitron'; }
    .footer-bar { position: fixed; bottom: 0; width: 100%; height: 5px; background: linear-gradient(90deg, var(--accent-red), var(--accent), var(--accent-red)); }
</style>
"""

# ==========================================
# 🌐 4. ROUTES
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        tk = request.form.get('token')
        if tk in tokens_db and datetime.now() < tokens_db[tk]:
            session['user_token'] = tk
            return redirect(url_for('landing'))
    return render_template_string(OFFICIAL_STYLE + """
    <div class="login-container"><div class="auth-box fade-in"><div class="brand-title">XIANG RUNG</div>
    <form method="POST"><input type="password" name="token" class="custom-input" placeholder="ENTER ACCESS KEY" style="text-align:center; margin: 20px 0;"><button type="submit" class="btn-search">AUTHORIZE</button></form></div></div>
    """)

@app.route('/portal')
def landing():
    tk = session.get('user_token')
    if not tk or tk not in tokens_db or datetime.now() > tokens_db[tk]: return redirect(url_for('login'))
    return render_template_string(OFFICIAL_STYLE + """
    <div class="nav"><div class="brand-title" style="font-size:18px;">XIANG RUNG <span style="color:var(--accent-red)">OS</span></div></div>
    <div class="landing-grid fade-in">
        <a href="/search?mode=phone" class="mode-btn"><i class="fa fa-phone-volume" style="font-size:40px;"></i><h2>PHONE IDENTITY</h2></a>
        <a href="/search?mode=pid" class="mode-btn"><i class="fa fa-id-card" style="font-size:40px;"></i><h2>CIVIL DATABASE</h2></a>
    </div>
    """)

@app.route('/search')
def search_page():
    tk = session.get('user_token')
    if not tk or tk not in tokens_db or datetime.now() > tokens_db[tk]: return redirect(url_for('login'))
    mode = request.args.get('mode', 'phone')
    return render_template_string(OFFICIAL_STYLE + f"""
    <div class="nav"><a href="/portal" style="color:var(--accent); text-decoration:none;">BACK</a></div>
    <div style="max-width:800px; margin: 40px auto; padding: 0 20px;">
        <input type="text" id="query" class="custom-input" placeholder="Search...">
        <button class="btn-search" onclick="doSearch()" style="margin-top:20px;">EXECUTE SEARCH</button>
    </div>
    <div id="results" style="max-width:900px; margin:0 auto;"></div>
    <script>
        async function doSearch() {{
            const q = document.getElementById('query').value;
            const res = await fetch('/api/search', {{method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{query: q, mode: '{mode}'}})}});
            const data = await res.json();
            document.getElementById('results').innerHTML = '';
            data.results.forEach(p => {{
                document.getElementById('results').innerHTML += `
                <div class="id-card fade-in">
                    <div class="id-card-header"><span>${{p.role}}</span></div>
                    <div class="id-card-body">
                        <div class="id-photo"><i class="fa fa-user" style="font-size:60px;"></i></div>
                        <div class="id-details">
                            <div class="data-item"><div class="data-label">Name</div><div class="data-value">${{p.name}}</div></div>
                            <div class="data-item"><div class="data-label">PID</div><div class="data-value">${{p.pid}}</div></div>
                            <div class="data-item"><div class="data-label">DOB</div><div class="data-value">${{p.birth}}</div></div>
                            <div class="data-item"><div class="data-label">Gender</div><div class="data-value">${{p.gender}}</div></div>
                            <div class="data-item full-width"><div class="data-label">Address</div><div class="data-value">${{p.addr}}</div></div>
                            <div class="data-item full-width"><div class="data-label">Father Info</div><div class="data-value" style="color:var(--accent)">${{p.father_id}}</div></div>
                            <div class="data-item full-width"><div class="data-label">Mother Info</div><div class="data-value" style="color:var(--accent)">${{p.mother_id}}</div></div>
                        </div>
                    </div>
                </div>`;
            }});
        }}
    </script>
    """)

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

    final_results = []
    res_target = nhso_client.search_by_pid(target_pid)
    if res_target.get('success'):
        p = res_target['data'].get("personData", {})
        if p:
            h = p.get('homeAddress', {}); c = p.get('addressCatm', {})
            f_id = str(p.get('fatherPid', p.get('fatherId', '0')))
            m_id = str(p.get('motherPid', p.get('motherId', '0')))
            
            # --- ดึงชื่อพ่อแม่แบบป้องกันโดนแบน ---
            f_name = "ไม่ทราบชื่อ"; m_name = "ไม่ทราบชื่อ"
            if len(f_id) == 13 and f_id != '0000000000000':
                time.sleep(0.5)
                rf = nhso_client.search_by_pid(f_id)
                if rf.get('success'): f_name = rf['data'].get("personData", {}).get('fullName', f_id)
            
            if len(m_id) == 13 and m_id != '0000000000000':
                time.sleep(0.5)
                rm = nhso_client.search_by_pid(m_id)
                if rm.get('success'): m_name = rm['data'].get("personData", {}).get('fullName', m_id)

            final_results.append({
                "role": "เป้าหมายหลัก", "pid": target_pid, "name": p.get('fullName', '-'),
                "gender": "ชาย" if "นาย" in p.get('fullName','') else "หญิง", "birth": p.get('displayBirthDate', '-'),
                "addr": f"บ้านเลขที่ {h.get('adressNo','-')} หมู่ {h.get('moo','-')} ตำบล{c.get('tumbonName','-')} อำเภอ{c.get('amphurName','-')} จังหวัด{c.get('changwatName','-')}",
                "father_id": f"{f_name} ({f_id})", "mother_id": f"{m_name} ({m_id})"
            })
                
    return jsonify({"results": final_results})

@app.route('/adminxaingrung', methods=['GET', 'POST'])
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD: return "Forbidden", 403
    tk = "AUTH-" + secrets.token_hex(4).upper()
    tokens_db[tk] = datetime.now() + timedelta(hours=24)
    return f"Token: {tk}"

@app.route('/')
def index(): return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
