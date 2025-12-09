import {Client, DataSourceObjectResponse, isFullDatabase, isFullPage} from "@notionhq/client"
import {Config} from "@/config";
import {DiaryList, DiaryPage} from "@/types";
import {logger} from "@/logger";
import assert from "node:assert";
import {NotionToMarkdown} from "notion-to-md";
import pRetry, {makeRetriable} from "p-retry";
import {retryOptions} from "@/helpers";

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
        let database = await makeRetriable(this.notion.databases.retrieve,
            retryOptions)({database_id: this.config.database})
        assert(isFullDatabase(database))
        this.dataSourceId = database.data_sources[0].id
        logger.debug({dataSourceId: this.dataSourceId})
    }

    async getAllEntries() {
        let now = Date.now()
        let arr: DataSourceObjectResponse[] = []
        let nextCursor: string | null = ''
        while (nextCursor !== null) {
            logger.debug({nextCursor}, "Getting entries")
            let dataSource = await makeRetriable(this.notion.dataSources.query,
                retryOptions)({
                data_source_id: this.dataSourceId,
                start_cursor: nextCursor ? nextCursor : undefined,
                sorts: [
                    {
                        "timestamp": "last_edited_time",
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
        let page = await makeRetriable(this.notion.pages.retrieve,
            retryOptions)({page_id: id})
        assert(isFullPage(page))
        assert(this.config.fields.date in page.properties)
        assert(this.config.fields.wordCount in page.properties)
        let dateProp = page.properties[this.config.fields.date]
        assert(dateProp.type === 'date')
        let wordCountProp = page.properties[this.config.fields.wordCount]
        assert(wordCountProp.type === 'number')
        let date = dateProp.date?.start ?? '';
        logger.debug({id: page.id, date}, "Fetched page")
        return <DiaryPage>{
            page,
            date,
            wordCount: wordCountProp.number ?? 0
        }
    }

    async updatePage(diaryPage: DiaryPage) {
        await makeRetriable(this.notion.pages.update, retryOptions)({
            page_id: diaryPage.page.id, properties: {
                [this.config.fields.wordCount]: {type: 'number', number: diaryPage.wordCount}
            }
        })
        logger.debug({id: diaryPage.page.id, date: diaryPage.date}, "Updated page")
    }

    async pageToMarkdown(id: string) {
        const blocks = await pRetry(attemptNumber => {
            return this.n2m.pageToMarkdown(id)
        }, retryOptions);
        const mdString = this.n2m.toMarkdownString(blocks);
        return mdString.parent
    }
}

export function getStaleEntries(diaryList: DiaryList, baseTime: number) {
    return diaryList.entries.filter(value => {
        return Date.parse(value.last_edited_time) > baseTime
    })
}

export function diaryPagePropertiesToYamlHeader(page: DiaryPage) {
    return `---
date: ${page.date}
wordCount: ${page.wordCount}
---\n\n`
}