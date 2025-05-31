import json
import http.server
import socketserver
import requests
WEATHER_DATA = { 
    "Tokyo": 
    {
        "condition": "Sunny",
        "temperature": 22
    }, 
    "New York": 
        {
            "condition": "Cloudy", 
            "temperature": 15
        }, 
    "London":
        {
            "condition": "Rainy", 
            "temperature": 12
        } 
        }
TOOLS = [
        {
        "name": "getWeather", 
        "description": "获取指定城市的天气数据", 
        "parameters": 
            { 
             "type": "object",
             "properties": 
                 { 
                  "city": 
                      {
                          "type": "string", 
                          "description": "城市名称"
                    } 
                }, 
                 "required": ["city"] 
            }
    }
    ]


class MCPHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        # 如果请求是获取工具元数据
        if self.path == "/tools":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"tools": TOOLS}).encode('utf-8'))
            return
        # 处理工具执行
        if self.path == "/execute":
            print("Received request to execute tool")
            content_length = int(self.headers.get("Content-Length", 0)) 
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                request = json.loads(post_data)
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
                return
            tool_name = request.get("tool")
            params = request.get("parameters", {})

            if tool_name == "getWeather":
                city = params.get("city")
                api_key = "YOUR_API_KEY"
                url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    response_data = {
                        "status": "success",
                        "result": {"condition": data["weather"][0]["main"], "temperature": data["main"]["temp"]}
                    }
                else:
                    response_data = {"status": "error", "message": f"无法获取 {city} 的天气数据"}
            else:
                response_data = {
                    "status": "error",
                    "message": "未知工具"
                }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))

    def do_GET(self):
        # SSE endpoint example
        if self.path == "/events":
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()
            # Example: send a single event, then close
            self.wfile.write(b"data: Hello, SSE!\n\n")
        else:
            super().do_GET()
        
def run_server(port=9000):
    with socketserver.TCPServer(("", port), MCPHandler) as httpd:
        print(f"Serving on port {port}")
        httpd.serve_forever()
        
if __name__ == "__main__":
    run_server()
