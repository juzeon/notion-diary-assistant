import YAML from "yaml"
import * as fs from "node:fs";

export interface Fields {
    date: string;
    wordCount: string;
}

export interface State {
    last: Last
}

export interface Last {
    wordCount: string;
    export: string;
}

export interface Config {
    token: string;
    database: string;
    fields: Fields;
}

export function loadConfig() {
    return YAML.parse(fs.readFileSync("config.yml", {encoding: 'utf-8'})) as Config
}

export function loadState() {
    return YAML.parse(fs.readFileSync("state.yml", {encoding: 'utf-8'})) as State
}

export function saveState(state: State) {
    fs.writeFileSync("state.yml", YAML.stringify(state), {encoding: "utf-8"})
}