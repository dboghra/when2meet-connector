# when2meet-connector
Notifies you when everyone has filled out the when2meet

Install dependencies once:

```
python -m pip install -r requirements.txt
```

## Command-line script

```
python when2meet.py
```

Lists who has responded, then optionally waits (checking every 60 seconds)
until the names you give have all responded. Windows only (beep + pop-up).

## MCP server (use it from Claude)

An MCP server is a small program that offers "tools" to an AI app like Claude.
Claude reads each tool's name and description, and calls it when it's useful.
`mcp_server.py` offers two tools, reusing the code in `when2meet.py`:

- `list_responders(url)`: who has filled out the event
- `check_missing(url, expected_names)`: which expected people haven't yet

### Connect to Claude desktop

1. In Claude desktop: Settings > Developer > Edit Config. This opens
   `claude_desktop_config.json`.
2. Add an `mcpServers` entry next to the existing settings (keep what's there,
   and mind the commas). Use the full path to your Python and to the script:

```json
"mcpServers": {
  "when2meet": {
    "command": "C:\\Users\\Dreshta\\.pyenv\\pyenv-win\\versions\\3.10.11\\python.exe",
    "args": ["C:\\Users\\Dreshta\\Documents\\when2meet-connector\\mcp_server.py"]
  }
}
```

3. Fully quit Claude desktop (including from the system tray) and reopen it.
4. Ask: "Who has filled out https://www.when2meet.com/?XXXX-XXXXX?"

If the server doesn't appear, check the logs under `%APPDATA%\Claude\logs`.
