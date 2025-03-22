/**
 * Creates a square 2D array of strings with the specified length, initialized with undefined values
 * @param length The length of each side of the square array
 * @returns A 2D array of strings initialized with undefined values
 */
export function create2DArray<T>(length: number): T[][] {
    return Array(length).fill(null).map(() => Array(length).fill(undefined));
}