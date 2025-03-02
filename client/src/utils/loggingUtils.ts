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

export function developmentWarn(message?: string, ...optionalParams: unknown[]) {
    if (!isDevelopment) return;

    if (optionalParams.length > 0) {
        console.warn(message, ...optionalParams);
    } else {
        console.warn(message);
    }
}

export function developmentErrorLog(message?: string, ...optionalParams: unknown[]) {
    if (!isDevelopment) return;

    if (optionalParams.length > 0) {
        console.error(message, ...optionalParams);
    } else {
        console.error(message);
    }
}