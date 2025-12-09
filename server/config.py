import yaml
import os
import logging
import sys

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "config/settings.yaml")

class Config:
    def __init__(self):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            self._raw = yaml.safe_load(f)

        # Read server section
        server = self._raw.get("server", {})
        self.server_name = server.get("name", "oracle_performance_mcp")
        self.server_port = server.get("port", 8300)

        # Logging configuration
        log_config = self._raw.get("logging", {})
        self.log_level = log_config.get("level", "INFO").upper()
        self.show_tool_calls = log_config.get("show_tool_calls", True)
        self.show_sql_queries = log_config.get("show_sql_queries", False)
        
        # DEBUG: Force print to stderr to see in Docker logs
        sys.stderr.write(f"[CONFIG-DEBUG] show_sql_queries = {self.show_sql_queries}\n")
        sys.stderr.flush()

        # Oracle analysis configuration
        oracle_analysis = self._raw.get("oracle_analysis", {})
        self.output_preset = oracle_analysis.get("output_preset", "standard").lower()

        # Database presets
        self.database_presets = self._raw.get("database_presets", {})

    def get_db_preset(self, name):
        if name not in self.database_presets:
            raise KeyError(f"DB preset '{name}' is not defined in settings.yaml")
        return self.database_presets[name]

config = Config()
