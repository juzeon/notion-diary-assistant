import pino from "pino";

export let logger = pino({
    transport: {
        target: 'pino-pretty'
    },
})
logger.level = 'trace'