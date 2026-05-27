"""
auth_server.py  —  Stock Pro 10X med login
Sæt disse 3 miljøvariabler (Render: Environment):
  APP_USERNAME   dit brugernavn   (fx: thomas)
  APP_PASSWORD   din adgangskode  (fx: Kode123!)
  SECRET_KEY     en lang hemmelig streng (fx: xK9mP2qR7nL5vW8)
"""

import os, hashlib, hmac, time, json, urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

HOST     = "0.0.0.0"
PORT     = int(os.environ.get("PORT", "7722"))
ROOT     = Path(__file__).resolve().parent

USERNAME   = os.environ.get("APP_USERNAME", "admin")
PASSWORD   = os.environ.get("APP_PASSWORD", "skift-mig")
SECRET     = os.environ.get("SECRET_KEY",   "skift-denne-nu!")
MAX_AGE    = 60 * 60 * 24 * 30   # 30 dage

LOGIN_HTML = (ROOT / "login.html").read_bytes()

# --- session-token (HMAC, ingen database) ------------------------------------
def make_token(user):
    ts  = str(int(time.time()))
    msg = f"{user}:{ts}"
    sig = hmac.new(SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()
    return urllib.parse.quote(f"{msg}:{sig}", safe="")

def valid_token(tok):
    try:
        raw         = urllib.parse.unquote(tok)
        msg, sig    = raw.rsplit(":", 1)
        user, ts    = msg.rsplit(":", 1)
        if not hmac.compare_digest(hmac.new(SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest(), sig):
            return False
        return time.time() - int(ts) < MAX_AGE
    except Exception:
        return False

def logged_in(headers):
    for part in headers.get("Cookie", "").split(";"):
        k, _, v = part.strip().partition("=")
        if k == "sp_sess":
            return valid_token(v)
    return False

# --- handler -----------------------------------------------------------------
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    # ekstra security-headers på alt
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def json_response(self, payload, status=200):
        data = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type",   "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204); self.end_headers()

    # ---------- GET ----------------------------------------------------------
    def do_GET(self):
        p = urllib.parse.urlparse(self.path).path

        if p == "/favicon.ico":
            self.send_response(204); self.end_headers(); return

        if p == "/login":
            self._page(LOGIN_HTML); return

        if p == "/logout":
            self._redir("/login", clear_cookie=True); return

        if not logged_in(self.headers):
            self._redir("/login"); return

        # --- herunder: alt fra original server.py ---
        import server as _s
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

        if p == "/api/etf":
            if _s.etf_core is None:
                return self.json_response({"ok": False, "error": "ETF ikke indlaedt"}, 500)
            ticker = (qs.get("ticker", [""])[0] or "").strip().upper()
            if not ticker:
                return self.json_response({"ok": False, "error": "Missing ticker"}, 400)
            try:
                ov = _s.etf_core.etf_overview(ticker)
                return self.json_response(ov)
            except Exception as e:
                return self.json_response({"ok": False, "error": str(e)}, 502)

        if p == "/api/ping":
            return self.json_response({"ok": True, "ts": int(time.time())})

        if p in ("/api/etf-search", "/api/etf-db", "/api/etf-debug",
                 "/api/breakout-universes", "/api/breakout-single",
                 "/api/breakout-tickers", "/api/breakout", "/api/breakout-scan",
                 "/api/backtest", "/api/yahoo-test", "/api/universe",
                 "/api/news", "/api/earnings", "/api/stock-finnhub",
                 "/api/stock", "/api/stocks", "/api/smallcaps",
                 "/api/smallcaps-data"):
            # Delegate to original handler logic via subclass trick
            return _s.Handler.do_GET(self)

        # statiske filer (index.html, etf.html, osv.)
        return super().do_GET()

    # ---------- POST ---------------------------------------------------------
    def do_POST(self):
        p = urllib.parse.urlparse(self.path).path
        if p == "/login":
            length = int(self.headers.get("Content-Length", 0))
            data   = urllib.parse.parse_qs(self.rfile.read(length).decode())
            uname  = data.get("username", [""])[0].strip()
            passwd = data.get("password", [""])[0]
            ok = (hmac.compare_digest(uname.lower(), USERNAME.lower()) and
                  hmac.compare_digest(passwd, PASSWORD))
            if ok:
                tok = make_token(uname)
                self.send_response(302)
                self.send_header("Location", "/")
                self.send_header("Set-Cookie",
                    f"sp_sess={tok}; Path=/; HttpOnly; SameSite=Lax; Max-Age={MAX_AGE}")
                self.send_header("Content-Length", "0")
                self.end_headers()
            else:
                self._redir("/login?error=1")
            return
        if not logged_in(self.headers):
            self._redir("/login"); return
        super().do_GET()  # ingen POST-endpoints i original

    # ---------- helpers ------------------------------------------------------
    def _page(self, body: bytes, status=200):
        self.send_response(status)
        self.send_header("Content-Type",   "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _redir(self, loc, clear_cookie=False):
        self.send_response(302)
        self.send_header("Location", loc)
        if clear_cookie:
            self.send_header("Set-Cookie",
                "sp_sess=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *_):
        pass   # stille — fjern linjen for debug-output

# --- start -------------------------------------------------------------------
def main():
    os.chdir(ROOT)
    try:
        import server as _s
        if _s.etf_core:
            _s.etf_core._load_db()
            _s.etf_core._clear_broken_cache()
    except Exception as e:
        print(f"[OBS] server.py advarsel: {e}")

    print(f"Stock Pro 10X korer pa http://{HOST}:{PORT}/")
    print(f"Brugernavn: {USERNAME}  |  Adgangskode: {'*'*len(PASSWORD)}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()

if __name__ == "__main__":
    main()
