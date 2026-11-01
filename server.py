import http.server
import socketserver
import sqlite3
import json
import os
import seed_data

PORT = int(os.environ.get('PORT', 8000))
DB_FILE = 'shop_terminal.db'

if not os.path.exists(DB_FILE):
    seed_data.seed()

class ShopTerminalHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
            return super().do_GET()

        if self.path == '/api/categories':
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("SELECT id, name, icon, image_url FROM categories")
            rows = cur.fetchall()
            conn.close()
            cats = [{"id": r[0], "name": r[1], "icon": r[2], "image_url": r[3]} for r in rows]
            self.send_json(cats)
            return

        if self.path.startswith('/api/models'):
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            # Check for category filter e.g. /api/models?cat=1
            cat_id = None
            if '?cat=' in self.path:
                cat_id = self.path.split('?cat=')[1]
                cur.execute("SELECT id, category_id, make, model_number, fuel_spec, spark_plug, plug_gap, oil_spec, oil_capacity, valve_lash, diagram_url FROM models WHERE category_id = ?", (cat_id,))
            else:
                cur.execute("SELECT id, category_id, make, model_number, fuel_spec, spark_plug, plug_gap, oil_spec, oil_capacity, valve_lash, diagram_url FROM models")
            rows = cur.fetchall()
            conn.close()
            models = [{
                "id": r[0], "category_id": r[1], "make": r[2], "model_number": r[3],
                "fuel_spec": r[4], "spark_plug": r[5], "plug_gap": r[6], "oil_spec": r[7],
                "oil_capacity": r[8], "valve_lash": r[9], "diagram_url": r[10]
            } for r in rows]
            self.send_json(models)
            return

        if self.path.startswith('/api/model_detail'):
            # e.g. /api/model_detail?id=1
            model_id = self.path.split('?id=')[1]
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()

            cur.execute("SELECT id, category_id, make, model_number, fuel_spec, spark_plug, plug_gap, oil_spec, oil_capacity, valve_lash, diagram_url FROM models WHERE id = ?", (model_id,))
            m = cur.fetchone()
            if not m:
                self.send_json({"error": "Model not found"}, status=404)
                conn.close()
                return

            model_data = {
                "id": m[0], "category_id": m[1], "make": m[2], "model_number": m[3],
                "fuel_spec": m[4], "spark_plug": m[5], "plug_gap": m[6], "oil_spec": m[7],
                "oil_capacity": m[8], "valve_lash": m[9], "diagram_url": m[10],
                "assemblies": []
            }

            cur.execute("SELECT id, name FROM assemblies WHERE model_id = ?", (model_id,))
            asm_rows = cur.fetchall()
            for a in asm_rows:
                asm_id, asm_name = a[0], a[1]
                cur.execute("SELECT id, name, oem_number, cross_ref, fits_info, restock_url FROM parts WHERE assembly_id = ?", (asm_id,))
                parts = [{
                    "id": p[0], "name": p[1], "oem_number": p[2],
                    "cross_ref": p[3], "fits_info": p[4], "restock_url": p[5]
                } for p in cur.fetchall()]
                model_data["assemblies"].append({
                    "id": asm_id,
                    "name": asm_name,
                    "parts": parts
                })

            conn.close()
            self.send_json(model_data)
            return

        return super().do_GET()

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len).decode('utf-8')
        data = json.loads(post_body) if post_body else {}

        # 1-Click Import of a New Model Blueprint
        if self.path == '/api/import_model':
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO models (category_id, make, model_number, fuel_spec, spark_plug, plug_gap, oil_spec, oil_capacity, valve_lash, diagram_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('category_id', 1),
                data.get('make', ''),
                data.get('model_number', ''),
                data.get('fuel_spec', ''),
                data.get('spark_plug', ''),
                data.get('plug_gap', ''),
                data.get('oil_spec', ''),
                data.get('oil_capacity', ''),
                data.get('valve_lash', ''),
                data.get('diagram_url', '')
            ))
            new_model_id = cur.lastrowid

            for asm in data.get('assemblies', []):
                cur.execute("INSERT INTO assemblies (model_id, name) VALUES (?, ?)", (new_model_id, asm.get('name', 'General Assembly')))
                asm_id = cur.lastrowid
                for p in asm.get('parts', []):
                    cur.execute('''
                        INSERT INTO parts (assembly_id, name, oem_number, cross_ref, fits_info, restock_url)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        asm_id,
                        p.get('name', ''),
                        p.get('oem_number', ''),
                        p.get('cross_ref', ''),
                        p.get('fits_info', ''),
                        p.get('restock_url', '')
                    ))

            conn.commit()
            conn.close()
            self.send_json({"status": "success", "model_id": new_model_id})
            return

        self.send_json({"error": "Endpoint not found"}, status=404)

    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    with socketserver.TCPServer(('', PORT), ShopTerminalHandler) as httpd:
        print(f"Shop Terminal server running on port {PORT}")
        httpd.serve_forever()
