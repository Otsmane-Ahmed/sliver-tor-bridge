import os
import shutil
from stem.control import Controller
from stem.process import launch_tor_with_config


class TorManager:
    
    def __init__(
        self,
        hidden_service_dir='hidden_service',
        tor_port=9050,
        ctrl_port=9051,
        service_port=80,
        target_port=8443
    ):
        self.hidden_service_dir = os.path.abspath(hidden_service_dir)
        self.tor_port = tor_port
        self.ctrl_port = ctrl_port
        self.service_port = service_port
        self.target_port = target_port
        self.tor_process = None
        self._onion_address = None

    def start_tor(self):
        print("[*] Starting Tor Hidden Service...")
        
        if not os.path.exists(self.hidden_service_dir):
            os.makedirs(self.hidden_service_dir, mode=0o700)
        else:
            os.chmod(self.hidden_service_dir, 0o700)
        
        tor_config = {
            'SocksPort': str(self.tor_port),
            'ControlPort': str(self.ctrl_port),
            'HiddenServiceDir': self.hidden_service_dir,
            'HiddenServicePort': f'{self.service_port} 127.0.0.1:{self.target_port}',
            'CookieAuthentication': '1',
            'Log': 'NOTICE stdout',
        }

        print(f"[*] Hidden Service Dir: {self.hidden_service_dir}")
        print(f"[*] Service Port: {self.service_port} -> localhost:{self.target_port}")

        try:
            print("[*] Connecting to Tor network (this may take 1-3 minutes)...")
            self.tor_process = launch_tor_with_config(
                config=tor_config,
                take_ownership=True,
                completion_percent=100,
                timeout=300,
                init_msg_handler=lambda line: print(f"    {line}") if 'Bootstrapped' in line else None
            )
            print("[+] Tor started successfully!")
            
            self._onion_address = self.get_onion_address()
            if self._onion_address:
                print(f"[+] Hidden Service: http://{self._onion_address}")
            
        except Exception as e:
            print(f"[!] Error starting Tor: {e}")
            if "Process terminated" in str(e):
                print("[!] Hint: Check if another Tor instance is running (sudo systemctl stop tor)")
                print("[!] Hint: Check permissions on hidden service directory")
            raise

    def get_onion_address(self):
        hostname_path = os.path.join(self.hidden_service_dir, 'hostname')
        if os.path.exists(hostname_path):
            with open(hostname_path, 'r') as f:
                return f.read().strip()
        return None

    def stop_tor(self):
        if self.tor_process:
            print("[*] Stopping Tor...")
            self.tor_process.kill()
            print("[+] Tor stopped.")
            self.tor_process = None

    def is_running(self):
        return self.tor_process is not None

    def cleanup(self):
        if os.path.exists(self.hidden_service_dir):
            shutil.rmtree(self.hidden_service_dir)
            print(f"[*] Cleaned up: {self.hidden_service_dir}")

    def __enter__(self):
        self.start_tor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_tor()
