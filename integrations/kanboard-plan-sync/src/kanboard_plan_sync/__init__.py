"""kanboard-plan-sync core.

Markdown plan documents are the source of truth. Kanboard is a projection of
their progress state. This package reads Markdown plans, builds an internal
sync manifest, and drives a Kanboard JSON-RPC projection. SQLite is never
written; JSON-RPC is the only write path.
"""

__version__ = "0.1.0"
