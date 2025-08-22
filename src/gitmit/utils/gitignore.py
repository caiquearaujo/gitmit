"""Module for parsing and matching gitignore patterns."""

import os
import re
from pathlib import Path
from typing import List, Optional


class GitignoreParser:
    """Parser for gitignore-style pattern files."""

    def __init__(self, base_path: Path):
        """Initialize the gitignore parser.
        
        Args:
            base_path: The base path (repository root) for pattern matching.
        """
        self.base_path = Path(base_path)
        self.patterns: List[tuple[str, bool]] = []
        
    def load_patterns(self, file_path: Path) -> None:
        """Load patterns from a gitignore file.
        
        Args:
            file_path: Path to the gitignore file.
        """
        if not file_path.exists():
            return
            
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                    
                # Handle negation patterns
                negated = False
                if line.startswith('!'):
                    negated = True
                    line = line[1:]
                    
                # Convert gitignore pattern to regex
                pattern = self._gitignore_to_regex(line)
                if pattern:
                    self.patterns.append((pattern, negated))
    
    def _gitignore_to_regex(self, pattern: str) -> Optional[str]:
        """Convert a gitignore pattern to a regex pattern.
        
        Args:
            pattern: The gitignore pattern.
            
        Returns:
            A compiled regex pattern or None if invalid.
        """
        if not pattern:
            return None
            
        # Escape special regex characters except those used in gitignore
        pattern = pattern.replace('\\', '\\\\')
        pattern = pattern.replace('.', '\\.')
        pattern = pattern.replace('+', '\\+')
        pattern = pattern.replace('^', '\\^')
        pattern = pattern.replace('$', '\\$')
        pattern = pattern.replace('(', '\\(')
        pattern = pattern.replace(')', '\\)')
        pattern = pattern.replace('{', '\\{')
        pattern = pattern.replace('}', '\\}')
        pattern = pattern.replace('|', '\\|')
        
        # Handle directory-only patterns (ending with /)
        is_dir_only = pattern.endswith('/')
        if is_dir_only:
            pattern = pattern[:-1]
            
        # Handle absolute patterns (starting with /)
        if pattern.startswith('/'):
            pattern = pattern[1:]
            pattern = '^' + pattern
        else:
            # Pattern can match at any level
            pattern = '(^|.*/)'  + pattern
            
        # Convert gitignore wildcards to regex
        pattern = pattern.replace('**/', '(.*/)?')
        pattern = pattern.replace('*', '[^/]*')
        pattern = pattern.replace('?', '[^/]')
        
        # Handle character ranges [abc] or [!abc]
        pattern = re.sub(r'\[([^\]]+)\]', lambda m: '[' + m.group(1).replace('!', '^') + ']', pattern)
        
        if is_dir_only:
            pattern = pattern + '(/.*)?$'
        else:
            pattern = pattern + '(/.*)?$'
            
        return pattern
    
    def should_ignore(self, file_path: str) -> bool:
        """Check if a file should be ignored based on loaded patterns.
        
        Args:
            file_path: The file path relative to the repository root.
            
        Returns:
            True if the file should be ignored, False otherwise.
        """
        # Normalize the path
        file_path = file_path.replace('\\', '/')
        
        # Start with not ignored
        ignored = False
        
        # Check each pattern in order (later patterns override earlier ones)
        for pattern, negated in self.patterns:
            try:
                if re.match(pattern, file_path):
                    ignored = not negated
            except re.error:
                # Skip invalid patterns
                continue
                
        return ignored
    
    @classmethod
    def from_file(cls, repo_path: Path, filename: str = '.gitmitignore') -> 'GitignoreParser':
        """Create a GitignoreParser from a gitignore file.
        
        Args:
            repo_path: The repository root path.
            filename: The name of the ignore file (default: .gitmitignore).
            
        Returns:
            A configured GitignoreParser instance.
        """
        parser = cls(repo_path)
        ignore_file = repo_path / filename
        parser.load_patterns(ignore_file)
        return parser