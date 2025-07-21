import socket
import subprocess
import ipaddress
import concurrent.futures
import psutil
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML
from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import srp


class ProxyCommand:
    def __init__(self):
        self.network = self.get_local_network()

    def get_local_ip(self):
        # 获取本地机器的 IP 地址
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    return addr.address
        return None

    def get_local_network(self):
        local_ip = self.get_local_ip()
        if local_ip:
            # 计算子网网段
            network = ipaddress.IPv4Network(f'{local_ip}/24', strict=False)
            return network
        return None

    def scan_proxy_ports(self, ip, ports=[80, 8080, 3128, 1080]):
        # 扫描指定端口
        open_ports = []
        for port in ports:
            try:
                sock = socket.create_connection((ip, port), timeout=1)
                sock.close()
                open_ports.append(port)
            except socket.error:
                pass
        return open_ports

    def verify_http_proxy(self, ip, port):
        # 验证 HTTP 代理
        try:
            sock = socket.create_connection((ip, port), timeout=1)
            sock.sendall(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
            response = sock.recv(1024)
            if b"HTTP" in response:
                print_formatted_text(HTML(f"<ansigreen>HTTP Proxy found at {ip}:{port}</ansigreen>"))
            sock.close()
        except socket.error:
            pass

    def verify_socks_proxy(self, ip, port):
        # 验证 SOCKS 代理
        try:
            sock = socket.create_connection((ip, port), timeout=1)
            sock.sendall(b"\x05\x01\x00")  # SOCKS5 握手请求
            response = sock.recv(2)
            if response == b"\x05\x00":
                print_formatted_text(HTML(f"<ansigreen>SOCKS Proxy found at {ip}:{port}</ansigreen>"))
            sock.close()
        except socket.error:
            pass

    def discover_hosts(self):
        # 扫描子网内的活跃主机
        arp_request = ARP(pdst=str(self.network))
        ether_frame = Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = ether_frame / arp_request
        result = srp(arp_request_broadcast, timeout=3, verbose=False)[0]

        hosts = []
        for sent, received in result:
            hosts.append(received.psrc)
        return hosts

    def scan_network(self):
        # 扫描局域网并验证代理
        hosts = self.discover_hosts()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for ip in hosts:
                futures.append(executor.submit(self.check_for_proxies, ip))

            # 等待所有任务完成
            for future in concurrent.futures.as_completed(futures):
                future.result()

    def check_for_proxies(self, ip):
        # 检查 HTTP 和 SOCKS 代理
        open_ports = self.scan_proxy_ports(ip)
        if 8080 in open_ports or 3128 in open_ports:
            self.verify_http_proxy(ip, 8080)
            self.verify_http_proxy(ip, 3128)
        if 1080 in open_ports:
            self.verify_socks_proxy(ip, 1080)

    def run(self):
        # 执行代理扫描
        print_formatted_text(HTML("<skyblue>Scanning the network for proxies...</skyblue>"))
        self.scan_network()


