import {DataSourceObjectResponse, PageObjectResponse} from "@notionhq/client";

export interface DiaryList {
    entries: DataSourceObjectResponse[]
    fetchTime: number,
}

export interface DiaryPage {
    date: string
    wordCount: number
    page: PageObjectResponse
}