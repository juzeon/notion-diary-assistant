import {Client, DataSourceObjectResponse, isFullDatabase, isFullPage} from "@notionhq/client"
import {Config} from "@/config";
import {DiaryList, DiaryPage} from "@/types";
import {logger} from "@/logger";
import assert from "node:assert";
import {NotionToMarkdown} from "notion-to-md";

export class NotionClient {
    notion: Client
    config: Config
    dataSourceId: string = ''
    n2m: NotionToMarkdown

    constructor(config: Config) {
        this.notion = new Client({auth: config.token})
        this.n2m = new NotionToMarkdown({notionClient: this.notion});
        this.config = config
    }

    async init() {
        let database = await this.notion.databases.retrieve({database_id: this.config.database})
        assert(isFullDatabase(database))
        this.dataSourceId = database.data_sources[0].id
        logger.debug({dataSourceId: this.dataSourceId})
    }

    async getAllEntries() {
        let now = Date.now()
        let startCursor = ''
        let arr: DataSourceObjectResponse[] = []
        let nextCursor: string | null = ''
        while (nextCursor !== null) {
            let dataSource = await this.notion.dataSources.query({
                data_source_id: this.dataSourceId,
                start_cursor: startCursor ? startCursor : undefined,
                sorts: [
                    {
                        "property": this.config.fields.date,
                        "direction": "descending"
                    }
                ]
            })
            arr.push(...dataSource.results as DataSourceObjectResponse[])
            nextCursor = dataSource.next_cursor
        }
        return <DiaryList>{fetchTime: now, entries: arr}
    }

    async getPage(id: string) {
        let page = await this.notion.pages.retrieve({page_id: id})
        assert(isFullPage(page))
        assert(this.config.fields.date in page.properties)
        assert(this.config.fields.wordCount in page.properties)
        let dateProp = page.properties[this.config.fields.date]
        assert(dateProp.type === 'date')
        let wordCountProp = page.properties[this.config.fields.wordCount]
        assert(wordCountProp.type === 'number')
        return <DiaryPage>{
            page,
            date: dateProp.date?.start ?? '',
            wordCount: wordCountProp.number ?? 0
        }
    }

    async updatePage(diaryPage: DiaryPage) {
        await this.notion.pages.update({
            page_id: diaryPage.page.id, properties: {
                [this.config.fields.wordCount]: {type: 'number', number: diaryPage.wordCount}
            }
        })
    }

    async pageToMarkdown(id: string) {
        const blocks = await this.n2m.pageToMarkdown(id);
        const mdString = this.n2m.toMarkdownString(blocks);
        return mdString.parent
    }
}

export function getStaleEntries(diaryList: DiaryList, baseTime: number) {
    return diaryList.entries.filter(value => {
        return Date.parse(value.last_edited_time) > baseTime
    })
}