from flask import Flask, request, Response
import requests
import logging
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


class SliverProxy:
    
    def __init__(self, sliver_host='127.0.0.1', sliver_port=8443, listen_port=8080):
        self.sliver_host = sliver_host
        self.sliver_port = sliver_port
        self.sliver_url = f'https://{sliver_host}:{sliver_port}'
        self.listen_port = listen_port
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
        @self.app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
        def proxy(path):
            return self._relay_request(path)

    def _relay_request(self, path):
        url = f'{self.sliver_url}/{path}'
        headers = {key: value for key, value in request.headers if key.lower() != 'host'}
        
        try:
            response = requests.request(
                method=request.method,
                url=url,
                headers=headers,
                data=request.get_data(),
                cookies=request.cookies,
                allow_redirects=False,
                timeout=30,
                verify=False
            )
            
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            response_headers = [
                (name, value) for name, value in response.raw.headers.items()
                if name.lower() not in excluded_headers
            ]
            
            return Response(response.content, response.status_code, response_headers)
            
        except requests.exceptions.ConnectionError:
            return Response("Sliver server not reachable", status=502, mimetype='text/plain')
        except requests.exceptions.Timeout:
            return Response("Request to Sliver server timed out", status=504, mimetype='text/plain')
        except Exception as e:
            return Response(f"Proxy error: {str(e)}", status=500, mimetype='text/plain')

    def run(self, debug=False):
        print(f"[*] Proxy listening on port {self.listen_port}")
        print(f"[*] Forwarding to Sliver at {self.sliver_url}")
        self.app.run(host='127.0.0.1', port=self.listen_port, debug=debug, threaded=True)


def create_proxy(sliver_host='127.0.0.1', sliver_port=8443, listen_port=8080):
    return SliverProxy(sliver_host, sliver_port, listen_port)
