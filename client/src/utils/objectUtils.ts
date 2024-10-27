export function isNullOrUndefined(obj: unknown) {
    return obj === null || obj === undefined;
}

export function isNotNullNorUndefined(obj: unknown) {
    return !isNullOrUndefined(obj);
}