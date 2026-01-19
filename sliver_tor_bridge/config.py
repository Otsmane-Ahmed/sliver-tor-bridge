import os
import yaml
from dataclasses import dataclass
from typing import Optional


@dataclass
class TorConfig:
    socks_port: int = 9050
    control_port: int = 9051


@dataclass
class HiddenServiceConfig:
    port: int = 80
    directory: str = './hidden_service'


@dataclass
class SliverConfig:
    host: str = '127.0.0.1'
    port: int = 8443


@dataclass
class BridgeConfig:
    sliver: SliverConfig
    tor: TorConfig
    hidden_service: HiddenServiceConfig
    proxy_port: int = 8080
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BridgeConfig':
        return cls(
            sliver=SliverConfig(**data.get('sliver', {})),
            tor=TorConfig(**data.get('tor', {})),
            hidden_service=HiddenServiceConfig(**data.get('hidden_service', {})),
            proxy_port=data.get('proxy_port', 8080)
        )
    
    @classmethod
    def from_file(cls, path: str) -> 'BridgeConfig':
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)
    
    @classmethod
    def default(cls) -> 'BridgeConfig':
        return cls(
            sliver=SliverConfig(),
            tor=TorConfig(),
            hidden_service=HiddenServiceConfig()
        )
    
    def to_dict(self) -> dict:
        return {
            'sliver': {'host': self.sliver.host, 'port': self.sliver.port},
            'tor': {'socks_port': self.tor.socks_port, 'control_port': self.tor.control_port},
            'hidden_service': {'port': self.hidden_service.port, 'directory': self.hidden_service.directory},
            'proxy_port': self.proxy_port
        }
    
    def save(self, path: str):
        with open(path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)


def load_config(path: Optional[str] = None) -> BridgeConfig:
    if path and os.path.exists(path):
        return BridgeConfig.from_file(path)
    
    common_paths = ['./config.yaml', './config.yml', os.path.expanduser('~/.sliver-tor-bridge/config.yaml')]
    
    for p in common_paths:
        if os.path.exists(p):
            return BridgeConfig.from_file(p)
    
    return BridgeConfig.default()
