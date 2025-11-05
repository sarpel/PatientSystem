class Logger {
    private isDev = (import.meta as any).env.MODE === 'development';

    debug(msg: string, ...args: any[]) {
        if (this.isDev) console.debug(`[DEBUG] ${msg}`, ...args);
    }

    info(msg: string, ...args: any[]) {
        if (this.isDev) console.log(`[INFO] ${msg}`, ...args);
    }

    error(msg: string, ...args: any[]) {
        console.error(`[ERROR] ${msg}`, ...args);
    }
}

export const logger = new Logger();