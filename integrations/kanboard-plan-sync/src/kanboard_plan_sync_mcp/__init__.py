"""Plan-centric MCP facade for kanboard-plan-sync.

This server exposes only plan-centric tools. Raw Kanboard API methods
(``createTask``, ``updateTask``, ``moveTaskPosition``, ...) are never surfaced;
they remain implementation details of the core adapter.
"""

__version__ = "0.1.0"
