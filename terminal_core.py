import os
import sys
import shlex
import subprocess
from typing import Dict, List, Tuple, Optional, Callable
from colorama import init, Fore, Style

from commands import FileCommands, SystemCommands, TextCommands, NetworkCommands
from utils import ColorOutput, PathConverter

init(autoreset=True)


class LinuxTerminal:
    
    def __init__(self):
        self.cwd = os.getcwd()
        self.env = dict(os.environ)
        self.history: List[str] = []
        self.aliases: Dict[str, str] = {
            'll': 'ls -la',
            'la': 'ls -a',
            'l': 'ls -CF',
            '..': 'cd ..',
            '...': 'cd ../..',
            'cls': 'clear',
            'md': 'mkdir',
            'rd': 'rmdir',
            'del': 'rm',
            'copy': 'cp',
            'move': 'mv',
            'type': 'cat',
            'dir': 'ls -la',
        }
        self.running = True
        
        # Command registry
        self.commands: Dict[str, Callable] = {
            # File commands
            'ls': lambda args: FileCommands.ls(args, self.cwd),
            'dir': lambda args: FileCommands.ls(['-la'] + args, self.cwd),
            'cd': self._cd,
            'pwd': lambda args: FileCommands.pwd(args, self.cwd),
            'mkdir': lambda args: FileCommands.mkdir(args, self.cwd),
            'rmdir': lambda args: FileCommands.rmdir(args, self.cwd),
            'rm': lambda args: FileCommands.rm(args, self.cwd),
            'cp': lambda args: FileCommands.cp(args, self.cwd),
            'mv': lambda args: FileCommands.mv(args, self.cwd),
            'touch': lambda args: FileCommands.touch(args, self.cwd),
            'chmod': lambda args: FileCommands.chmod(args, self.cwd),
            'ln': lambda args: FileCommands.ln(args, self.cwd),
            'find': lambda args: FileCommands.find(args, self.cwd),
            
            # Text commands
            'cat': lambda args: TextCommands.cat(args, self.cwd),
            'head': lambda args: TextCommands.head(args, self.cwd),
            'tail': lambda args: TextCommands.tail(args, self.cwd),
            'grep': lambda args: TextCommands.grep(args, self.cwd),
            'wc': lambda args: TextCommands.wc(args, self.cwd),
            'sort': lambda args: TextCommands.sort(args, self.cwd),
            'uniq': lambda args: TextCommands.uniq(args, self.cwd),
            'cut': lambda args: TextCommands.cut(args, self.cwd),
            'tr': lambda args: TextCommands.tr(args, self.cwd),
            'sed': lambda args: TextCommands.sed(args, self.cwd),
            'awk': lambda args: TextCommands.awk(args, self.cwd),
            'diff': lambda args: TextCommands.diff(args, self.cwd),
            
            # System commands
            'clear': lambda args: SystemCommands.clear(args, self.cwd),
            'echo': lambda args: SystemCommands.echo(args, self.cwd),
            'date': lambda args: SystemCommands.date(args, self.cwd),
            'whoami': lambda args: SystemCommands.whoami(args, self.cwd),
            'hostname': lambda args: SystemCommands.hostname(args, self.cwd),
            'uname': lambda args: SystemCommands.uname(args, self.cwd),
            'uptime': lambda args: SystemCommands.uptime(args, self.cwd),
            'ps': lambda args: SystemCommands.ps(args, self.cwd),
            'top': lambda args: SystemCommands.top(args, self.cwd),
            'kill': lambda args: SystemCommands.kill(args, self.cwd),
            'df': lambda args: SystemCommands.df(args, self.cwd),
            'du': lambda args: SystemCommands.du(args, self.cwd),
            'free': lambda args: SystemCommands.free(args, self.cwd),
            'env': lambda args: SystemCommands.env(args, self.cwd),
            'export': lambda args: SystemCommands.export(args, self.cwd),
            'unset': lambda args: SystemCommands.unset(args, self.cwd),
            'which': lambda args: SystemCommands.which(args, self.cwd),
            'history': lambda args: SystemCommands.history(args, self.cwd, self.history),
            'alias': lambda args: SystemCommands.alias(args, self.cwd, self.aliases),
            'unalias': lambda args: SystemCommands.unalias(args, self.cwd, self.aliases),
            
            # Network commands
            'ping': lambda args: NetworkCommands.ping(args, self.cwd),
            'curl': lambda args: NetworkCommands.curl(args, self.cwd),
            'wget': lambda args: NetworkCommands.wget(args, self.cwd),
            'ifconfig': lambda args: NetworkCommands.ifconfig(args, self.cwd),
            'ip': lambda args: NetworkCommands.ip(args, self.cwd),
            'netstat': lambda args: NetworkCommands.netstat(args, self.cwd),
            'ssh': lambda args: NetworkCommands.ssh(args, self.cwd),
            'scp': lambda args: NetworkCommands.scp(args, self.cwd),
            'nslookup': lambda args: NetworkCommands.nslookup(args, self.cwd),
            'host': lambda args: NetworkCommands.host(args, self.cwd),
            
            # Built-in commands
            'exit': self._exit,
            'quit': self._exit,
            'help': self._help,
            'man': self._help,
        }
    
    def _cd(self, args: List[str]) -> str:
        """Change directory."""
        new_cwd, output = FileCommands.cd(args, self.cwd)
        self.cwd = new_cwd
        os.chdir(self.cwd)
        return output
    
    def _exit(self, args: List[str]) -> str:
        """Exit the terminal."""
        self.running = False
        return ColorOutput.info("Goodbye!")
    
    def _help(self, args: List[str]) -> str:
        """Display help information."""
        if args:
            cmd = args[0]
            help_text = {
                'ls': 'ls [OPTIONS] [FILE]... - List directory contents\n  -l  long format\n  -a  show hidden\n  -h  human readable sizes',
                'cd': 'cd [DIR] - Change directory\n  cd ~  home directory\n  cd -  previous directory',
                'grep': 'grep [OPTIONS] PATTERN [FILE]... - Search for patterns\n  -i  ignore case\n  -r  recursive\n  -n  line numbers',
                'find': 'find [PATH] [OPTIONS] - Search for files\n  -name PATTERN  filename pattern\n  -type f|d  file or directory',
            }
            return help_text.get(cmd, f"No help available for '{cmd}'")
        
        output = [
            f"{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗",
            f"║           {Fore.YELLOW}Linux Terminal for Windows - Help{Fore.CYAN}                 ║",
            f"╠══════════════════════════════════════════════════════════════╣",
            f"║ {Fore.GREEN}File Commands:{Fore.CYAN}                                                ║",
            f"║   ls, cd, pwd, mkdir, rmdir, rm, cp, mv, touch, find, ln    ║",
            f"║                                                              ║",
            f"║ {Fore.GREEN}Text Commands:{Fore.CYAN}                                                ║",
            f"║   cat, head, tail, grep, wc, sort, uniq, cut, sed, awk,diff ║",
            f"║                                                              ║",
            f"║ {Fore.GREEN}System Commands:{Fore.CYAN}                                              ║",
            f"║   clear, echo, date, whoami, hostname, uname, uptime        ║",
            f"║   ps, top, kill, df, du, free, env, export, which, history  ║",
            f"║                                                              ║",
            f"║ {Fore.GREEN}Network Commands:{Fore.CYAN}                                             ║",
            f"║   ping, curl, wget, ifconfig, ip, netstat, ssh, scp         ║",
            f"║                                                              ║",
            f"║ {Fore.YELLOW}Type 'help <command>' for detailed help{Fore.CYAN}                      ║",
            f"║ {Fore.YELLOW}Use 'exit' or 'quit' to close the terminal{Fore.CYAN}                   ║",
            f"╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}",
        ]
        return '\n'.join(output)
    
    def get_prompt(self) -> str:
        """Generate the command prompt."""
        user = os.environ.get('USERNAME', os.environ.get('USER', 'user'))
        host = os.environ.get('COMPUTERNAME', 'localhost')
        path = PathConverter.to_linux(self.cwd)
        
        # Shorten home directory to ~
        home = PathConverter.to_linux(os.path.expanduser('~'))
        if path.startswith(home):
            path = '~' + path[len(home):]
        
        return f"{Fore.GREEN}{user}@{host}{Style.RESET_ALL}:{Fore.BLUE}{path}{Style.RESET_ALL}$ "
    
    def parse_command(self, command_line: str) -> Tuple[str, List[str]]:
        """Parse command line into command and arguments."""
        if not command_line.strip():
            return '', []
        
        # Handle aliases
        parts = command_line.strip().split(None, 1)
        if parts[0] in self.aliases:
            alias_expanded = self.aliases[parts[0]]
            if len(parts) > 1:
                command_line = f"{alias_expanded} {parts[1]}"
            else:
                command_line = alias_expanded
        
        try:
            tokens = shlex.split(command_line)
        except ValueError:
            tokens = command_line.split()
        
        if not tokens:
            return '', []
        
        return tokens[0], tokens[1:]
    
    def execute(self, command_line: str) -> str:
        """Execute a command and return output."""
        command_line = command_line.strip()
        
        if not command_line or command_line.startswith('#'):
            return ''
        
        # Add to history
        self.history.append(command_line)
        
        # Handle pipes (basic implementation)
        if '|' in command_line:
            return self._handle_pipe(command_line)
        
        # Handle output redirection
        if '>' in command_line or '>>' in command_line:
            return self._handle_redirect(command_line)
        
        cmd, args = self.parse_command(command_line)
        
        if cmd in self.commands:
            try:
                return self.commands[cmd](args)
            except Exception as e:
                return ColorOutput.error(f"{cmd}: {e}")
        else:
            # Try to execute as Windows command
            return self._execute_external(command_line)
    
    def _handle_pipe(self, command_line: str) -> str:
        """Handle piped commands."""
        commands = command_line.split('|')
        output = ''
        
        for cmd in commands:
            cmd = cmd.strip()
            if output:
                # Pass previous output as input (simplified)
                cmd_name, args = self.parse_command(cmd)
                # For now, just execute independently
                output = self.execute(cmd)
            else:
                output = self.execute(cmd)
        
        return output
    
    def _handle_redirect(self, command_line: str) -> str:
        """Handle output redirection."""
        append_mode = '>>' in command_line
        
        if append_mode:
            parts = command_line.split('>>')
        else:
            parts = command_line.split('>')
        
        if len(parts) != 2:
            return ColorOutput.error("Invalid redirection syntax")
        
        cmd = parts[0].strip()
        filepath = parts[1].strip()
        
        output = self.execute(cmd)
        
        try:
            full_path = PathConverter.to_windows(filepath)
            if not os.path.isabs(full_path):
                full_path = os.path.join(self.cwd, full_path)
            
            mode = 'a' if append_mode else 'w'
            with open(full_path, mode, encoding='utf-8') as f:
                f.write(output + '\n')
            return ''
        except Exception as e:
            return ColorOutput.error(f"Redirect failed: {e}")
    
    def _execute_external(self, command_line: str) -> str:
        """Execute external command."""
        try:
            result = subprocess.run(
                command_line,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.cwd
            )
            output = result.stdout + result.stderr
            return output.rstrip()
        except Exception as e:
            return ColorOutput.error(f"Command failed: {e}")
    
    def run(self):
        """Main terminal loop."""
        print(f"{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗")
        print(f"║      {Fore.YELLOW}Linux Terminal for Windows v1.0{Fore.CYAN}                        ║")
        print(f"║      {Fore.WHITE}Type 'help' for available commands{Fore.CYAN}                     ║")
        print(f"╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        print()
        
        try:
            import readline
        except ImportError:
            try:
                import pyreadline3 as readline
            except ImportError:
                readline = None
        
        while self.running:
            try:
                command = input(self.get_prompt())
                output = self.execute(command)
                if output:
                    print(output)
            except KeyboardInterrupt:
                print("\n^C")
            except EOFError:
                print()
                self._exit([])
            except Exception as e:
                print(ColorOutput.error(f"Error: {e}"))