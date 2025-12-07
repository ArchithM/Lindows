import os
import re
from typing import List
from utils import ColorOutput, PathConverter


class TextCommands:
    
    @staticmethod
    def cat(args: List[str], cwd: str) -> str:
        """Concatenate and display files."""
        if not args:
            return ColorOutput.error("cat: missing file operand")
        
        number_lines = '-n' in args
        args = [a for a in args if not a.startswith('-')]
        
        output = []
        line_num = 1
        
        for path in args:
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            if not os.path.exists(full_path):
                output.append(ColorOutput.error(f"cat: {path}: No such file or directory"))
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        if number_lines:
                            output.append(f"{line_num:6d}  {line.rstrip()}")
                            line_num += 1
                        else:
                            output.append(line.rstrip())
            except Exception as e:
                output.append(ColorOutput.error(f"cat: {path}: {e}"))
        
        return '\n'.join(output)
    
    @staticmethod
    def head(args: List[str], cwd: str) -> str:
        """Display first lines of a file."""
        lines_count = 10
        files = []
        
        i = 0
        while i < len(args):
            if args[i] == '-n' and i + 1 < len(args):
                try:
                    lines_count = int(args[i + 1])
                except ValueError:
                    pass
                i += 2
            elif args[i].startswith('-') and args[i][1:].isdigit():
                lines_count = int(args[i][1:])
                i += 1
            else:
                files.append(args[i])
                i += 1
        
        if not files:
            return ColorOutput.error("head: missing file operand")
        
        output = []
        for path in files:
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            if len(files) > 1:
                output.append(f"==> {path} <==")
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    for i, line in enumerate(f):
                        if i >= lines_count:
                            break
                        output.append(line.rstrip())
            except Exception as e:
                output.append(ColorOutput.error(f"head: {path}: {e}"))
        
        return '\n'.join(output)
    
    @staticmethod
    def tail(args: List[str], cwd: str) -> str:
        """Display last lines of a file."""
        lines_count = 10
        files = []
        
        i = 0
        while i < len(args):
            if args[i] == '-n' and i + 1 < len(args):
                try:
                    lines_count = int(args[i + 1])
                except ValueError:
                    pass
                i += 2
            elif args[i].startswith('-') and args[i][1:].isdigit():
                lines_count = int(args[i][1:])
                i += 1
            else:
                files.append(args[i])
                i += 1
        
        if not files:
            return ColorOutput.error("tail: missing file operand")
        
        output = []
        for path in files:
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            if len(files) > 1:
                output.append(f"==> {path} <==")
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                    for line in lines[-lines_count:]:
                        output.append(line.rstrip())
            except Exception as e:
                output.append(ColorOutput.error(f"tail: {path}: {e}"))
        
        return '\n'.join(output)
    
    @staticmethod
    def grep(args: List[str], cwd: str) -> str:
        """Search for patterns in files."""
        ignore_case = '-i' in args
        invert_match = '-v' in args
        count_only = '-c' in args
        line_numbers = '-n' in args
        recursive = '-r' in args or '-R' in args
        
        args = [a for a in args if not a.startswith('-')]
        
        if len(args) < 1:
            return ColorOutput.error("grep: missing pattern")
        
        pattern = args[0]
        files = args[1:] if len(args) > 1 else []
        
        flags = re.IGNORECASE if ignore_case else 0
        
        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            return ColorOutput.error(f"grep: invalid regex: {e}")
        
        def search_file(filepath, show_filename=False):
            results = []
            matches = 0
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    for line_num, line in enumerate(f, 1):
                        matched = bool(regex.search(line))
                        if matched != invert_match:
                            matches += 1
                            if not count_only:
                                prefix = ""
                                if show_filename:
                                    prefix = f"{ColorOutput.colorize(filepath, 'magenta')}:"
                                if line_numbers:
                                    prefix += f"{ColorOutput.colorize(str(line_num), 'green')}:"
                                
                                # Highlight matches
                                if not invert_match:
                                    highlighted = regex.sub(
                                        lambda m: ColorOutput.colorize(m.group(), 'red'),
                                        line.rstrip()
                                    )
                                else:
                                    highlighted = line.rstrip()
                                
                                results.append(f"{prefix}{highlighted}")
            except Exception as e:
                results.append(ColorOutput.error(f"grep: {filepath}: {e}"))
            
            if count_only:
                prefix = f"{filepath}:" if show_filename else ""
                results.append(f"{prefix}{matches}")
            
            return results
        
        output = []
        
        if not files:
            # Read from stdin (not implemented in this version)
            return ColorOutput.error("grep: reading from stdin not implemented")
        
        for path in files:
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            if recursive and os.path.isdir(full_path):
                for root, dirs, filenames in os.walk(full_path):
                    for filename in filenames:
                        filepath = os.path.join(root, filename)
                        output.extend(search_file(filepath, show_filename=True))
            elif os.path.isfile(full_path):
                output.extend(search_file(full_path, show_filename=len(files) > 1))
            else:
                output.append(ColorOutput.error(f"grep: {path}: No such file or directory"))
        
        return '\n'.join(output)
    
    @staticmethod
    def wc(args: List[str], cwd: str) -> str:
        """Word, line, and byte count."""
        show_lines = '-l' in args
        show_words = '-w' in args
        show_chars = '-c' in args
        show_bytes = '-m' in args
        
        if not any([show_lines, show_words, show_chars, show_bytes]):
            show_lines = show_words = show_chars = True
        
        files = [a for a in args if not a.startswith('-')]
        
        if not files:
            return ColorOutput.error("wc: missing file operand")
        
        output = []
        total_lines = total_words = total_chars = 0
        
        for path in files:
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    lines = content.count('\n')
                    words = len(content.split())
                    chars = len(content)
                    
                    total_lines += lines
                    total_words += words
                    total_chars += chars
                    
                    parts = []
                    if show_lines:
                        parts.append(f"{lines:8d}")
                    if show_words:
                        parts.append(f"{words:8d}")
                    if show_chars:
                        parts.append(f"{chars:8d}")
                    parts.append(path)
                    
                    output.append(' '.join(parts))
            except Exception as e:
                output.append(ColorOutput.error(f"wc: {path}: {e}"))
        
        if len(files) > 1:
            parts = []
            if show_lines:
                parts.append(f"{total_lines:8d}")
            if show_words:
                parts.append(f"{total_words:8d}")
            if show_chars:
                parts.append(f"{total_chars:8d}")
            parts.append("total")
            output.append(' '.join(parts))
        
        return '\n'.join(output)
    
    @staticmethod
    def sort(args: List[str], cwd: str) -> str:
        """Sort lines of text files."""
        reverse = '-r' in args
        numeric = '-n' in args
        unique = '-u' in args
        
        files = [a for a in args if not a.startswith('-')]
        
        if not files:
            return ColorOutput.error("sort: missing file operand")
        
        all_lines = []
        for path in files:
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    all_lines.extend(line.rstrip() for line in f)
            except Exception as e:
                return ColorOutput.error(f"sort: {path}: {e}")
        
        if numeric:
            def key_func(x):
                try:
                    return float(x.split()[0]) if x.split() else 0
                except ValueError:
                    return 0
            all_lines.sort(key=key_func, reverse=reverse)
        else:
            all_lines.sort(reverse=reverse)
        
        if unique:
            all_lines = list(dict.fromkeys(all_lines))
        
        return '\n'.join(all_lines)
    
    @staticmethod
    def uniq(args: List[str], cwd: str) -> str:
        """Report or omit repeated lines."""
        count = '-c' in args
        duplicate_only = '-d' in args
        unique_only = '-u' in args
        
        files = [a for a in args if not a.startswith('-')]
        
        if not files:
            return ColorOutput.error("uniq: missing file operand")
        
        output = []
        for path in files:
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = [line.rstrip() for line in f]
                
                prev_line = None
                line_count = 0
                
                for i, line in enumerate(lines):
                    if line == prev_line:
                        line_count += 1
                    else:
                        if prev_line is not None:
                            if (not duplicate_only and not unique_only) or \
                               (duplicate_only and line_count > 1) or \
                               (unique_only and line_count == 1):
                                if count:
                                    output.append(f"{line_count:7d} {prev_line}")
                                else:
                                    output.append(prev_line)
                        prev_line = line
                        line_count = 1
                
                # Handle last line
                if prev_line is not None:
                    if (not duplicate_only and not unique_only) or \
                       (duplicate_only and line_count > 1) or \
                       (unique_only and line_count == 1):
                        if count:
                            output.append(f"{line_count:7d} {prev_line}")
                        else:
                            output.append(prev_line)
            except Exception as e:
                output.append(ColorOutput.error(f"uniq: {path}: {e}"))
        
        return '\n'.join(output)
    
    @staticmethod
    def cut(args: List[str], cwd: str) -> str:
        """Remove sections from each line."""
        delimiter = '\t'
        fields = None
        chars = None
        
        i = 0
        files = []
        while i < len(args):
            if args[i] == '-d' and i + 1 < len(args):
                delimiter = args[i + 1]
                i += 2
            elif args[i] == '-f' and i + 1 < len(args):
                fields = args[i + 1]
                i += 2
            elif args[i] == '-c' and i + 1 < len(args):
                chars = args[i + 1]
                i += 2
            elif not args[i].startswith('-'):
                files.append(args[i])
                i += 1
            else:
                i += 1
        
        if not files:
            return ColorOutput.error("cut: missing file operand")
        
        def parse_range(spec):
            """Parse field/character specification."""
            result = []
            for part in spec.split(','):
                if '-' in part:
                    start, end = part.split('-', 1)
                    start = int(start) if start else 1
                    end = int(end) if end else 1000
                    result.extend(range(start, end + 1))
                else:
                    result.append(int(part))
            return sorted(set(result))
        
        output = []
        for path in files:
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        line = line.rstrip()
                        if fields:
                            parts = line.split(delimiter)
                            selected = [parts[i-1] for i in parse_range(fields) if i <= len(parts)]
                            output.append(delimiter.join(selected))
                        elif chars:
                            selected = [line[i-1] for i in parse_range(chars) if i <= len(line)]
                            output.append(''.join(selected))
                        else:
                            output.append(line)
            except Exception as e:
                output.append(ColorOutput.error(f"cut: {path}: {e}"))
        
        return '\n'.join(output)
    
    @staticmethod
    def tr(args: List[str], cwd: str) -> str:
        """Translate or delete characters."""
        delete = '-d' in args
        squeeze = '-s' in args
        args = [a for a in args if not a.startswith('-')]
        
        if len(args) < 1:
            return ColorOutput.error("tr: missing operand")
        
        set1 = args[0]
        set2 = args[1] if len(args) > 1 else ''
        
        # This is a simplified version - would need stdin in real implementation
        return ColorOutput.info("tr: reading from stdin not implemented. Use with pipes.")
    
    @staticmethod
    def sed(args: List[str], cwd: str) -> str:
        """Stream editor for filtering and transforming text."""
        in_place = '-i' in args
        args = [a for a in args if a != '-i']
        
        if len(args) < 1:
            return ColorOutput.error("sed: missing script")
        
        script = args[0]
        files = args[1:] if len(args) > 1 else []
        
        # Parse sed command (simplified - only s/// supported)
        match = re.match(r's([/|#])(.+?)\1(.+?)\1([g])?', script)
        if not match:
            return ColorOutput.error(f"sed: invalid script: {script}")
        
        delimiter, pattern, replacement, flags = match.groups()
        regex_flags = 0 if 'g' in (flags or '') else 0
        
        try:
            regex = re.compile(pattern)
        except re.error as e:
            return ColorOutput.error(f"sed: invalid regex: {e}")
        
        output = []
        for path in files:
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                if 'g' in (flags or ''):
                    result = regex.sub(replacement, content)
                else:
                    result = regex.sub(replacement, content, count=1)
                
                if in_place:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(result)
                else:
                    output.append(result.rstrip())
            except Exception as e:
                output.append(ColorOutput.error(f"sed: {path}: {e}"))
        
        return '\n'.join(output)
    
    @staticmethod
    def awk(args: List[str], cwd: str) -> str:
        """Pattern scanning and processing (simplified)."""
        if len(args) < 1:
            return ColorOutput.error("awk: missing program")
        
        program = args[0]
        files = args[1:] if len(args) > 1 else []
        
        # Very simplified awk - only supports print with field references
        if not files:
            return ColorOutput.error("awk: missing file operand")
        
        output = []
        
        # Parse simple print statement
        print_match = re.match(r"\{?\s*print\s*(.*?)\s*\}?", program)
        if not print_match:
            return ColorOutput.error("awk: only simple print statements supported")
        
        print_spec = print_match.group(1) or '$0'
        
        for path in files:
            full_path = PathConverter.to_windows(path)
            if not os.path.isabs(full_path):
                full_path = os.path.join(cwd, full_path)
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        fields = [''] + line.rstrip().split()  # $0 is the whole line
                        fields[0] = line.rstrip()
                        
                        result_parts = []
                        for part in print_spec.split(','):
                            part = part.strip()
                            if part.startswith('$'):
                                try:
                                    idx = int(part[1:])
                                    if idx < len(fields):
                                        result_parts.append(fields[idx])
                                except ValueError:
                                    result_parts.append(part)
                            else:
                                result_parts.append(part.strip('"\''))
                        
                        output.append(' '.join(result_parts))
            except Exception as e:
                output.append(ColorOutput.error(f"awk: {path}: {e}"))
        
        return '\n'.join(output)
    
    @staticmethod
    def diff(args: List[str], cwd: str) -> str:
        """Compare files line by line."""
        import difflib
        
        files = [a for a in args if not a.startswith('-')]
        
        if len(files) < 2:
            return ColorOutput.error("diff: missing file operand")
        
        file1, file2 = files[:2]
        
        path1 = PathConverter.to_windows(file1)
        path2 = PathConverter.to_windows(file2)
        if not os.path.isabs(path1):
            path1 = os.path.join(cwd, path1)
        if not os.path.isabs(path2):
            path2 = os.path.join(cwd, path2)
        
        try:
            with open(path1, 'r', encoding='utf-8', errors='replace') as f:
                lines1 = f.readlines()
            with open(path2, 'r', encoding='utf-8', errors='replace') as f:
                lines2 = f.readlines()
            
            diff = difflib.unified_diff(lines1, lines2, fromfile=file1, tofile=file2)
            output = []
            for line in diff:
                line = line.rstrip()
                if line.startswith('+'):
                    output.append(ColorOutput.colorize(line, 'green'))
                elif line.startswith('-'):
                    output.append(ColorOutput.colorize(line, 'red'))
                elif line.startswith('@'):
                    output.append(ColorOutput.colorize(line, 'cyan'))
                else:
                    output.append(line)
            
            return '\n'.join(output) if output else ""
        except Exception as e:
            return ColorOutput.error(f"diff: {e}")