/**
 * Capitalizes the first letter of each word in a string and replaces underscores with spaces.
 * @param input The string to transform.
 * @returns The transformed string.
 */
export function capitalizeAndReplaceUnderscores(input: string): string {
    return input
        .replace(/_/g, ' ') // Replace underscores with spaces
        .toLowerCase()
        .replace(/\b\w/g, char => char.toUpperCase()); // Capitalize the first letter of each word
}