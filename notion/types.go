package notion

import (
	"encoding/json"
	"time"
)

type DiaryEntries struct {
	Entries   []Object
	FetchTime time.Time
}
type QueryDataSourceReq struct {
	StartCursor string `json:"start_cursor,omitempty"`
}
type List struct {
	Results    []Object `json:"results"`
	NextCursor string   `json:"next_cursor"`
}
type Object struct {
	Object         string              `json:"object"`
	ID             string              `json:"id"`
	DataSources    []DataSource        `json:"data_sources,omitempty"`
	CreatedTime    time.Time           `json:"created_time"`
	CreatedBy      PartialUser         `json:"created_by"`
	LastEditedTime time.Time           `json:"last_edited_time"`
	LastEditedBy   PartialUser         `json:"last_edited_by"`
	Title          []RichText          `json:"title"`
	Description    []RichText          `json:"description"`
	Icon           any                 `json:"icon,omitempty"`  // Can be File Object or Emoji object
	Cover          *FileObject         `json:"cover,omitempty"` // Can be null
	Parent         Parent              `json:"parent"`
	URL            string              `json:"url"`
	Archived       bool                `json:"archived"`
	InTrash        bool                `json:"in_trash"`
	IsInline       bool                `json:"is_inline"`
	PublicURL      string              `json:"public_url"` // Can be null
	Properties     map[string]Property `json:"properties"` // only Page
}

// Property defines the schema for a single column in a database.
// The configuration for the property is determined by its "type".
type Property struct {
	ID          string           `json:"id"`
	Type        string           `json:"type"`
	Name        string           `json:"name,omitempty"` // Name is not in the response for all endpoints
	Title       *json.RawMessage `json:"title,omitempty"`
	RichText    *json.RawMessage `json:"rich_text,omitempty"`
	Number      int              `json:"number,omitempty"`
	Select      *SelectOption    `json:"select,omitempty"`
	MultiSelect []SelectOption   `json:"multi_select,omitempty"`
	Date        *DateProperty    `json:"date,omitempty"`
}

type DateProperty struct {
	Start    time.Time `json:"start"`
	End      time.Time `json:"end"`
	TimeZone string    `json:"time_zone,omitempty"`
}

// SelectOption is one of the available options for a select-style property.
type SelectOption struct {
	ID    string `json:"id"`
	Name  string `json:"name"`
	Color string `json:"color"`
}

// DataSource is a simplified reference to a data source.
type DataSource struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

// PartialUser represents a user object with only the ID.
type PartialUser struct {
	Object string `json:"object"`
	ID     string `json:"id"`
}

// RichText is a component of a Notion property that supports formatting.
type RichText struct {
	Type        string      `json:"type"`
	Text        *Text       `json:"text,omitempty"`
	Annotations Annotations `json:"annotations"`
	PlainText   string      `json:"plain_text"`
	Href        string      `json:"href,omitempty"`
}

// Text holds the content of a RichText object.
type Text struct {
	Content string `json:"content"`
	Link    *Link  `json:"link,omitempty"`
}

// Link represents a hyperlink in a RichText object.
type Link struct {
	URL string `json:"url"`
}

// Annotations specify the formatting of a RichText object.
type Annotations struct {
	Bold          bool   `json:"bold"`
	Italic        bool   `json:"italic"`
	Strikethrough bool   `json:"strikethrough"`
	Underline     bool   `json:"underline"`
	Code          bool   `json:"code"`
	Color         string `json:"color"`
}

// FileObject represents a file, either hosted by Notion or external.
type FileObject struct {
	Type     string        `json:"type"`
	File     *InternalFile `json:"file,omitempty"`
	External *ExternalFile `json:"external,omitempty"`
}

// InternalFile represents a file hosted by Notion.
type InternalFile struct {
	URL        string    `json:"url"`
	ExpiryTime time.Time `json:"expiry_time"`
}

// ExternalFile represents a file hosted on an external service.
type ExternalFile struct {
	URL string `json:"url"`
}

// Parent indicates the location of the database in the Notion workspace.
type Parent struct {
	Type       string `json:"type"`
	PageID     string `json:"page_id,omitempty"`
	DatabaseID string `json:"database_id,omitempty"`
	Workspace  bool   `json:"workspace,omitempty"`
}
