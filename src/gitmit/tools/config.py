"""Config display tool."""

import configparser
from pathlib import Path
from typing import Optional

from ..services.config import Services
from ..utils.terminal import Panel, display_info


class ConfigTool:
    """Config display tool."""

    def __init__(self, services: Services):
        """Initialize the config tool."""
        self.services = services
        self.config_path = Path(services.path)
        
    def _hide_sensitive(self, value: str, is_sensitive: bool = False) -> str:
        """Hide sensitive data or show empty values properly."""
        if not value or value.strip() == "":
            return "<empty>"
        if is_sensitive and value not in ["<your-google-api-key>", "<your-mysql-password>"]:
            return "<hidden>"
        if value in ["<your-google-api-key>", "<your-mysql-password>"]:
            return "<not set>"
        return value
    
    def _get_token_usage(self) -> tuple[Optional[int], Optional[str]]:
        """Get current month token usage for the active model.
        
        Returns:
            tuple: (token_count, model_name) or (None, None) if unavailable
        """
        try:
            if not self.services.database:
                return None, None
                
            # Get the current model from commit service
            model_name = getattr(self.services.commit, 'model', None)
            if not model_name:
                return None, None
                
            # Start database connection if needed
            if not self.services.database.connected:
                self.services.database.start()
            
            # Get the full model name for database query (e.g., "google/gemini-2.0-flash")
            commit_config = configparser.ConfigParser()
            commit_config.read(self.config_path)
            full_model = commit_config.get("models", "commit", fallback="")
            
            if full_model:
                tokens = self.services.database.current_month_tokens_used(full_model)
                return tokens, model_name
            
            return None, None
        except Exception:
            return None, None
    
    def run(self):
        """Run the config display tool."""
        # Show file status message
        file_created = getattr(self.services, 'file_created', False)
        if file_created:
            display_info(
                f"Config file created successfully. See at: [bold yellow]{self.config_path}[/bold yellow]"
            )
        else:
            display_info(
                f"Config file is available at [bold yellow]{self.config_path}[/bold yellow]"
            )
        
        # Read the config file
        config = configparser.ConfigParser()
        config.read(self.config_path)
        
        # Build configuration display lines
        lines = []
        
        # Environment section
        lines.append("[bold cyan]Environment:[/bold cyan]")
        lines.append(f"  Config File: [bold yellow]{self.config_path}[/bold yellow]")
        lines.append(f"  Permissions: [bold yellow]{oct(self.config_path.stat().st_mode)[-3:]}[/bold yellow]")
        lines.append("")
        
        # Models section
        commit_model = config.get("models", "commit", fallback="")
        resume_model = config.get("models", "resume", fallback="")
        
        lines.append("[bold cyan]Models:[/bold cyan]")
        lines.append(f"  Commit Model: [bold yellow]{self._hide_sensitive(commit_model)}[/bold yellow]")
        lines.append(f"  Resume Model: [bold yellow]{self._hide_sensitive(resume_model)}[/bold yellow]")
        
        # Add token usage if available
        token_usage, active_model = self._get_token_usage()
        if token_usage is not None and active_model is not None:
            lines.append(f"  Active Model: [bold yellow]{active_model}[/bold yellow]")
            lines.append(f"  Current Month Tokens: [bold yellow]{token_usage:,}[/bold yellow]")
        lines.append("")
        
        # Google section
        google_api_key = config.get("google", "api_key", fallback="")
        lines.append("[bold cyan]Google:[/bold cyan]")
        lines.append(f"  API Key: [bold yellow]{self._hide_sensitive(google_api_key, is_sensitive=True)}[/bold yellow]")
        lines.append("")
        
        # Ollama section
        ollama_host = config.get("ollama", "host", fallback="")
        lines.append("[bold cyan]Ollama:[/bold cyan]")
        lines.append(f"  Host: [bold yellow]{self._hide_sensitive(ollama_host)}[/bold yellow]")
        lines.append("")
        
        # MySQL section
        mysql_host = config.get("mysql", "host", fallback="")
        mysql_port = config.get("mysql", "port", fallback="")
        mysql_user = config.get("mysql", "user", fallback="")
        mysql_password = config.get("mysql", "password", fallback="")
        mysql_database = config.get("mysql", "database", fallback="")
        
        lines.append("[bold cyan]MySQL:[/bold cyan]")
        lines.append(f"  Host: [bold yellow]{self._hide_sensitive(mysql_host)}[/bold yellow]")
        lines.append(f"  Port: [bold yellow]{self._hide_sensitive(mysql_port)}[/bold yellow]")
        lines.append(f"  User: [bold yellow]{self._hide_sensitive(mysql_user)}[/bold yellow]")
        lines.append(f"  Password: [bold yellow]{self._hide_sensitive(mysql_password, is_sensitive=True)}[/bold yellow]")
        lines.append(f"  Database: [bold yellow]{self._hide_sensitive(mysql_database)}[/bold yellow]")
        
        # Check database connection status
        db_status = "Not configured"
        if self.services.database:
            try:
                if not self.services.database.connected:
                    self.services.database.start()
                db_status = "Connected" if self.services.database.connected else "Failed"
            except Exception:
                db_status = "Connection failed"
        
        lines.append(f"  Connection Status: [bold yellow]{db_status}[/bold yellow]")
        
        # Display all configuration in a panel
        display_info(Panel("\n".join(lines), title="Configuration"))