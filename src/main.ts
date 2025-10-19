import {NotionClient} from "@/notion";
import {loadConfig} from "@/config";
import {logger} from "@/logger";

;(async () => {
    let config = loadConfig()
    let notion = new NotionClient(config)
    await notion.init()
    let diaryList = await notion.getAllEntries()
    logger.info(diaryList.entries[0])
})()