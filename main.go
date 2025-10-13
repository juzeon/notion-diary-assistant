package main

import (
	"github.com/samber/lo"
	"log/slog"
	"notion-diary-assistant/config"
	"notion-diary-assistant/notion"
)

func main() {
	slog.SetLogLoggerLevel(slog.LevelDebug)
	client := lo.Must(notion.NewClient(config.Config.Token, config.Config.Database))
	lo.Must(client.GetAllEntries())
}
