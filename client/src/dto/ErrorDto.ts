export interface ErrorDto {
    error: string;
}

export function ParseErrorDto(data: unknown) {
    if (isErrorDto(data)) {
        return {
            error: data.error
        } as ErrorDto;
    } else {
        return { error: data } as ErrorDto;
    }
}

function isErrorDto(data: unknown): data is { error: string } {
    return typeof data === "object" && data !== null && "error" in data;
}