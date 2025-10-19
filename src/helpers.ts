import {Options} from "p-retry";

export function countChineseCharacters(str: string): number {
    if (!str) {
        return 0;
    }
    const chineseCharRegex = /[\u4e00-\u9fff]/g;
    const matches = str.match(chineseCharRegex);
    return matches ? matches.length : 0;
}

export let retryOptions: Options = {
    retries: 5,
}