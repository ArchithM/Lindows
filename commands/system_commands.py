import os
import sys
import platform
import datetime
import subprocess
import psutil
from typing import List
from utils import ColorOutput


class SystemCommands:
    
    @staticmethod
    def clear(args: List[str], cwd: str) -> str:
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        return "\033[H\033[J"  # ANSI escape code for clear
    
    @staticmethod
    def echo(args: List[str], cwd: str) -> str:
        """Echo text to terminal."""
        no_newline = '-n' in args
        args = [a for a in args if a != '-n']
        text = ' '.join(args)
        
        # Handle escape sequences
        text = text.replace('\\n', '\n')
        text = text.replace('\\t', '\t')
        text = text.replace('\\\\', '\\')
        
        # Expand environment variables
        for key, value in os.environ.items():
            text = text.replace(f'${key}', value)
            text = text.replace(f'${{{key}}}', value)
        
        return text if no_newline else text
    
    @staticmethod
    def date(args: List[str], cwd: str) -> str:
        """Display current date and time."""
        now = datetime.datetime.now()
        
        if args and args[0].startswith('+'):
            # Custom format
            fmt = args[0][1:]
            fmt = fmt.replace('%Y', now.strftime('%Y'))
            fmt = fmt.replace('%m', now.strftime('%m'))
            fmt = fmt.replace('%d', now.strftime('%d'))
            fmt = fmt.replace('%H', now.strftime('%H'))
            fmt = fmt.replace('%M', now.strftime('%M'))
            fmt = fmt.replace('%S', now.strftime('%S'))
            return fmt
        
        return now.strftime('%a %b %d %H:%M:%S %Z %Y')
    
    @staticmethod
    def whoami(args: List[str], cwd: str) -> str:
        """Display current username."""
        return os.environ.get('USERNAME', os.environ.get('USER', 'unknown'))
    
    @staticmethod
    def hostname(args: List[str], cwd: str) -> str:
        """Display system hostname."""
        return platform.node()
    
    @staticmethod
    def uname(args: List[str], cwd: str) -> str:
        """Display system information."""
        if not args or '-a' in args:
            return f"{platform.system()} {platform.node()} {platform.release()} {platform.version()} {platform.machine()}"
        
        parts = []
        if '-s' in args:
            parts.append(platform.system())
        if '-n' in args:
            parts.append(platform.node())
        if '-r' in args:
            parts.append(platform.release())
        if '-v' in args:
            parts.append(platform.version())
        if '-m' in args:
            parts.append(platform.machine())
        
        return ' '.join(parts) if parts else platform.system()
    
    @staticmethod
    def uptime(args: List[str], cwd: str) -> str:
        """Display system uptime."""
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        now = datetime.datetime.now()
        uptime = now - boot_time
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days > 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
        parts.append(f"{minutes} min")
        
        users = len(psutil.users())
        load = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
        
        return f" {now.strftime('%H:%M:%S')} up {', '.join(parts)}, {users} user{'s' if users != 1 else ''}, load average: {load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}"
    
    @staticmethod
    def ps(args: List[str], cwd: str) -> str:
        """Display running processes."""
        show_all = '-a' in args or '-e' in args or 'aux' in ''.join(args)
        
        output = []
        output.append(f"{'PID':>7} {'CPU%':>6} {'MEM%':>6} {'NAME':<30}")
        output.append("-" * 55)
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                if show_all or info['name'] not in ['System Idle Process', 'System']:
                    output.append(f"{info['pid']:>7} {info['cpu_percent']:>6.1f} {info['memory_percent']:>6.1f} {info['name']:<30}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return '\n'.join(output[:50] if not show_all else output)  # Limit output
    
    @staticmethod
    def top(args: List[str], cwd: str) -> str:
        """Display dynamic process view (snapshot)."""
        output = []
        
        # System info
        cpu_percent = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        output.append(f"CPU: {cpu_percent}%  |  Memory: {mem.percent}% ({mem.used // (1024**3)}GB / {mem.total // (1024**3)}GB)  |  Swap: {swap.percent}%")
        output.append("")
        output.append(f"{'PID':>7} {'USER':<12} {'CPU%':>6} {'MEM%':>6} {'STATUS':<10} {'NAME':<25}")
        output.append("-" * 75)
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        for info in processes[:20]:
            username = (info['username'] or 'N/A').split('\\')[-1][:12]
            output.append(f"{info['pid']:>7} {username:<12} {info['cpu_percent'] or 0:>6.1f} {info['memory_percent'] or 0:>6.1f} {info['status']:<10} {info['name'][:25]:<25}")
        
        return '\n'.join(output)
    
    @staticmethod
    def kill(args: List[str], cwd: str) -> str:
        """Kill a process by PID."""
        if not args:
            return ColorOutput.error("kill: missing PID")
        
        signal_num = 9  # Default SIGKILL
        pids = []
        
        for arg in args:
            if arg.startswith('-'):
                try:
                    signal_num = int(arg[1:])
                except ValueError:
                    pass
            else:
                try:
                    pids.append(int(arg))
                except ValueError:
                    return ColorOutput.error(f"kill: invalid PID: {arg}")
        
        output = []
        for pid in pids:
            try:
                proc = psutil.Process(pid)
                proc.terminate() if signal_num == 15 else proc.kill()
            except psutil.NoSuchProcess:
                output.append(ColorOutput.error(f"kill: ({pid}) - No such process"))
            except psutil.AccessDenied:
                output.append(ColorOutput.error(f"kill: ({pid}) - Operation not permitted"))
        
        return '\n'.join(output)
    
    @staticmethod
    def df(args: List[str], cwd: str) -> str:
        """Display disk space usage."""
        human_readable = '-h' in args
        
        output = []
        output.append(f"{'Filesystem':<20} {'Size':>10} {'Used':>10} {'Avail':>10} {'Use%':>6} {'Mounted on':<15}")
        
        def format_size(size):
            if not human_readable:
                return str(size)
            for unit in ['B', 'K', 'M', 'G', 'T']:
                if size < 1024:
                    return f"{size:.1f}{unit}"
                size /= 1024
            return f"{size:.1f}P"
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                output.append(
                    f"{partition.device:<20} "
                    f"{format_size(usage.total):>10} "
                    f"{format_size(usage.used):>10} "
                    f"{format_size(usage.free):>10} "
                    f"{usage.percent:>5}% "
                    f"{partition.mountpoint:<15}"
                )
            except PermissionError:
                continue
        
        return '\n'.join(output)
    
    @staticmethod
    def du(args: List[str], cwd: str) -> str:
        """Estimate file space usage."""
        from utils import PathConverter
        
        human_readable = '-h' in args
        summarize = '-s' in args
        paths = [a for a in args if not a.startswith('-')] or ['.']
        
        def format_size(size):
            if not human_readable:
                return str(size // 1024)  # Default to KB
            for unit in ['B', 'K', 'M', 'G', 'T']:
                if size < 1024:
                    return f"{size:.1f}{unit}"
                size /= 1024
            return f"{size:.1f}P"
        
        def get_dir_size(path):
            total = 0
            for entry in os.scandir(path):
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat().st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total += get_dir_size(entry.path)
                except PermissionError:
                    pass
            return total
        
        output = []
        for path in paths:
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            if not os.path.exists(full_path):
                output.append(ColorOutput.error(f"du: cannot access '{path}': No such file or directory"))
                continue
            
            if os.path.isfile(full_path):
                size = os.path.getsize(full_path)
                output.append(f"{format_size(size)}\t{path}")
            else:
                if summarize:
                    size = get_dir_size(full_path)
                    output.append(f"{format_size(size)}\t{path}")
                else:
                    for root, dirs, files in os.walk(full_path):
                        size = sum(os.path.getsize(os.path.join(root, f)) for f in files if os.path.exists(os.path.join(root, f)))
                        output.append(f"{format_size(size)}\t{PathConverter.to_linux(root)}")
        
        return '\n'.join(output)
    
    @staticmethod
    def free(args: List[str], cwd: str) -> str:
        """Display memory usage."""
        human_readable = '-h' in args
        
        def format_size(size):
            if not human_readable:
                return str(size // 1024)  # KB
            for unit in ['B', 'K', 'M', 'G', 'T']:
                if size < 1024:
                    return f"{size:.1f}{unit}"
                size /= 1024
            return f"{size:.1f}P"
        
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        output = []
        output.append(f"{'':>12} {'total':>12} {'used':>12} {'free':>12} {'shared':>12} {'buff/cache':>12} {'available':>12}")
        output.append(
            f"{'Mem:':>12} "
            f"{format_size(mem.total):>12} "
            f"{format_size(mem.used):>12} "
            f"{format_size(mem.free):>12} "
            f"{format_size(getattr(mem, 'shared', 0)):>12} "
            f"{format_size(getattr(mem, 'buffers', 0) + getattr(mem, 'cached', 0)):>12} "
            f"{format_size(mem.available):>12}"
        )
        output.append(
            f"{'Swap:':>12} "
            f"{format_size(swap.total):>12} "
            f"{format_size(swap.used):>12} "
            f"{format_size(swap.free):>12}"
        )
        
        return '\n'.join(output)
    
    @staticmethod
    def env(args: List[str], cwd: str) -> str:
        """Display environment variables."""
        output = []
        for key, value in sorted(os.environ.items()):
            output.append(f"{key}={value}")
        return '\n'.join(output)
    
    @staticmethod
    def export(args: List[str], cwd: str) -> str:
        """Set environment variables."""
        if not args:
            return SystemCommands.env(args, cwd)
        
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                os.environ[key] = value
            else:
                # Just mark as exported (no-op in Python)
                pass
        
        return ""
    
    @staticmethod
    def unset(args: List[str], cwd: str) -> str:
        """Unset environment variables."""
        for arg in args:
            if arg in os.environ:
                del os.environ[arg]
        return ""
    
    @staticmethod
    def which(args: List[str], cwd: str) -> str:
        """Locate a command."""
        if not args:
            return ColorOutput.error("which: missing argument")
        
        output = []
        for cmd in args:
            result = shutil.which(cmd) if 'shutil' in dir() else None
            if result is None:
                import shutil as sh
                result = sh.which(cmd)
            
            if result:
                output.append(result)
            else:
                output.append(ColorOutput.error(f"which: no {cmd} in PATH"))
        
        return '\n'.join(output)
    
    @staticmethod
    def history(args: List[str], cwd: str, command_history: List[str]) -> str:
        """Display command history."""
        count = 10
        if args:
            try:
                count = int(args[0])
            except ValueError:
                pass
        
        output = []
        start = max(0, len(command_history) - count)
        for i, cmd in enumerate(command_history[start:], start + 1):
            output.append(f" {i:4d}  {cmd}")
        
        return '\n'.join(output)
    
    @staticmethod
    def alias(args: List[str], cwd: str, aliases: dict) -> str:
        """Manage command aliases."""
        if not args:
            return '\n'.join(f"alias {k}='{v}'" for k, v in aliases.items())
        
        for arg in args:
            if '=' in arg:
                name, value = arg.split('=', 1)
                value = value.strip("'\"")
                aliases[name] = value
            else:
                if arg in aliases:
                    return f"alias {arg}='{aliases[arg]}'"
        
        return ""
    
    @staticmethod
    def unalias(args: List[str], cwd: str, aliases: dict) -> str:
        """Remove command aliases."""
        for arg in args:
            if arg in aliases:
                del aliases[arg]
        return ""


import shutil