package config

import (
	"github.com/samber/lo"
	"github.com/spf13/viper"
)

type config struct {
	Token    string
	Database string
	Fields   fields
}
type fields struct {
	Date      string
	WordCount string
}

var Config config

func init() {
	viper.SetConfigName("config")
	viper.AddConfigPath(".")
	lo.Must0(viper.ReadInConfig())
	lo.Must0(viper.Unmarshal(&Config))
}
