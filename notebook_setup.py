"""Windows Jupyter fix for MCP stdio subprocesses. Import this before agents."""

from __future__ import annotations

import io
import os
import sys
from contextlib import asynccontextmanager


def _patch_mcp_stdio() -> None:
    if sys.platform != "win32":
        return

    import mcp.client.stdio as mcp_stdio

    original = mcp_stdio.stdio_client

    @asynccontextmanager
    async def notebook_stdio_client(server, errlog=None):
        if errlog is None:
            errlog = sys.stderr
        try:
            errlog.fileno()
        except (AttributeError, io.UnsupportedOperation, NotImplementedError, ValueError, OSError):
            errlog = open(os.devnull, "w")
        async with original(server, errlog=errlog) as streams:
            yield streams

    mcp_stdio.stdio_client = notebook_stdio_client

    # agents.mcp captures stdio_client at import time — update that copy too.
    import agents.mcp.server as agents_mcp_server

    agents_mcp_server.stdio_client = notebook_stdio_client


_patch_mcp_stdio()
