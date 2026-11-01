import http.server
import socketserver
import os

PORT = int(os.environ.get('PORT', 8000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(BASE_DIR, 'equipment_catalog.json')

class ShopTerminalHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Default route serves index.html
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
            return super().do_GET()

        # API route to fetch the full equipment catalog
        if self.path == '/api/catalog':
            if not os.path.exists(CATALOG_PATH):
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "Catalog file not found"}')
                return

            try:
                with open(CATALOG_PATH, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
            return

        return super().do_GET()

if __name__ == '__main__':
    with socketserver.TCPServer(('', PORT), ShopTerminalHandler) as httpd:
        print(f"Shop Terminal server running on port {PORT}")
        httpd.serve_forever()
