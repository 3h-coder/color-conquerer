/**
 * Removes the specified DOM element from the page
 * after the specified delay using the setTimeout API.
 */
export function cleanup(element: HTMLElement, delayInMs: number) {
    setTimeout(() => element.remove(), delayInMs);
}

/** Removes the specified class name from the given element after the specified
 * delay using the setTimeout API.
 */
export function cleanupStyleClass(element: HTMLElement, styleClass: string, delayInMs: number) {
    setTimeout(() => element.classList.remove(styleClass), delayInMs);
}

export function delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}