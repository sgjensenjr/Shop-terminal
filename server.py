import os
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer
from database import get_connection, init_db
from seed_data import seed_blowers

# Ensure DB and seeds run automatically on start
init_db()
seed_blowers()

class InventoryAPIHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '':
            self.path = '/index.html'

        if self.path == '/api/models':
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT e.*, COUNT(f.id) as unit_count
                FROM equipment e
                LEFT JOIN fleet_units f ON e.id = f.equipment_id
                GROUP BY e.id
                ORDER BY e.category, e.make, e.model
            """)
            models = [dict(row) for row in cur.fetchall()]
            conn.close()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(models).encode())

        elif self.path.startswith('/api/units'):
            equipment_id = self.path.split('equipment_id=')[-1] if 'equipment_id=' in self.path else None
            unit_tag = self.path.split('unit_tag=')[-1] if 'unit_tag=' in self.path else None

            conn = get_connection()
            cur = conn.cursor()
            if equipment_id:
                cur.execute("SELECT * FROM fleet_units WHERE equipment_id = ? ORDER BY unit_tag", (equipment_id,))
            elif unit_tag:
                cur.execute("""
                    SELECT f.*, e.category, e.make, e.model, e.image_url,
                           e.oil_type, e.oil_capacity, e.fuel_mix, e.spark_plug_spec, e.valve_spec, e.notes as model_notes
                    FROM fleet_units f
                    JOIN equipment e ON f.equipment_id = e.id
                    WHERE f.unit_tag = ?
                """, (unit_tag,))
            else:
                cur.execute("SELECT * FROM fleet_units ORDER BY unit_tag")
            rows = [dict(row) for row in cur.fetchall()]
            conn.close()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(rows).encode())

        elif self.path.startswith('/api/assemblies'):
            equipment_id = self.path.split('equipment_id=')[-1] if 'equipment_id=' in self.path else None
            conn = get_connection()
            cur = conn.cursor()
            if equipment_id:
                cur.execute("""
                    SELECT DISTINCT a.id, a.name
                    FROM assemblies a
                    JOIN equipment_parts ep ON a.id = ep.assembly_id
                    WHERE ep.equipment_id = ?
                    ORDER BY a.name
                """, (equipment_id,))
            else:
                cur.execute("SELECT * FROM assemblies ORDER BY name")
            rows = [dict(row) for row in cur.fetchall()]
            conn.close()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(rows).encode())

        elif self.path.startswith('/api/parts'):
            query_params = dict(qp.split('=') for qp in self.path.split('?')[-1].split('&') if '=' in qp)
            equipment_id = query_params.get('equipment_id')
            assembly_id = query_params.get('assembly_id')

            conn = get_connection()
            cur = conn.cursor()
            query = """
                SELECT p.*, a.name as assembly_name
                FROM parts p
                JOIN equipment_parts ep ON p.id = ep.part_id
                JOIN assemblies a ON ep.assembly_id = a.id
                WHERE ep.equipment_id = ? AND ep.assembly_id = ?
                ORDER BY p.name
            """
            cur.execute(query, (equipment_id, assembly_id))
            rows = [dict(row) for row in cur.fetchall()]
            conn.close()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(rows).encode())

        elif self.path.startswith('/api/maintenance'):
            unit_id = self.path.split('unit_id=')[-1] if 'unit_id=' in self.path else None
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM maintenance_logs
                WHERE unit_id = ?
                ORDER BY service_date DESC, id DESC
            """, (unit_id,))
            rows = [dict(row) for row in cur.fetchall()]
            conn.close()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(rows).encode())

        else:
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8')) if post_data else {}

        conn = get_connection()
        cur = conn.cursor()

        if self.path == '/api/equipment/add':
            cur.execute("""
                INSERT INTO equipment (category, make, model, image_url, oil_type, fuel_mix, spark_plug_spec, valve_spec, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('category'), data.get('make'), data.get('model'),
                data.get('image_url') or 'https://images.unsplash.com/photo-1590856029826-c7a73142bbf1?w=200&h=200&fit=crop',
                data.get('oil_type'), data.get('fuel_mix'), data.get('spark_plug_spec'), data.get('valve_spec'),
                data.get('notes', '')
            ))
            eq_id = cur.lastrowid
            if data.get('unit_tag'):
                cur.execute("INSERT INTO fleet_units (equipment_id, unit_tag, status) VALUES (?, ?, 'In Service')",
                            (eq_id, data.get('unit_tag')))
            conn.commit()

        elif self.path == '/api/models/update_notes':
            cur.execute("UPDATE equipment SET notes = ? WHERE id = ?", (data.get('notes', '').strip(), data.get('equipment_id')))
            conn.commit()

        elif self.path == '/api/units/add':
            cur.execute("""
                INSERT INTO fleet_units (equipment_id, unit_tag, status, notes)
                VALUES (?, ?, 'In Service', ?)
            """, (data.get('equipment_id'), data.get('unit_tag'), data.get('notes', '')))
            conn.commit()

        elif self.path == '/api/parts/add':
            cur.execute("""
                INSERT INTO parts (name, oem_number, hardware_spec, location, stock_qty, reorder_min, supplier_name, reorder_url)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """, (
                data.get('name'), data.get('oem_number'), data.get('hardware_spec'),
                data.get('location'), int(data.get('stock_qty', 0)),
                data.get('supplier_name'), data.get('reorder_url')
            ))
            part_id = cur.lastrowid
            cur.execute("""
                INSERT INTO equipment_parts (equipment_id, assembly_id, part_id)
                VALUES (?, ?, ?)
            """, (data.get('equipment_id'), data.get('assembly_id'), part_id))
            conn.commit()

        elif self.path == '/api/parts/adjust_stock':
            cur.execute("UPDATE parts SET stock_qty = MAX(0, stock_qty + ?) WHERE id = ?", (data.get('delta'), data.get('part_id')))
            conn.commit()

        elif self.path == '/api/maintenance/add':
            cur.execute("""
                INSERT INTO maintenance_logs (unit_id, work_performed, parts_used, tech_notes)
                VALUES (?, ?, ?, ?)
            """, (data.get('unit_id'), data.get('work_performed'), data.get('parts_used'), data.get('tech_notes')))
            conn.commit()

        elif self.path == '/api/units/delete':
            cur.execute("DELETE FROM fleet_units WHERE id = ?", (data.get('unit_id'),))
            conn.commit()

        conn.close()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"success": True}).encode())

def run_server():
    # Cloud hosts provide the PORT environment variable
    port = int(os.environ.get('PORT', 8000))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, InventoryAPIHandler)
    print(f"Shop terminal running on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
