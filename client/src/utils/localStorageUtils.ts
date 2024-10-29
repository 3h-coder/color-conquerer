export function extractKey(key: string) {
    const value = localStorage.getItem(key);
    localStorage.removeItem(key);
    return value;
}