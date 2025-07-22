from inspect import signature
import ipaddress
import subprocess
import psutil
import socket  
import typer

import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from typer import colors
from log import logger

app = typer.Typer(invoke_without_command=True)


@app.callback()
def default(ctx: typer.Context):
    """
    proxy 命令入口。未指定子命令时默认执行 scan。
    """
    if ctx.invoked_subcommand is None:
        origin_scan(None, 7890)


def scan(
    subnet: str|None = typer.Option(None, '--subnet', '-s', help="搜索范围"),
    port: int = typer.Option(7890, '--port', '-p', help="代理端口"),

):
    """
    扫描可用的代理
    """
    ips = {}
    
    if subnet:
        ips['input'] = subnet.split('/')
    else:
        # 获取所有网络接口的地址信息
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:  # 只处理 IPv4 地址
                    network = ipaddress.IPv4Network(f'{addr.address}/{addr.netmask}', strict=False)
                    ips[interface] = str(network.network_address) , str(network.prefixlen)
    
    endpoints = []
    for interface, (addr,prefix) in ips.items():
        if interface=='lo':
            continue
        logger.debug(f"{interface}: {addr}/{prefix}")
        
        eps = scan_subnet_for_port(f"{addr}/{prefix}", port)
        endpoints.extend(eps)
    for ep in endpoints:
        logger.debug(f"endpoint: {ep}:{port}")
        
        typer.echo(typer.style(f'\n执行以下命令以设置代理:', fg=colors.CYAN))
        if check_socks5_proxy(ep, port):
            cmd = f'\texport http_proxy=socks5://{ep}:7890 https_proxy=socks5://{ep}:7890 all_proxy=socks5://{ep}:7890'
            
            typer.echo(typer.style(cmd, fg=colors.YELLOW))
                    
origin_scan = scan
scan = app.command()(scan)


def scan_host_port(ip: str, port: int, timeout: float = 0.3) -> bool:
    """尝试连接目标IP的指定端口，返回是否开放"""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False
    

def scan_subnet_for_port(cidr: str, port: int):
    """扫描子网内开启了指定端口的主机"""
    network = ipaddress.ip_network(cidr, strict=False)

    logger.info(f"Scanning {cidr} for port {port}...")

    with ThreadPoolExecutor(max_workers=100) as executor:
        future_to_ip = {
            executor.submit(scan_host_port, str(ip), port): str(ip)
            for ip in network.hosts()
        }

        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                if future.result():
                    yield ip 
            except Exception as e:
                print(f"❌ {ip}:{port} error: {e}")



@app.command()
def test_scan():
    endpoints = scan_subnet_for_port("192.168.2.245/24", 7890)
    for ep in endpoints:
        print('ep:', ep)



import socket
import requests
import socks
import ssl
from urllib.request import urlopen, Request
from urllib.error import URLError

def check_socks5_proxy(host, port):
    """检测 SOCKS5 代理"""
    try:
        # 通过 SOCKS5 代理连接
        socks.set_default_proxy(socks.SOCKS5, host, port)
        socket.socket = socks.socksocket  # 将所有 socket 请求通过 SOCKS 代理
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.connect(("httpbin.org", 80))  # 测试连接到外部网站
        return True
    except Exception as e:
        print(f"SOCKS5代理检测失败: {e}")
        return False

def check_http_proxy(host, port):
    """检测 HTTP 代理"""
    try:
        proxy_url = f"http://{host}:{port}"
        response = requests.get("https://example.com", proxies={"http": proxy_url, "https": proxy_url}, timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException as e:
        print(f"HTTP代理检测失败: {e}")
        return False

def check_https_proxy(host, port):
    """检测 HTTPS 代理"""
    try:
        proxy_url = f"http://{host}:{port}"
        response = requests.get("https://example.com", proxies={"http": proxy_url, "https": proxy_url}, timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException as e:
        print(f"HTTPS代理检测失败: {e}")
        return False

def detect_proxy_type(host, port):
    """检测代理类型"""
    if check_socks5_proxy(host, port):
        print("代理类型: SOCKS5")
    if check_http_proxy(host, port):
        print("代理类型: HTTP")
    if check_https_proxy(host, port):
        print("代理类型: HTTPS")
    else:
        print("未识别的代理类型")


def test1():# 测试
    host = "192.168.2.1"
    port = 7890
    detect_proxy_type(host, port)







if __name__ == "__main__":
    app()
