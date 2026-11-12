from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import re
from app.database import get_db_connection, init_db
from app.logic import validate_status_transition, validate_application_input

class RoleRadarHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_OPTIONS(self):
        self._send_json({}, 200)

    def do_GET(self):
        conn = get_db_connection()

        # 1. Serve main HTML dashboard on root "/"
        if self.path == "/" or self.path == "/index.html":
            try:
                with open("static/index.html", "rb") as f:
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(f.read())
                    conn.close()
                    return
            except FileNotFoundError:
                pass

        # 2. Serve static CSS and JS assets
        elif self.path in ["/style.css", "/app.js"]:
            try:
                content_type = "text/css" if self.path.endswith(".css") else "application/javascript"
                with open(f"static{self.path}", "rb") as f:
                    self.send_response(200)
                    self.send_header("Content-Type", content_type)
                    self.end_headers()
                    self.wfile.write(f.read())
                    conn.close()
                    return
            except FileNotFoundError:
                pass

        # 3. Fetch All Applications
        elif self.path == "/api/v1/applications":
            apps = conn.execute("SELECT * FROM applications ORDER BY created_at DESC").fetchall()
            conn.close()
            return self._send_json([dict(row) for row in apps])

        # 4. Aggregated Analytics Query (with COALESCE to prevent null values)
        elif self.path == "/api/v1/analytics/stats":
            stats = conn.execute('''
                SELECT 
                    COUNT(*) AS total_applications,
                    COALESCE(SUM(CASE WHEN status = 'OFFER' THEN 1 ELSE 0 END), 0) AS offers,
                    COALESCE(SUM(CASE WHEN status = 'INTERVIEWING' THEN 1 ELSE 0 END), 0) AS interviewing,
                    COALESCE(SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END), 0) AS rejected
                FROM applications
            ''').fetchone()
            conn.close()
            return self._send_json(dict(stats))

        conn.close()
        return self._send_json({"error": "Route not found"}, 404)

    def do_POST(self):
        if self.path == "/api/v1/applications":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError:
                return self._send_json({"error": "Invalid JSON payload"}, 400)

            is_valid, err_msg = validate_application_input(data)
            if not is_valid:
                return self._send_json({"error": err_msg}, 400)

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO applications (company_name, role_title, job_url, salary_range, applied_date, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data["company_name"],
                data["role_title"],
                data.get("job_url"),
                data.get("salary_range"),
                data["applied_date"],
                data.get("notes")
            ))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return self._send_json({"message": "Application created", "application_id": new_id}, 201)

        return self._send_json({"error": "Route not found"}, 404)

    def do_PUT(self):
        match = re.match(r"^/api/v1/applications/(\d+)/status$", self.path)
        if match:
            app_id = int(match.group(1))
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError:
                return self._send_json({"error": "Invalid JSON payload"}, 400)

            new_status = data.get("status")

            conn = get_db_connection()
            app_entry = conn.execute("SELECT status FROM applications WHERE application_id = ?", (app_id,)).fetchone()

            if not app_entry:
                conn.close()
                return self._send_json({"error": "Application not found"}, 404)

            current_status = app_entry["status"]

            if not validate_status_transition(current_status, new_status):
                conn.close()
                return self._send_json({
                    "error": "INVALID_STATE_TRANSITION",
                    "message": f"Cannot transition from '{current_status}' to '{new_status}'."
                }, 400)

            conn.execute("UPDATE applications SET status = ? WHERE application_id = ?", (new_status, app_id))
            conn.commit()
            conn.close()
            return self._send_json({"message": "Status updated successfully", "new_status": new_status})

        return self._send_json({"error": "Route not found"}, 404)

def run(server_class=HTTPServer, handler_class=RoleRadarHandler):
    init_db()
    # Read dynamic PORT assigned by Render, defaulting to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    server_address = ("0.0.0.0", port)
    httpd = server_class(server_address, handler_class)
    print(f"🚀 RoleRadar Engine running on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
