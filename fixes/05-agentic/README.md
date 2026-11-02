# Agentic Browsing + MCP

1. Site Settings → SEO → llms.txt: Enable ✓ and paste `llms.txt`.
2. Kaffora Newsletter → Configuration → **Expose this form to AI agents** (WebMCP) ✓.
3. Drag the **Schema.org JSON-LD** fragment (Kaffora Coffee collection) onto the page, set Name `Kaffora Coffee` and URL `http://kaffora.localhost:8080/`, Publish.
4. Instance Settings → Platform → **MCP Server** → Enabled. Endpoint: `http://localhost:8080/o/mcp`.
5. Claude Desktop: merge `claude_desktop_config.json` into your config file and restart Claude Desktop.
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Basic auth value, macOS/Linux: `printf '%s' 'user@example.com:password' | base64`
   - Basic auth value, PowerShell: `[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('user@example.com:password'))`
6. Prompt: *"List the pages of the Kaffora Coffee site and tell me which ones are missing an SEO description."*

Use a dedicated low-privilege user: the agent acts with that user's permissions.
