import os
import subprocess
import socket
from typing import List
from utils import ColorOutput


class NetworkCommands:
    
    @staticmethod
    def ping(args: List[str], cwd: str) -> str:
        """Send ICMP ECHO_REQUEST to network hosts."""
        if not args:
            return ColorOutput.error("ping: missing host operand")
        
        count = 4
        host = None
        
        i = 0
        while i < len(args):
            if args[i] == '-c' and i + 1 < len(args):
                try:
                    count = int(args[i + 1])
                except ValueError:
                    pass
                i += 2
            elif not args[i].startswith('-'):
                host = args[i]
                i += 1
            else:
                i += 1
        
        if not host:
            return ColorOutput.error("ping: missing host operand")
        
        try:
            # Use Windows ping command
            result = subprocess.run(
                ['ping', '-n', str(count), host],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return ColorOutput.error(f"ping: {host}: timed out")
        except Exception as e:
            return ColorOutput.error(f"ping: {e}")
    
    @staticmethod
    def curl(args: List[str], cwd: str) -> str:
        """Transfer data from or to a server."""
        output_file = None
        silent = '-s' in args or '--silent' in args
        include_headers = '-i' in args or '--include' in args
        
        url = None
        i = 0
        while i < len(args):
            if args[i] in ['-o', '--output'] and i + 1 < len(args):
                output_file = args[i + 1]
                i += 2
            elif not args[i].startswith('-'):
                url = args[i]
                i += 1
            else:
                i += 1
        
        if not url:
            return ColorOutput.error("curl: missing URL")
        
        try:
            import urllib.request
            import urllib.error
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'curl/7.0 (Linux Terminal for Windows)')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()
                
                if output_file:
                    from utils import PathConverter
                    full_path = PathConverter.to_windows(output_file)
                    if not os.path.isabs(full_path):
                        full_path = os.path.join(cwd, full_path)
                    with open(full_path, 'wb') as f:
                        f.write(content)
                    return "" if silent else ColorOutput.success(f"Downloaded to {output_file}")
                
                output = []
                if include_headers:
                    output.append(f"HTTP/{response.version} {response.status} {response.reason}")
                    for header, value in response.headers.items():
                        output.append(f"{header}: {value}")
                    output.append("")
                
                try:
                    output.append(content.decode('utf-8'))
                except UnicodeDecodeError:
                    output.append(f"[Binary data: {len(content)} bytes]")
                
                return '\n'.join(output)
        except urllib.error.HTTPError as e:
            return ColorOutput.error(f"curl: HTTP error {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            return ColorOutput.error(f"curl: {e.reason}")
        except Exception as e:
            return ColorOutput.error(f"curl: {e}")
    
    @staticmethod
    def wget(args: List[str], cwd: str) -> str:
        """Non-interactive network downloader."""
        output_file = None
        quiet = '-q' in args or '--quiet' in args
        
        url = None
        i = 0
        while i < len(args):
            if args[i] in ['-O', '--output-document'] and i + 1 < len(args):
                output_file = args[i + 1]
                i += 2
            elif not args[i].startswith('-'):
                url = args[i]
                i += 1
            else:
                i += 1
        
        if not url:
            return ColorOutput.error("wget: missing URL")
        
        if not output_file:
            output_file = url.split('/')[-1] or 'index.html'
        
        try:
            import urllib.request
            
            if not quiet:
                print(f"--  {url}")
                print(f"Saving to: '{output_file}'")
            
            def reporthook(count, block_size, total_size):
                if not quiet and total_size > 0:
                    percent = int(count * block_size * 100 / total_size)
                    print(f"\rProgress: {percent}%", end='', flush=True)
            
            from utils import PathConverter
            full_path = PathConverter.to_windows(output_file)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            urllib.request.urlretrieve(url, full_path, reporthook if not quiet else None)
            
            if not quiet:
                print()
                return ColorOutput.success(f"'{output_file}' saved")
            return ""
        except Exception as e:
            return ColorOutput.error(f"wget: {e}")
    
    @staticmethod
    def ifconfig(args: List[str], cwd: str) -> str:
        """Display network interface configuration."""
        import psutil
        
        output = []
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        for interface, addresses in addrs.items():
            stat = stats.get(interface)
            status = "UP" if stat and stat.isup else "DOWN"
            mtu = stat.mtu if stat else "N/A"
            
            output.append(f"{interface}: flags=<{status}>  mtu {mtu}")
            
            for addr in addresses:
                if addr.family == socket.AF_INET:
                    output.append(f"        inet {addr.address}  netmask {addr.netmask}")
                elif addr.family == socket.AF_INET6:
                    output.append(f"        inet6 {addr.address}")
                elif addr.family == psutil.AF_LINK:
                    output.append(f"        ether {addr.address}")
            
            output.append("")
        
        return '\n'.join(output)
    
    @staticmethod
    def ip(args: List[str], cwd: str) -> str:
        """Show/manipulate routing, network devices (simplified)."""
        if not args or args[0] in ['addr', 'address', 'a']:
            return NetworkCommands.ifconfig([], cwd)
        elif args[0] == 'route':
            try:
                result = subprocess.run(['route', 'print'], capture_output=True, text=True)
                return result.stdout
            except Exception as e:
                return ColorOutput.error(f"ip route: {e}")
        else:
            return ColorOutput.error(f"ip: unknown command '{args[0]}'")
    
    @staticmethod
    def netstat(args: List[str], cwd: str) -> str:
        """Print network connections."""
        try:
            cmd = ['netstat']
            if '-a' in args:
                cmd.append('-a')
            if '-n' in args:
                cmd.append('-n')
            if '-t' in args or '-u' in args:
                cmd.append('-p')
                cmd.append('TCP' if '-t' in args else 'UDP')
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout + result.stderr
        except Exception as e:
            return ColorOutput.error(f"netstat: {e}")
    
    @staticmethod
    def ssh(args: List[str], cwd: str) -> str:
        """OpenSSH client."""
        if not args:
            return ColorOutput.error("ssh: missing host")
        
        try:
            # Pass through to system ssh
            subprocess.run(['ssh'] + args)
            return ""
        except FileNotFoundError:
            return ColorOutput.error("ssh: command not found. Install OpenSSH client.")
        except Exception as e:
            return ColorOutput.error(f"ssh: {e}")
    
    @staticmethod
    def scp(args: List[str], cwd: str) -> str:
        """Secure copy."""
        if len(args) < 2:
            return ColorOutput.error("scp: missing source or destination")
        
        try:
            subprocess.run(['scp'] + args)
            return ""
        except FileNotFoundError:
            return ColorOutput.error("scp: command not found. Install OpenSSH client.")
        except Exception as e:
            return ColorOutput.error(f"scp: {e}")
    
    @staticmethod
    def nslookup(args: List[str], cwd: str) -> str:
        """Query DNS."""
        if not args:
            return ColorOutput.error("nslookup: missing host")
        
        host = args[0]
        
        try:
            result = socket.getaddrinfo(host, None)
            output = [f"Server:  Local DNS", f"Name:    {host}", ""]
            
            addresses = set()
            for family, _, _, _, sockaddr in result:
                addresses.add(sockaddr[0])
            
            for addr in addresses:
                output.append(f"Address: {addr}")
            
            return '\n'.join(output)
        except socket.gaierror as e:
            return ColorOutput.error(f"nslookup: {host}: {e}")
    
    @staticmethod
    def host(args: List[str], cwd: str) -> str:
        """DNS lookup utility."""
        return NetworkCommands.nslookup(args, cwd)