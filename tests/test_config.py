"""
Tests for the configuration module
"""

import pytest
import os
import tempfile
from sliver_tor_bridge.config import BridgeConfig, load_config


class TestBridgeConfig:
    """Tests for BridgeConfig class"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = BridgeConfig.default()
        
        assert config.sliver.host == '127.0.0.1'
        assert config.sliver.port == 8443
        assert config.tor.socks_port == 9050
        assert config.tor.control_port == 9051
        assert config.hidden_service.port == 80
    
    def test_from_dict(self):
        """Test creating config from dictionary"""
        data = {
            'sliver': {'host': '192.168.1.1', 'port': 9999},
            'tor': {'socks_port': 9150},
            'proxy_port': 9090
        }
        
        config = BridgeConfig.from_dict(data)
        
        assert config.sliver.host == '192.168.1.1'
        assert config.sliver.port == 9999
        assert config.tor.socks_port == 9150
        assert config.proxy_port == 9090
    
    def test_save_and_load(self):
        """Test saving and loading config file"""
        config = BridgeConfig.default()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
        
        try:
            config.save(config_path)
            loaded = BridgeConfig.from_file(config_path)
            
            assert loaded.sliver.host == config.sliver.host
            assert loaded.sliver.port == config.sliver.port
        finally:
            os.unlink(config_path)
    
    def test_to_dict(self):
        """Test converting config to dictionary"""
        config = BridgeConfig.default()
        data = config.to_dict()
        
        assert 'sliver' in data
        assert 'tor' in data
        assert 'hidden_service' in data
        assert data['sliver']['port'] == 8443


class TestLoadConfig:
    """Tests for load_config function"""
    
    def test_load_default(self):
        """Test loading defaults when no file exists"""
        config = load_config('/nonexistent/path.yaml')
        
        assert config.sliver.host == '127.0.0.1'
        assert config.sliver.port == 8443
