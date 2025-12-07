import os
import re
from pathlib import Path


class PathConverter:
    """Converst paths between Windows and Linux formats."""
    
    @staticmethod
    def to_windows(linux_path: str) -> str:
        if not linux_path:
            return os.getcwd()
        
        # Handle home directory
        if linux_path.startswith('~'):
            home = os.path.expanduser('~')
            linux_path = linux_path.replace('~', home, 1)
        
        match = re.match(r'^/([a-zA-Z])(/.*)?$', linux_path)
        if match:
            drive = match.group(1).upper()
            rest = match.group(2) or ''
            linux_path = f"{drive}:{rest}"
        
        match = re.match(r'^/mnt/([a-zA-Z])(/.*)?$', linux_path)
        if match:
            drive = match.group(1).upper()
            rest = match.group(2) or ''
            linux_path = f"{drive}:{rest}"
        
        windows_path = linux_path.replace('/', '\\')
        
        if not os.path.isabs(windows_path):
            windows_path = os.path.join(os.getcwd(), windows_path)
        
        return os.path.normpath(windows_path)
    
    @staticmethod
    def to_linux(windows_path: str) -> str:
        """Convert Windows-style path to Linux path."""
        if not windows_path:
            return os.getcwd().replace('\\', '/')
        
        # Handle drive letters
        match = re.match(r'^([a-zA-Z]):\\(.*)$', windows_path)
        if match:
            drive = match.group(1).lower()
            rest = match.group(2)
            windows_path = f"/{drive}/{rest}"
        
        # Replace backslashes with forward slashes
        return windows_path.replace('\\', '/')
    
    @staticmethod
    def expand_path(path: str) -> str:
        """Expand environment variables and user home in path."""
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        return PathConverter.to_windows(path)
    
    @staticmethod
    def glob_pattern(pattern: str) -> list:
        """Expand glob patterns."""
        from glob import glob
        expanded = PathConverter.to_windows(pattern)
        results = glob(expanded)
        return results if results else [pattern]