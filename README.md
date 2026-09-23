# sene-mcp

> **Work in progress — v0.1 under construction.** Lot 1 of 3: server skeleton, 2 tools, CI.

An [MCP](https://modelcontextprotocol.io) server that gives AI agents **safe, sourced tools** for farming cooperatives in Mali: crop pest guidance and market prices.

*Sɛnɛ* means "to farm" in Bambara.

## Design principles

- **Tools know, the agent talks.** Tools return facts from hand-written, cited pest sheets. They never generate advice, so a product name or a dose cannot come out of a tool.
- **Safety is tested.** CI fails if any pest sheet lacks a source or contains a dosage or an active ingredient.
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
uv run sene-mcp        # starts the server on stdio; creates sene.db with demo data on first run
```

Try it with the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector uv run sene-mcp
```

## Development

```bash
uv run pytest          # tests, including pest-sheet safety checks
uv run ruff check .    # lint
uv run mypy            # types
```

## License

MIT
