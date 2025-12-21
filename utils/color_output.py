from colorama import init, Fore, Back, Style
import re

init(autoreset=True)


class ColorOutput:
    """Handle colored terminal output."""
    
    COLORS = {
        'red': Fore.RED,
        'green': Fore.GREEN,
        'yellow': Fore.YELLOW,
        'blue': Fore.BLUE,
        'magenta': Fore.MAGENTA,
        'cyan': Fore.CYAN,
        'white': Fore.WHITE,
        'reset': Style.RESET_ALL,
        'bold': Style.BRIGHT,
    }
    
    # File type colors (like ls --color)
    FILE_COLORS = {
        'directory': Fore.BLUE + Style.BRIGHT,
        'executable': Fore.GREEN + Style.BRIGHT,
        'symlink': Fore.CYAN,
        'archive': Fore.RED,
        'image': Fore.MAGENTA,
        'audio': Fore.CYAN,
        'video': Fore.MAGENTA + Style.BRIGHT,
        'document': Fore.YELLOW,
        'code': Fore.GREEN,      
    }
    
    EXTENSIONS = {
        'archive': ['.zip', '.tar', '.gz', '.rar', '.7z', '.bz2', '.xz'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp'],
        'audio': ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.wma'],
        'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
        'document': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'],
        'code': ['.py', '.js', '.java', '.c', '.cpp', '.h', '.html', '.css', '.sh', '.bat'],
        'executable': ['.exe', '.msi', '.bat', '.cmd', '.com', '.ps1'],
    }
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Apply color to text."""
        color_code = cls.COLORS.get(color.lower(), '')
        return f"{color_code}{text}{Style.RESET_ALL}"
    
    @classmethod
    def get_file_color(cls, filename: str, is_dir: bool = False, is_exec: bool = False) -> str:
        """Get appropriate color for a file based on type."""
        if is_dir:
            return cls.FILE_COLORS['directory']
        if is_exec:
            return cls.FILE_COLORS['executable']
        
        ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        
        for file_type, extensions in cls.EXTENSIONS.items():
            if ext in extensions:
                return cls.FILE_COLORS.get(file_type, '')
        
        return ''
    
    @classmethod
    def success(cls, message: str) -> str:
        """Format success message."""
        return f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}"
    
    @classmethod
    def error(cls, message: str) -> str:
        """Format error message."""
        return f"{Fore.RED}✗ {message}{Style.RESET_ALL}"
    
    @classmethod
    def warning(cls, message: str) -> str:
        """Format warning message."""
        return f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}"
    
    @classmethod
    def info(cls, message: str) -> str:
        """Format info message."""
        return f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}"