import os
import shutil
import stat
import datetime
from pathlib import Path
from typing import List, Optional
from utils import ColorOutput, PathConverter


class FileCommands:
    """Linux-style file commands for Windows."""
    
    @staticmethod
    def ls(args: List[str], cwd: str) -> str:
        """List directory contents."""
        show_all = False
        show_long = False
        show_human = False
        recursive = False
        paths = []
        
        # Parse arguments
        for arg in args:
            if arg.startswith('-'):
                if 'a' in arg:
                    show_all = True
                if 'l' in arg:
                    show_long = True
                if 'h' in arg:
                    show_human = True
                if 'R' in arg:
                    recursive = True
            else:
                paths.append(arg)
        
        if not paths:
            paths = ['.']
        
        output = []
        
        for path in paths:
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            if not os.path.exists(full_path):
                output.append(ColorOutput.error(f"ls: cannot access '{path}': No such file or directory"))
                continue
            
            if os.path.isfile(full_path):
                output.append(FileCommands._format_file_entry(full_path, show_long, show_human))
            else:
                if len(paths) > 1:
                    output.append(f"\n{path}:")
                
                entries = FileCommands._list_directory(full_path, show_all, show_long, show_human)
                output.extend(entries)
        
        return '\n'.join(output)
    
    @staticmethod
    def _list_directory(path: str, show_all: bool, show_long: bool, show_human: bool) -> List[str]:
        """List contents of a directory."""
        entries = []
        try:
            items = os.listdir(path)
            if not show_all:
                items = [i for i in items if not i.startswith('.')]
            items.sort(key=str.lower)
            
            for item in items:
                full_path = os.path.join(path, item)
                entry = FileCommands._format_file_entry(full_path, show_long, show_human)
                entries.append(entry)
        except PermissionError:
            entries.append(ColorOutput.error(f"ls: cannot open directory: Permission denied"))
        
        return entries
    
    @staticmethod
    def _format_file_entry(path: str, show_long: bool, show_human: bool) -> str:
        """Format a single file entry."""
        name = os.path.basename(path)
        is_dir = os.path.isdir(path)
        is_exec = os.access(path, os.X_OK) and not is_dir
        
        color = ColorOutput.get_file_color(name, is_dir, is_exec)
        colored_name = f"{color}{name}{ColorOutput.COLORS['reset']}"
        
        if is_dir:
            colored_name += '/'
        
        if not show_long:
            return colored_name
        
        # Long format
        try:
            stat_info = os.stat(path)
            mode = FileCommands._format_mode(stat_info.st_mode, is_dir)
            nlink = stat_info.st_nlink
            size = stat_info.st_size
            mtime = datetime.datetime.fromtimestamp(stat_info.st_mtime)
            
            if show_human:
                size = FileCommands._human_readable_size(size)
            else:
                size = str(size)
            
            return f"{mode} {nlink:3d} {size:>8} {mtime.strftime('%b %d %H:%M')} {colored_name}"
        except:
            return colored_name
    
    @staticmethod
    def _format_mode(mode: int, is_dir: bool) -> str:
        """Format file mode string."""
        result = 'd' if is_dir else '-'
        
        perms = [
            (stat.S_IRUSR, 'r'), (stat.S_IWUSR, 'w'), (stat.S_IXUSR, 'x'),
            (stat.S_IRGRP, 'r'), (stat.S_IWGRP, 'w'), (stat.S_IXGRP, 'x'),
            (stat.S_IROTH, 'r'), (stat.S_IWOTH, 'w'), (stat.S_IXOTH, 'x'),
        ]
        
        for perm, char in perms:
            result += char if mode & perm else '-'
        
        return result
    
    @staticmethod
    def _human_readable_size(size: int) -> str:
        """Convert size to human readable format."""
        for unit in ['B', 'K', 'M', 'G', 'T']:
            if size < 1024:
                return f"{size:.1f}{unit}" if unit != 'B' else f"{size}{unit}"
            size /= 1024
        return f"{size:.1f}P"
    
    @staticmethod
    def cd(args: List[str], cwd: str) -> tuple:
        """Change directory. Returns (new_cwd, output_message)."""
        if not args:
            new_path = os.path.expanduser('~')
        elif args[0] == '-':
            new_path = os.environ.get('OLDPWD', cwd)
        else:
            new_path = PathConverter.to_windows(args[0])
            if not os.path.isabs(new_path):
                new_path = os.path.join(cwd, new_path)
        
        new_path = os.path.normpath(new_path)
        
        if not os.path.exists(new_path):
            return cwd, ColorOutput.error(f"cd: {args[0] if args else '~'}: No such file or directory")
        
        if not os.path.isdir(new_path):
            return cwd, ColorOutput.error(f"cd: {args[0]}: Not a directory")
        
        os.environ['OLDPWD'] = cwd
        return new_path, ""
    
    @staticmethod
    def pwd(args: List[str], cwd: str) -> str:
        """Print working directory."""
        return PathConverter.to_linux(cwd)
    
    @staticmethod
    def mkdir(args: List[str], cwd: str) -> str:
        """Create directories."""
        if not args:
            return ColorOutput.error("mkdir: missing operand")
        
        create_parents = '-p' in args
        args = [a for a in args if not a.startswith('-')]
        
        output = []
        for path in args:
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            try:
                if create_parents:
                    os.makedirs(full_path, exist_ok=True)
                else:
                    os.mkdir(full_path)
            except FileExistsError:
                output.append(ColorOutput.error(f"mkdir: cannot create directory '{path}': File exists"))
            except PermissionError:
                output.append(ColorOutput.error(f"mkdir: cannot create directory '{path}': Permission denied"))
            except Exception as e:
                output.append(ColorOutput.error(f"mkdir: {e}"))
        
        return '\n'.join(output)
    
    @staticmethod
    def rmdir(args: List[str], cwd: str) -> str:
        """Remove empty directories."""
        if not args:
            return ColorOutput.error("rmdir: missing operand")
        
        output = []
        for path in args:
            if path.startswith('-'):
                continue
            
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            try:
                os.rmdir(full_path)
            except FileNotFoundError:
                output.append(ColorOutput.error(f"rmdir: failed to remove '{path}': No such file or directory"))
            except OSError:
                output.append(ColorOutput.error(f"rmdir: failed to remove '{path}': Directory not empty"))
            except Exception as e:
                output.append(ColorOutput.error(f"rmdir: {e}"))
        
        return '\n'.join(output)
    
    @staticmethod
    def rm(args: List[str], cwd: str) -> str:
        """Remove files or directories."""
        if not args:
            return ColorOutput.error("rm: missing operand")
        
        recursive = False
        force = False
        
        paths = []
        for arg in args:
            if arg.startswith('-'):
                if 'r' in arg or 'R' in arg:
                    recursive = True
                if 'f' in arg:
                    force = True
            else:
                paths.append(arg)
        
        output = []
        for path in paths:
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            if not os.path.exists(full_path):
                if not force:
                    output.append(ColorOutput.error(f"rm: cannot remove '{path}': No such file or directory"))
                continue
            
            try:
                if os.path.isdir(full_path):
                    if recursive:
                        shutil.rmtree(full_path)
                    else:
                        output.append(ColorOutput.error(f"rm: cannot remove '{path}': Is a directory"))
                else:
                    os.remove(full_path)
            except PermissionError:
                if not force:
                    output.append(ColorOutput.error(f"rm: cannot remove '{path}': Permission denied"))
            except Exception as e:
                if not force:
                    output.append(ColorOutput.error(f"rm: {e}"))
        
        return '\n'.join(output)
    
    @staticmethod
    def cp(args: List[str], cwd: str) -> str:
        """Copy files or directories."""
        recursive = False
        args_filtered = []
        
        for arg in args:
            if arg.startswith('-'):
                if 'r' in arg or 'R' in arg:
                    recursive = True
            else:
                args_filtered.append(arg)
        
        if len(args_filtered) < 2:
            return ColorOutput.error("cp: missing destination file operand")
        
        sources = args_filtered[:-1]
        dest = PathConverter.to_windows(args_filtered[-1])
        if not os.path.isabs(dest):
            dest = os.path.join(cwd, dest)
        
        output = []
        for source in sources:
            src_path = PathConverter.to_windows(source)
            if not os.path.isabs(src_path):
                src_path = os.path.join(cwd, src_path)
            
            if not os.path.exists(src_path):
                output.append(ColorOutput.error(f"cp: cannot stat '{source}': No such file or directory"))
                continue
            
            try:
                if os.path.isdir(src_path):
                    if not recursive:
                        output.append(ColorOutput.error(f"cp: -r not specified; omitting directory '{source}'"))
                        continue
                    dest_path = os.path.join(dest, os.path.basename(src_path)) if os.path.isdir(dest) else dest
                    shutil.copytree(src_path, dest_path)
                else:
                    dest_path = os.path.join(dest, os.path.basename(src_path)) if os.path.isdir(dest) else dest
                    shutil.copy2(src_path, dest_path)
            except Exception as e:
                output.append(ColorOutput.error(f"cp: {e}"))
        
        return '\n'.join(output)
    
    @staticmethod
    def mv(args: List[str], cwd: str) -> str:
        """Move/rename files or directories."""
        args_filtered = [a for a in args if not a.startswith('-')]
        
        if len(args_filtered) < 2:
            return ColorOutput.error("mv: missing destination file operand")
        
        sources = args_filtered[:-1]
        dest = PathConverter.to_windows(args_filtered[-1])
        if not os.path.isabs(dest):
            dest = os.path.join(cwd, dest)
        
        output = []
        for source in sources:
            src_path = PathConverter.to_windows(source)
            if not os.path.isabs(src_path):
                src_path = os.path.join(cwd, src_path)
            
            if not os.path.exists(src_path):
                output.append(ColorOutput.error(f"mv: cannot stat '{source}': No such file or directory"))
                continue
            
            try:
                dest_path = os.path.join(dest, os.path.basename(src_path)) if os.path.isdir(dest) else dest
                shutil.move(src_path, dest_path)
            except Exception as e:
                output.append(ColorOutput.error(f"mv: {e}"))
        
        return '\n'.join(output)
    
    @staticmethod
    def touch(args: List[str], cwd: str) -> str:
        """Create empty files or update timestamps."""
        if not args:
            return ColorOutput.error("touch: missing file operand")
        
        output = []
        for path in args:
            if path.startswith('-'):
                continue
            
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            try:
                Path(full_path).touch()
            except Exception as e:
                output.append(ColorOutput.error(f"touch: cannot touch '{path}': {e}"))
        
        return '\n'.join(output)
    
    @staticmethod
    def chmod(args: List[str], cwd: str) -> str:
        """Change file mode (limited Windows support)."""
        if len(args) < 2:
            return ColorOutput.error("chmod: missing operand")
        
        mode = args[0]
        files = args[1:]
        
        output = []
        for path in files:
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            if not os.path.exists(full_path):
                output.append(ColorOutput.error(f"chmod: cannot access '{path}': No such file or directory"))
                continue
            
            try:
                # Windows has limited chmod support
                if '+x' in mode or mode == '755' or mode == '777':
                    os.chmod(full_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                elif '-x' in mode or mode == '644':
                    os.chmod(full_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
            except Exception as e:
                output.append(ColorOutput.error(f"chmod: changing permissions of '{path}': {e}"))
        
        return '\n'.join(output)
    
    @staticmethod
    def ln(args: List[str], cwd: str) -> str:
        """Create links."""
        symbolic = '-s' in args
        args_filtered = [a for a in args if not a.startswith('-')]
        
        if len(args_filtered) < 2:
            return ColorOutput.error("ln: missing file operand")
        
        source = PathConverter.to_windows(args_filtered[0])
        target = PathConverter.to_windows(args_filtered[1])
        
        if not os.path.isabs(source):
            source = os.path.join(cwd, source)
        if not os.path.isabs(target):
            target = os.path.join(cwd, target)
        
        try:
            if symbolic:
                os.symlink(source, target)
            else:
                os.link(source, target)
            return ""
        except Exception as e:
            return ColorOutput.error(f"ln: failed to create link: {e}")
    
    @staticmethod
    def find(args: List[str], cwd: str) -> str:
        """Find files."""
        path = cwd
        name_pattern = None
        file_type = None
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-name' and i + 1 < len(args):
                name_pattern = args[i + 1]
                i += 2
            elif arg == '-type' and i + 1 < len(args):
                file_type = args[i + 1]
                i += 2
            elif not arg.startswith('-'):
                path = PathConverter.to_windows(arg)
                if not os.path.isabs(path):
                    path = os.path.join(cwd, path)
                i += 1
            else:
                i += 1
        
        output = []
        try:
            import fnmatch
            for root, dirs, files in os.walk(path):
                items = dirs + files if file_type is None else (
                    dirs if file_type == 'd' else files if file_type == 'f' else dirs + files
                )
                for item in items:
                    if name_pattern is None or fnmatch.fnmatch(item, name_pattern):
                        full_path = os.path.join(root, item)
                        output.append(PathConverter.to_linux(full_path))
        except Exception as e:
            output.append(ColorOutput.error(f"find: {e}"))
        
        return '\n'.join(output)