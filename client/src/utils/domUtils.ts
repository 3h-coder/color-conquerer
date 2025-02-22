/**
 * Removes the specified DOM element from the page
 * after the specified delay using the setTimeout API.
 */
export function cleanup(element: HTMLElement, delayInMs: number) {
    setTimeout(() => element.remove(), delayInMs);
}