import {DataSourceObjectResponse} from "@notionhq/client";

export interface DiaryList {
    entries: DataSourceObjectResponse[]
    fetchTime: number,
}