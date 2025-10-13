package notion

import (
	"errors"
	"fmt"
	"github.com/imroc/req/v3"
	"github.com/samber/lo"
	"log/slog"
	"time"
)

type Client struct {
	client     *req.Client
	database   string
	dataSource string
}

func NewClient(token string, database string) (*Client, error) {
	client := req.NewClient().SetTimeout(15 * time.Second).
		SetBaseURL("https://api.notion.com/v1").
		SetCommonHeaders(map[string]string{
			"Authorization":  "Bearer " + token,
			"Notion-Version": "2025-09-03",
		}).OnAfterResponse(func(client *req.Client, resp *req.Response) error {
		if resp.IsErrorState() {
			return errors.New(fmt.Sprintf("notion api error: %d", resp.GetStatusCode()))
		}
		return nil
	}).SetCommonRetryCount(3).SetCommonRetryFixedInterval(time.Second)
	var obj Object
	_, err := client.R().SetSuccessResult(&obj).Get("/databases/" + database)
	if err != nil {
		return nil, err
	}
	dataSource := obj.DataSources[0].ID
	slog.Debug("Init notion client", "data-source", dataSource)
	return &Client{
		client:     client,
		database:   database,
		dataSource: dataSource,
	}, nil
}
func (o *Client) GetAllEntries() (DiaryEntries, error) {
	t := time.Now()
	var query QueryDataSourceReq
	var arr []Object
	o.client.EnableDumpAll()
	for {
		var list List
		_, err := o.client.R().SetSuccessResult(&list).SetBody(&query).Post("/data_sources/" + o.dataSource + "/query")
		if err != nil {
			return DiaryEntries{}, err
		}
		arr = append(arr, list.Results...)
		if list.NextCursor == "" {
			break
		}
		query.StartCursor = list.NextCursor
	}
	slog.Debug("Retrieve from data source", "count", len(arr))
	return DiaryEntries{
		Entries:   arr,
		FetchTime: t,
	}, nil
}

//func (o *Client) UpdateWordCount(diaryEntries DiaryEntries) error {
//	arr:=GetStaleEntries(diaryEntries)
//
//}
func GetStaleEntries(diaryEntries DiaryEntries) []Object {
	return lo.Filter(diaryEntries.Entries, func(item Object, index int) bool {
		return item.LastEditedTime.After(diaryEntries.FetchTime)
	})
}
