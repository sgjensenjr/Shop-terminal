import http.server
import socketserver
import os

PORT = int(os.environ.get('PORT', 8000))

class ShopTerminalHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Default route serves index.html
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
            return super().do_GET()

        # API route to fetch the full equipment catalog
        if self.path == '/api/catalog':
            try:
                with open('equipment_catalog.json', 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
            return

        return super().do_GET()

if __name__ == '__main__':
    with socketserver.TCPServer(('', PORT), ShopTerminalHandler) as httpd:
        print(f"Shop Terminal server running on port {PORT}")
        httpd.serve_forever()
