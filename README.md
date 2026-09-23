# sene-mcp

> **Work in progress — v0.1 under construction.** Lot 1 of 3: server skeleton, 2 tools, CI.

An [MCP](https://modelcontextprotocol.io) server that gives AI agents **safe, sourced tools** for farming cooperatives in Mali: crop pest guidance and market prices.

*Sɛnɛ* means "to farm" in Bambara.

## Design principles

- **Tools know, the agent talks.** Tools return facts from hand-written, cited pest sheets. They never generate advice.
- **Safety is enforced twice.** Every string of every pest sheet is scanned for dosages ("20 ml pour 15 litres", "1 sachet par pompe"…), active ingredients and trade names: the server refuses to load a sheet that fails, and CI also scans every tool output. The word list is a safety net, not a guarantee; sheets are written and reviewed by hand.
- **Honest data.** Prices in this version are fictitious demo data, flagged `is_demo_data: true` in every answer.
- **Ports and adapters.** The domain has no dependency on MCP, the database or any AI provider.

## Tools (lot 1)

| Tool | What it returns |
|---|---|
| `get_market_price` | Latest price per kg, in FCFA, per market (maize, rice, millet, sorghum) |
| `get_pest_sheet` | Symptoms, prevention, non-chemical control and sources for one pest |

Coming in lot 2: `diagnose_symptoms`, `analyze_photo`, `report_pest`, `publish_offer`, `search_offers`.

## Quick start

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/ibrahko/sene-mcp.git
cd sene-mcp
uv sync
uv run sene-mcp        # starts the server on stdio and waits for a client (Ctrl+C to stop)
```

On first run the server creates its SQLite database with demo data in a per-user folder
(Windows: `%LOCALAPPDATA%\sene-mcp`, macOS: `~/Library/Application Support/sene-mcp`,
Linux: `~/.local/share/sene-mcp`), whatever the current folder. Override with `SENE_DATA_DIR`
or `SENE_DATABASE_URL` (see `.env.example`). `uv run sene-mcp-seed` prepares it without
starting the server.

To use it from Claude Desktop or any MCP client, launch it with an absolute project path:

```bash
uv --directory /path/to/sene-mcp run sene-mcp
```

Try it with the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector uv run sene-mcp
```

## Development

```bash
uv run pytest               # tests, including pest-sheet safety and architecture checks
uv run ruff check .         # lint
uv run ruff format --check . # formatting
uv run mypy                 # types (strict)
uv run alembic upgrade head # migrations, for development
```

## License

MIT
