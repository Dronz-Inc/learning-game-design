# learning-game-design

A monorepo of the games I'm building as part of my game design course. Each game lives in its own sub-folder.

## Structure

```
learning-game-design/
├── .claude/
│   └── settings.json     # Claude Code plugins, referenced so they work in cloud/mobile
├── <game-1>/             # one folder per game
├── <game-2>/
└── ...
```

Add a new game by creating a sub-folder for it at the repo root.

## Claude Code plugins

This repo commits `.claude/settings.json` so the same Claude Code plugins I use locally are
available in cloud environments (claude.ai/code and the mobile app). On clone, Claude Code reads
`enabledPlugins` + `extraKnownMarketplaces` and installs them automatically from their public
GitHub marketplaces — nothing is vendored, so the repo stays small and updates flow from upstream.

Enabled plugins: arscontexta, claude-notifications-go, compound-engineering, design-and-refine,
frontend-design, last30days, linear, playground, ralph-loop.
