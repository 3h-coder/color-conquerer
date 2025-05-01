import { HTMLElements } from "../env";

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

export function getOrCreateDomElement(id: string, parent?: HTMLElement) {
    let element = document.getElementById(id);
    if (!element) {
        element = document.createElement(HTMLElements.div);
        element.id = id;
        if (parent)
            parent.appendChild(element);
        else
            document.body.appendChild(element);
    }
    return element;
}

export interface ElementCenterPoint {
    x: number;
    y: number;
}

export function getElementCenterPoint(element: HTMLElement): ElementCenterPoint {
    const rect = element.getBoundingClientRect();
    return {
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2
    };
}