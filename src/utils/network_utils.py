"""
Network Utilities - Pure Python Implementation

Provides network information without requiring the netifaces package
which needs C compilation.
"""

import socket
import subprocess
import re
from typing import Dict, List, Optional, Tuple
from loguru import logger


def get_local_ip() -> str:
    """
    Get the local IP address of this machine.
    
    Returns:
        Local IP address string
    """
    try:
        # Create a socket and connect to an external address
        # This doesn't actually send any data
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        try:
            # Connect to Google DNS - doesn't actually send data
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip
    except Exception as e:
        logger.debug(f"Could not get local IP: {e}")
        return "127.0.0.1"


def get_hostname() -> str:
    """
    Get the hostname of this machine.
    
    Returns:
        Hostname string
    """
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"


def get_all_ip_addresses() -> List[str]:
    """
    Get all IP addresses associated with this machine.
    
    Returns:
        List of IP address strings
    """
    ips = []
    try:
        hostname = socket.gethostname()
        # Get all addresses for this hostname
        addresses = socket.getaddrinfo(hostname, None)
        for addr in addresses:
            ip = addr[4][0]
            if ip not in ips and not ip.startswith("::"):
                ips.append(ip)
    except Exception as e:
        logger.debug(f"Error getting IP addresses: {e}")
    
    # Always include localhost
    if "127.0.0.1" not in ips:
        ips.append("127.0.0.1")
    
    return ips


def get_network_interfaces_windows() -> Dict[str, Dict]:
    """
    Get network interface information on Windows using ipconfig.
    
    Returns:
        Dictionary of interface information
    """
    interfaces = {}
    
    try:
        # Run ipconfig /all
        result = subprocess.run(
            ["ipconfig", "/all"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        if result.returncode != 0:
            return interfaces
        
        output = result.stdout
        
        # Parse the output
        current_adapter = None
        current_info = {}
        
        for line in output.split('\n'):
            line = line.strip()
            
            # New adapter section
            if 'adapter' in line.lower() and ':' in line:
                if current_adapter and current_info:
                    interfaces[current_adapter] = current_info
                current_adapter = line.rstrip(':')
                current_info = {'name': current_adapter}
            
            # Parse adapter properties
            elif current_adapter and ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower().replace(' ', '_').replace('.', '')
                    value = parts[1].strip()
                    
                    if 'ipv4' in key or key == 'ip_address':
                        # Extract IP, remove any extra info in parentheses
                        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', value)
                        if ip_match:
                            current_info['ipv4'] = ip_match.group(1)
                    elif 'subnet' in key:
                        current_info['subnet_mask'] = value
                    elif 'gateway' in key and value:
                        current_info['gateway'] = value
                    elif 'mac' in key or 'physical' in key:
                        current_info['mac_address'] = value
                    elif 'dhcp' in key and 'enabled' in key.lower():
                        current_info['dhcp_enabled'] = 'yes' in value.lower()
        
        # Add last adapter
        if current_adapter and current_info:
            interfaces[current_adapter] = current_info
            
    except subprocess.TimeoutExpired:
        logger.warning("ipconfig timed out")
    except Exception as e:
        logger.debug(f"Error getting network interfaces: {e}")
    
    return interfaces


def get_public_ip() -> Optional[str]:
    """
    Get the public IP address using an external service.
    
    Returns:
        Public IP address or None if unavailable
    """
    import urllib.request
    
    services = [
        "https://api.ipify.org",
        "https://icanhazip.com",
        "https://ifconfig.me/ip",
    ]
    
    for service in services:
        try:
            with urllib.request.urlopen(service, timeout=5) as response:
                ip = response.read().decode('utf-8').strip()
                # Validate it looks like an IP
                if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                    return ip
        except Exception:
            continue
    
    return None


def check_internet_connection(host: str = "8.8.8.8", port: int = 53, timeout: float = 3) -> bool:
    """
    Check if there is an internet connection.
    
    Args:
        host: Host to check (default: Google DNS)
        port: Port to check
        timeout: Timeout in seconds
        
    Returns:
        True if connected, False otherwise
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def get_network_info() -> Dict[str, any]:
    """
    Get comprehensive network information.
    
    Returns:
        Dictionary with network information
    """
    info = {
        "hostname": get_hostname(),
        "local_ip": get_local_ip(),
        "all_ips": get_all_ip_addresses(),
        "public_ip": None,
        "internet_connected": check_internet_connection(),
        "interfaces": {}
    }
    
    # Get interfaces on Windows
    import platform
    if platform.system() == "Windows":
        info["interfaces"] = get_network_interfaces_windows()
    
    # Try to get public IP if connected
    if info["internet_connected"]:
        info["public_ip"] = get_public_ip()
    
    return info


def ping_host(host: str, count: int = 4) -> Dict[str, any]:
    """
    Ping a host and return results.
    
    Args:
        host: Host to ping
        count: Number of pings
        
    Returns:
        Dictionary with ping results
    """
    result = {
        "host": host,
        "success": False,
        "packets_sent": count,
        "packets_received": 0,
        "avg_time_ms": None,
        "error": None
    }
    
    try:
        # Windows ping command
        cmd = ["ping", "-n", str(count), host]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=count * 2 + 5,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        output = process.stdout
        
        # Parse results
        # Look for "Received = X"
        received_match = re.search(r'Received\s*=\s*(\d+)', output)
        if received_match:
            result["packets_received"] = int(received_match.group(1))
            result["success"] = result["packets_received"] > 0
        
        # Look for average time
        avg_match = re.search(r'Average\s*=\s*(\d+)ms', output)
        if avg_match:
            result["avg_time_ms"] = int(avg_match.group(1))
            
    except subprocess.TimeoutExpired:
        result["error"] = "Ping timed out"
    except Exception as e:
        result["error"] = str(e)
    
    return result


# Simple speed test without external package
def simple_speed_test(url: str = "http://speedtest.tele2.net/1MB.zip") -> Dict[str, any]:
    """
    Perform a simple download speed test.
    
    Args:
        url: URL to download for testing
        
    Returns:
        Dictionary with speed test results
    """
    import urllib.request
    import time
    
    result = {
        "success": False,
        "download_speed_mbps": None,
        "error": None
    }
    
    try:
        start_time = time.time()
        
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read()
        
        end_time = time.time()
        
        # Calculate speed
        duration = end_time - start_time
        size_bytes = len(data)
        size_bits = size_bytes * 8
        speed_bps = size_bits / duration
        speed_mbps = speed_bps / (1024 * 1024)
        
        result["success"] = True
        result["download_speed_mbps"] = round(speed_mbps, 2)
        result["file_size_mb"] = round(size_bytes / (1024 * 1024), 2)
        result["duration_seconds"] = round(duration, 2)
        
    except Exception as e:
        result["error"] = str(e)
    
    return result