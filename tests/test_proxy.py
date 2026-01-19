"""
Tests for the proxy module
"""

import pytest
from unittest.mock import patch, MagicMock
from sliver_tor_bridge.proxy import SliverProxy, create_proxy


class TestSliverProxy:
    """Tests for SliverProxy class"""
    
    def test_initialization(self):
        """Test proxy initialization"""
        proxy = SliverProxy(
            sliver_host='192.168.1.1',
            sliver_port=9999,
            listen_port=8888
        )
        
        assert proxy.sliver_host == '192.168.1.1'
        assert proxy.sliver_port == 9999
        assert proxy.sliver_url == 'http://192.168.1.1:9999'
        assert proxy.listen_port == 8888
    
    def test_default_initialization(self):
        """Test proxy with default values"""
        proxy = SliverProxy()
        
        assert proxy.sliver_host == '127.0.0.1'
        assert proxy.sliver_port == 8443
        assert proxy.listen_port == 8080


class TestCreateProxy:
    """Tests for create_proxy factory function"""
    
    def test_create_proxy(self):
        """Test factory function"""
        proxy = create_proxy(
            sliver_host='10.0.0.1',
            sliver_port=5555,
            listen_port=6666
        )
        
        assert isinstance(proxy, SliverProxy)
        assert proxy.sliver_url == 'http://10.0.0.1:5555'
