package config

import (
	"github.com/samber/lo"
	"github.com/spf13/viper"
	"time"
)

type config struct {
	Token    string
	Database string
	Fields   fields
	LastTime time.Time
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
func WriteConfig() {
	lo.Must0(viper.WriteConfig())
}
