import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer

who_up = 0  # 1 - work, 2 - dead 
who_active = {} 

class MetricsHandler(BaseHTTPRequestHandler):
    """
    Handlers for GET query 
    """
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            
            response = []
            
            # who_up
            response.append(f"who_up {who_up}")
            
            # who_active
            for username, count in who_active.items():
                response.append(f"who_active{{username=\"{username}\"}} {count}")
            
            self.wfile.write("\n".join(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_http_server(port):
    """
    Start server on given port
    """
    server_address = ('', port)
    httpd = HTTPServer(server_address, MetricsHandler)
    print(f"Starting HTTP server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP server for who exporter metrics')
    parser.add_argument('-p', '--port', type=int, default=8000, help='Port to expose metrics on')
    args = parser.parse_args()

    start_http_server(args.port)
