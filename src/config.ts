import yaml from "js-yaml"
import * as fs from "node:fs";

export interface Fields {
    date: string;
    wordCount: string;
}

export interface Last {
    wordCount: string;
    export: string;
}

export interface Config {
    token: string;
    database: string;
    fields: Fields;
    last: Last;
}

export function loadConfig(){
    return yaml.load(fs.readFileSync("config.yml", {encoding: 'utf-8'})) as Config
}