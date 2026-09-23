# sene-mcp

[English](README.md) · **Français**

> **Travail en cours — v0.1 en construction.** Lot 1 sur 3 : squelette du serveur, 2 outils, intégration continue.

Un serveur [MCP](https://modelcontextprotocol.io) qui donne aux agents IA des **outils sûrs et sourcés** pour les coopératives agricoles du Mali : conseils contre les ravageurs et prix des marchés.

*Sɛnɛ* signifie « cultiver » en bambara.

## Principes de conception

- **Les outils savent, l'agent parle.** Les outils renvoient des faits tirés de fiches ravageurs rédigées à la main et sourcées. Ils ne génèrent jamais de conseil.
- **La sécurité est contrôlée deux fois.** Chaque texte de chaque fiche est analysé pour y chercher des doses (« 20 ml pour 15 litres », « 1 sachet par pompe »…), des matières actives et des noms commerciaux : le serveur refuse de charger une fiche fautive, et l'intégration continue analyse aussi chaque réponse d'outil. La liste de mots est un filet de sécurité, pas une garantie : les fiches sont écrites et relues à la main.
- **Des données honnêtes.** Dans cette version, les prix sont des données de démonstration fictives, marquées `is_demo_data: true` dans chaque réponse.
- **Ports et adaptateurs.** Le cœur métier ne dépend ni de MCP, ni de la base de données, ni d'aucun fournisseur d'IA.

## Outils (lot 1)

| Outil | Ce qu'il renvoie |
|---|---|
| `get_market_price` | Dernier prix au kilo, en FCFA, par marché (maïs, riz, mil, sorgho) |
| `get_pest_sheet` | Symptômes, prévention, lutte non chimique et sources pour un ravageur |

Au lot 2 : `diagnose_symptoms`, `analyze_photo`, `report_pest`, `publish_offer`, `search_offers`.

## Démarrage rapide

Nécessite [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/ibrahko/sene-mcp.git
cd sene-mcp
uv sync
uv run sene-mcp        # démarre le serveur en stdio et attend un client (Ctrl+C pour arrêter)
```

Au premier lancement, le serveur crée sa base SQLite avec les données de démonstration dans un dossier propre à l'utilisateur (Windows : `%LOCALAPPDATA%\sene-mcp`, macOS : `~/Library/Application Support/sene-mcp`, Linux : `~/.local/share/sene-mcp`), quel que soit le dossier courant. Pour changer d'emplacement : `SENE_DATA_DIR` ou `SENE_DATABASE_URL` (voir `.env.example`). `uv run sene-mcp-seed` prépare la base sans démarrer le serveur.

Pour l'utiliser depuis Claude Desktop ou tout autre client MCP, lancez-le avec le chemin absolu du projet :

```bash
uv --directory /chemin/vers/sene-mcp run sene-mcp
```

Pour l'essayer avec MCP Inspector :

```bash
npx @modelcontextprotocol/inspector uv run sene-mcp
```

## Développement

```bash
uv run pytest               # tests, dont les contrôles de sécurité des fiches et d'architecture
uv run ruff check .         # analyse du code
uv run ruff format --check . # mise en forme
uv run mypy                 # types (mode strict)
uv run alembic upgrade head # migrations, pour le développement
```

## Auteur

**Ibrahima Koné** — ingénieur back-end Python et IA, Bamako, Mali
[GitHub](https://github.com/ibrahko) · [LinkedIn](https://www.linkedin.com/in/ibrahima-koné-632006a1)

## Licence

MIT © 2026 Ibrahima Koné
