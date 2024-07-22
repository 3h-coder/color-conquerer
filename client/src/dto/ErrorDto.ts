export interface ErrorDto {
    error: string;
    displayToUser: boolean;
    socketConnectionKiller: boolean;
}

export function ParseErrorDto(data: unknown) {
    if (isErrorDto(data)) {
        return {
            error: data.error,
            displayToUser: data.displayToUser,
            socketConnectionKiller: data.socketConnectionKiller,
        } as ErrorDto;
    } else {
        return { error: data, displayToUser: false, socketConnectionKiller: false } as ErrorDto;
    }
}

function isErrorDto(data: unknown): data is ErrorDto {
    return typeof data === "object" && data !== null && data !== undefined &&
        "error" in data && "displayToUser" in data && "socketConnectionKiller" in data;
}