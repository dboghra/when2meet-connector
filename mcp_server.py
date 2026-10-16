"""MCP server that lets Claude check a When2meet event.

It reuses get_names() and normalize() from when2meet.py, so the original
script keeps working on its own.

Run by hand (it will just sit and wait for an MCP client):
    python mcp_server.py
"""

import requests
from mcp.server.mcpserver import MCPServer

from when2meet import get_names, normalize

mcp = MCPServer("when2meet")


def _fetch(url):
    """Return (names, None) on success or (None, error message) on failure."""
    if "when2meet.com" not in url:
        return None, "That doesn't look like a When2meet URL."
    try:
        return get_names(url), None
    except requests.RequestException as error:
        return None, f"Could not load that page: {error}"


# The docstring of each tool is what Claude reads to decide when to call it.
@mcp.tool()
def list_responders(url: str) -> str:
    """List the people who have filled out a When2meet event.

    Args:
        url: The full When2meet link, e.g. https://www.when2meet.com/?1234567-AbCde
    """
    names, error = _fetch(url)
    if error:
        return error
    if not names:
        return "Nobody has responded yet."
    listing = "\n".join(f"- {n.strip()}" for n in names)
    return f"{len(names)} people responded:\n{listing}"


@mcp.tool()
def check_missing(url: str, expected_names: list[str]) -> str:
    """Check which of the expected people have NOT yet filled out a When2meet.

    Matching ignores capitalization and extra spaces.

    Args:
        url: The full When2meet link.
        expected_names: Names of the people you're waiting on.
    """
    names, error = _fetch(url)
    if error:
        return error
    responded = {normalize(n) for n in names}
    missing = [n for n in expected_names if normalize(n) not in responded]
    if not missing:
        return "Everyone has responded!"
    return f"Still waiting on: {', '.join(missing)}"


if __name__ == "__main__":
    mcp.run()  # stdio transport: talks to the client over stdin/stdout
