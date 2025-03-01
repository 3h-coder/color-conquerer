/**
 * Removes the specified DOM element from the page
 * after the specified delay using the setTimeout API.
 */
export function cleanup(element: HTMLElement, delayInMs: number) {
    setTimeout(() => element.remove(), delayInMs);
}

export function delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}