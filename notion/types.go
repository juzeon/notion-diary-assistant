package notion

import "encoding/json"

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
	CreatedTime    string              `json:"created_time"`
	CreatedBy      PartialUser         `json:"created_by"`
	LastEditedTime string              `json:"last_edited_time"`
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
	ID          string            `json:"id"`
	Type        string            `json:"type"`
	Name        string            `json:"name,omitempty"` // Name is not in the response for all endpoints
	Title       *json.RawMessage  `json:"title,omitempty"`
	RichText    *json.RawMessage  `json:"rich_text,omitempty"`
	Number      *NumberProperty   `json:"number,omitempty"`
	Select      *SelectProperty   `json:"select,omitempty"`
	MultiSelect *SelectProperty   `json:"multi_select,omitempty"`
	Status      *SelectProperty   `json:"status,omitempty"`
	Date        *json.RawMessage  `json:"date,omitempty"`
	Checkbox    *json.RawMessage  `json:"checkbox,omitempty"`
	URL         *json.RawMessage  `json:"url,omitempty"`
	Email       *json.RawMessage  `json:"email,omitempty"`
	PhoneNumber *json.RawMessage  `json:"phone_number,omitempty"`
	Formula     *FormulaProperty  `json:"formula,omitempty"`
	Relation    *RelationProperty `json:"relation,omitempty"`
	// Add other property types as needed (e.g., rollup, files, created_by, etc.)
}

// NumberProperty holds the configuration for a "number" type property.
type NumberProperty struct {
	Format string `json:"format"` // e.g., "number", "number_with_commas", "percent"
}

// SelectProperty holds the configuration for "select", "multi_select", and "status" properties.
type SelectProperty struct {
	Options []SelectOption `json:"options"`
}

// SelectOption is one of the available options for a select-style property.
type SelectOption struct {
	ID    string `json:"id"`
	Name  string `json:"name"`
	Color string `json:"color"`
}

// FormulaProperty holds the configuration for a "formula" type property.
type FormulaProperty struct {
	Expression string `json:"expression"`
}

// RelationProperty holds the configuration for a "relation" type property.
type RelationProperty struct {
	DatabaseID string `json:"database_id"`
	Type       string `json:"type"` // "single_property" or "dual_property"
	// Depending on the type, there might be a single_property or dual_property object here.
	// Using json.RawMessage for simplicity if you don't need to inspect them.
	SingleProperty *json.RawMessage `json:"single_property,omitempty"`
	DualProperty   *json.RawMessage `json:"dual_property,omitempty"`
}

// --- Previously defined structs (unchanged) ---

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
	URL        string `json:"url"`
	ExpiryTime string `json:"expiry_time"`
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
