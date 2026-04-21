import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Add the api directory to the path so we can import your Vercel handler
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
from index import handler as ApiHandler

class LocalDevServer(SimpleHTTPRequestHandler):
    def do_POST(self):
        # Route API calls to your Vercel Python script
        if self.path == '/api/index':
            ApiHandler(self.request, self.client_address, self.server)
            return
        super().do_POST()
        
    def do_OPTIONS(self):
        if self.path == '/api/index':
            ApiHandler(self.request, self.client_address, self.server)
            return
        super().do_OPTIONS()

if __name__ == "__main__":
    # Ensure the API key is set securely before starting the server
    if not os.environ.get("GEMINI_API_KEY"):
        import getpass
        print("\n--- Local Dev Server Setup ---")
        os.environ["GEMINI_API_KEY"] = getpass.getpass("Please paste your fresh Gemini API key: ")
        
    port = 8000
    print(f"\n🚀 Starting Local Web Server...")
    print(f"👉 Open your browser and go to: http://localhost:{port}")
    print("Press Ctrl+C to stop the server.")
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, LocalDevServer)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
