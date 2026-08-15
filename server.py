import http.server
import socketserver
import urllib.request
import urllib.parse
import urllib.error
import json
import os
import time
import sys

# Load .env file manually if present
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

PORT = int(os.environ.get("PORT", 3000))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# In-memory rate limiting structure: ip -> (timestamp, count)
rate_limit_map = {}
RATE_LIMIT_WINDOW_SEC = 60
MAX_REQUESTS_PER_WINDOW = 10

def is_rate_limited(ip):
    now = time.time()
    if len(rate_limit_map) > 5000:
        stale_ips = [k for k, (start, _) in rate_limit_map.items() if now - start > RATE_LIMIT_WINDOW_SEC]
        for k in stale_ips:
            del rate_limit_map[k]

    if ip not in rate_limit_map:
        rate_limit_map[ip] = (now, 1)
        return False

    start_time, count = rate_limit_map[ip]
    if now - start_time > RATE_LIMIT_WINDOW_SEC:
        rate_limit_map[ip] = (now, 1)
        return False

    if count >= MAX_REQUESTS_PER_WINDOW:
        return True

    rate_limit_map[ip] = (start_time, count + 1)
    return False

def check_origin(origin, host):
    if not origin:
        return True

    try:
        parsed_origin = urllib.parse.urlparse(origin)
        origin_host = parsed_origin.netloc.split(':')[0] if parsed_origin.netloc else parsed_origin.path.split(':')[0]
        host_name = host.split(':')[0] if host else ''

        if (
            origin_host == host_name or
            origin_host in ('localhost', '127.0.0.1') or
            (os.environ.get('ALLOWED_DOMAINS') and origin_host in os.environ['ALLOWED_DOMAINS'].split(','))
        ):
            return True
        return False
    except Exception:
        return False

def validate_contents(contents):
    if not isinstance(contents, list):
        return "Request payload must contain a 'contents' array."
    if len(contents) == 0:
        return "Conversation history cannot be empty."
    if len(contents) > 40:
        return "Conversation history exceeds maximum limit of 40 messages."

    total_chars = 0
    for item in contents:
        if not isinstance(item, dict):
            return "Invalid item structure in conversation contents."
        role = item.get("role")
        if role not in ("user", "model"):
            return "Invalid message role."
        parts = item.get("parts")
        if not isinstance(parts, list) or len(parts) == 0:
            return "Message missing content parts."
        for part in parts:
            if not isinstance(part, dict) or not isinstance(part.get("text"), str):
                return "Invalid text part format."
            text = part.get("text")
            if len(text) > 4000:
                return "Single message exceeds limit of 4,000 characters."
            total_chars += len(text)

    if total_chars > 20000:
        return "Total conversation history exceeds character limit."
    return None

class HealthAppHandler(http.server.SimpleHTTPRequestHandler):
    def send_json_response(self, status_code, body, is_valid_origin=False):
        try:
            resp_bytes = json.dumps(body).encode('utf-8')
            self.send_response_only(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(resp_bytes)))
            self.send_header('Connection', 'close')
            self.send_header('Date', self.date_time_string())
            self.send_header('Server', self.version_string())
            origin = self.headers.get('Origin')
            if origin and is_valid_origin:
                self.send_header('Access-Control-Allow-Origin', origin)
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(resp_bytes)
            self.wfile.flush()
        except Exception as e:
            print(f"Error writing JSON response: {e}", file=sys.stderr)

    def do_POST(self):
        if self.path == '/api/chat':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length) if content_length > 0 else b''

                origin = self.headers.get('Origin')
                host = self.headers.get('Host')
                valid_origin = check_origin(origin, host)

                # 1. Domain/Origin check -> Return clean 403
                if not valid_origin:
                    return self.send_json_response(403, {"error": "Access forbidden: Request origin not allowed."}, is_valid_origin=False)

                # 2. Rate limiting check -> Return 429
                client_ip = self.headers.get('X-Forwarded-For', self.client_address[0]).split(',')[0].strip()
                if is_rate_limited(client_ip):
                    return self.send_json_response(429, {"error": "Too many requests. Please wait a minute before trying again."}, is_valid_origin=valid_origin)

                # 3. Environment check -> Return 500 with generic text
                if not GEMINI_API_KEY:
                    print("Server Configuration Error: GEMINI_API_KEY missing in environment variables.", file=sys.stderr)
                    return self.send_json_response(500, {"error": "Assistant service is currently unavailable. Please try again later."}, is_valid_origin=valid_origin)

                # 4. Input validation -> Return 400
                try:
                    req_body = json.loads(post_data.decode('utf-8'))
                except Exception:
                    return self.send_json_response(400, {"error": "Invalid JSON request body."}, is_valid_origin=valid_origin)

                contents = req_body.get('contents', [])
                val_error = validate_contents(contents)
                if val_error:
                    return self.send_json_response(400, {"error": val_error}, is_valid_origin=valid_origin)

                # 5. Forward request to Gemini API
                system_instruction = (
                    "You are KHeal ( ख्याल ), an empathetic, professional, and highly knowledgeable "
                    "AI medical assistant designed for health guidance, symptom triage, and wellness advice. "
                    "Maintain a reassuring, supportive, and clinical tone. Always keep responses clear, "
                    "well-structured (use bullet points or short sections when helpful), and concise."
                )
                
                model = "gemini-3.6-flash"
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
                
                payload = {
                    "system_instruction": {
                        "parts": [{"text": system_instruction}]
                    },
                    "contents": contents
                }
                
                headers = {'Content-Type': 'application/json'}
                req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
                
                with urllib.request.urlopen(req) as resp:
                    resp_data = resp.read()
                    self.send_response_only(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', str(len(resp_data)))
                    self.send_header('Connection', 'close')
                    self.send_header('Date', self.date_time_string())
                    self.send_header('Server', self.version_string())
                    if origin and valid_origin:
                        self.send_header('Access-Control-Allow-Origin', origin)
                    self.end_headers()
                    self.wfile.write(resp_data)
                    self.wfile.flush()
            except urllib.error.HTTPError as e:
                err_body = e.read().decode('utf-8')
                print(f"Gemini API HTTP Error ({e.code}): {err_body}", file=sys.stderr)
                return self.send_json_response(500, {"error": "An error occurred while processing your request with the AI model. Please try again later."}, is_valid_origin=True)
            except Exception as e:
                print(f"Unhandled server error in do_POST: {e}", file=sys.stderr)
                return self.send_json_response(500, {"error": "An unexpected internal error occurred. Please try again later."}, is_valid_origin=True)
        else:
            self.send_error(404, "Not Found")

    def do_OPTIONS(self):
        if self.path == '/api/chat':
            origin = self.headers.get('Origin')
            host = self.headers.get('Host')
            if check_origin(origin, host):
                self.send_response_only(200)
                if origin:
                    self.send_header('Access-Control-Allow-Origin', origin)
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
            else:
                self.send_json_response(403, {"error": "Access forbidden: Request origin not allowed."}, is_valid_origin=False)
        else:
            super().do_OPTIONS()

if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), HealthAppHandler) as httpd:
        print(f"KHeal server running at http://localhost:{PORT}")
        httpd.serve_forever()
