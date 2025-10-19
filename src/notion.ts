import {Client, DataSourceObjectResponse, isFullDatabase} from "@notionhq/client"
import {Config} from "@/config";
import {DiaryList} from "@/types";
import {logger} from "@/logger";

export class NotionClient {
    client: Client
    config: Config
    dataSourceId: string = ''

    constructor(config: Config) {
        this.client = new Client({auth: config.token})
        this.config = config
    }

    async init() {
        let database = await this.client.databases.retrieve({database_id: this.config.database})
        if (!isFullDatabase(database)) {
            throw new Error("not full database")
        }
        this.dataSourceId = database.data_sources[0].id
        logger.debug({dataSourceId: this.dataSourceId})
    }

    async getAllEntries() {
        let now = Date.now()
        let startCursor = ''
        let arr: DataSourceObjectResponse[] = []
        let nextCursor: string | null = ''
        while (nextCursor !== null) {
            let dataSource = await this.client.dataSources.query({
                data_source_id: this.dataSourceId,
                start_cursor: startCursor ? startCursor : undefined,
                sorts: [
                    {
                        "property": "日期",
                        "direction": "descending"
                    }
                ]
            })
            arr.push(...dataSource.results as DataSourceObjectResponse[])
            nextCursor = dataSource.next_cursor
        }
        return <DiaryList>{fetchTime: now, entries: arr}
    }
}

export function getStaleEntries(diaryList: DiaryList) {
    return diaryList.entries.filter(value => {
        return Date.parse(value.last_edited_time) > diaryList.fetchTime
    })
}