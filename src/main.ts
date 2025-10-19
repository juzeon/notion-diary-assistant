import {NotionClient} from "@/notion";
import {loadConfig, loadState} from "@/config";

;(async () => {
    let config = loadConfig()
    let state = loadState()
    let notion = new NotionClient(config)
    await notion.init()
    let diaryList = await notion.getAllEntries()

})()