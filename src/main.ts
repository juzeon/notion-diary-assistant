import {getStaleEntries, NotionClient} from "@/notion";
import {loadConfig, loadState} from "@/config";
import dedupe from "dedupe";
import pRetry from "p-retry"

;(async () => {
    let config = loadConfig()
    let state = loadState()
    let notion = new NotionClient(config)
    await notion.init()
    let diaryList = await notion.getAllEntries()
    let entries = dedupe([...getStaleEntries(diaryList, state.last.export),
        ...getStaleEntries(diaryList, state.last.wordCount)], input => {
        return input.id
    })

})()