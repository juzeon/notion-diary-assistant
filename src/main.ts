import {diaryPagePropertiesToYamlHeader, getStaleEntries, NotionClient} from "@/notion";
import {loadConfig, loadState, saveState} from "@/config";
import dedupe from "dedupe";
import pLimit from "p-limit";
import {countChineseCharacters} from "@/helpers";
import * as fsPro from 'node:fs/promises';
import * as fs from "node:fs";
import * as path from "node:path";
import filenamify from "filenamify";
import {logger} from "@/logger";
import {DataSourceObjectResponse} from "@notionhq/client";


;(async () => {
    let config = loadConfig()
    let state = loadState()
    if (!fs.existsSync("diaries")) {
        await fsPro.mkdir("diaries")
    }
    let notion = new NotionClient(config)
    await notion.init()
    let diaryList = await notion.getAllEntries()

    // get and merge deduplicate entries based on different `last time`
    let entries = dedupe([...getStaleEntries(diaryList, state.last.export),
        ...getStaleEntries(diaryList, state.last.wordCount)], input => {
        return input.id
    })
    logger.info(`${entries.length} diaries need to be processed`)

    let limitNotion = pLimit(config.concurrency.notion)
    let promises: Promise<void>[] = entries.map(entry => {
        return limitNotion(() => processPage(notion, entry))
    })
    await Promise.allSettled(promises)
    let now = Date.now()
    state.last.wordCount = now
    state.last.export = now
    saveState(state)
})()

async function processPage(notion: NotionClient, entry: DataSourceObjectResponse) {
    let page = await notion.getPage(entry.id)
    let content = await notion.pageToMarkdown(entry.id)
    let wordCount = countChineseCharacters(content)
    page.wordCount = wordCount
    let filename = filenamify(page.date ? page.date : page.page.id) + '.md'
    await fsPro.writeFile(path.join("diaries", filename),
        diaryPagePropertiesToYamlHeader(page) + content, {encoding: "utf-8"})
    await notion.updatePage(page)
    logger.info(`Processed diary ${page.date} (${page.page.id})`)
}