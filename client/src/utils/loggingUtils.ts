import { isDevelopment } from "../env";

/**
 * Log only if in development mode
 */
export function developmentLog(message?: string, ...optionalParams: unknown[]) {
    if (!isDevelopment) return;

    if (optionalParams.length > 0) {
        console.log(message, ...optionalParams);
    } else {
        console.log(message);
    }

}