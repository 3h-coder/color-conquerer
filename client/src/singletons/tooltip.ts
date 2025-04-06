import React, { createElement } from "react";
import { createRoot, Root } from "react-dom/client";
import { EMPTY_STRING, HTMLElements } from "../env";
import { getOrCreateDomElement } from "../utils/domUtils";

export enum TooltipPosition {
    TOP,
    BOTTOM,
    LEFT,
    RIGHT,
    TOP_LEFT,
    BOTTOM_LEFT,
    TOP_RIGHT,
    BOTTOM_RIGHT,
}

export interface BindTooltipOptions {
    tooltipText?: string;
    position?: TooltipPosition;
    tooltipContentElement?: HTMLElement | React.ReactNode;
}

const EVENT_MOUSE_ENTER = "mouseenter";
const EVENT_MOUSE_LEAVE = "mouseleave";
const EVENT_TOUCH_START = "touchstart";
const EVENT_TOUCH_END = "touchend";

// Since the mouse can only be over one element at a time, we can only have one tooltip
// active at a time. This is a global variable to keep track of the active tooltip.
let activeTooltipElement: HTMLElement | null = null;
let activeReactRoot: Root | null = null;
// We're using a ùutation observer as the target element may be removed from the DOM
// and we need to clean up the tooltip in that case.
let observer: MutationObserver | null = null;

/** Utility method for the mouse hover to display a tooltip relative to the given target react reference */
export function bindTooltip(
    targetRef: React.RefObject<HTMLElement>,
    options: BindTooltipOptions = {}
) {
    if (!targetRef.current)
        return;

    const targetElement = targetRef.current;
    const { tooltipText, position, tooltipContentElement } = options;

    const showTooltip = () => {
        cleanupActiveTooltip();
        resetMutationObserver(targetElement);

        createActiveTooltip(tooltipContentElement, tooltipText);
        adjustTooltipPosition(targetElement, position);
    };

    const hideTooltip = () => {
        cleanupActiveTooltip();
    };

    targetElement.addEventListener(EVENT_MOUSE_ENTER, showTooltip);
    targetElement.addEventListener(EVENT_MOUSE_LEAVE, hideTooltip);
    targetElement.addEventListener(EVENT_TOUCH_START, showTooltip);
    targetElement.addEventListener(EVENT_TOUCH_END, hideTooltip);

    return () => {
        targetElement.removeEventListener(EVENT_MOUSE_ENTER, showTooltip);
        targetElement.removeEventListener(EVENT_MOUSE_LEAVE, hideTooltip);
        targetElement.removeEventListener(EVENT_TOUCH_START, showTooltip);
        targetElement.removeEventListener(EVENT_TOUCH_END, hideTooltip);
    };
}

// #region utility functions

function createActiveTooltip(
    tooltipContentElement: HTMLElement | React.ReactNode,
    tooltipText: string | undefined
) {
    let reactRoot: Root | null = null;

    const tooltipElement = document.createElement(HTMLElements.div);
    tooltipElement.className = "tooltip";

    if (tooltipContentElement instanceof HTMLElement) {
        tooltipElement.appendChild(tooltipContentElement);
    } else if (tooltipContentElement) {
        reactRoot = createRoot(tooltipElement);
        reactRoot.render(
            createElement(React.Fragment, null, tooltipContentElement)
        );
    } else {
        tooltipElement.innerText = tooltipText ?? EMPTY_STRING;
    }

    const tooltipOverlay = getTooltipOverlay();
    tooltipOverlay.appendChild(tooltipElement);

    activeTooltipElement = tooltipElement;
    activeReactRoot = reactRoot;
}

function cleanupActiveTooltip() {
    if (activeTooltipElement) {
        if (activeReactRoot) {
            activeReactRoot.unmount();
            activeReactRoot = null;
        }
        if (activeTooltipElement.parentElement) {
            activeTooltipElement.parentElement.removeChild(activeTooltipElement);
        }
        activeTooltipElement = null;
    }
}

function adjustTooltipPosition(
    targetElement: HTMLElement,
    position: TooltipPosition | undefined
) {
    setTimeout(() => {
        if (!activeTooltipElement) return;

        const targetElementRect = targetElement.getBoundingClientRect();
        const tooltipRect = activeTooltipElement.getBoundingClientRect();

        const { left, top } = calculateTooltipPosition(
            targetElementRect,
            tooltipRect,
            position ?? TooltipPosition.TOP
        );
        activeTooltipElement.style.left = left;
        activeTooltipElement.style.top = top;
    }, 20);
}

function getTooltipOverlay() {
    const tooltipRoot = getOrCreateDomElement("tooltip-root");
    return getOrCreateDomElement("tooltip-overlay", tooltipRoot);
}

function resetMutationObserver(targetElement: HTMLElement) {
    destroyMutationObserver();

    observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (
                mutation.type === "childList" &&
                !document.body.contains(targetElement)
            ) {
                cleanupActiveTooltip();
                destroyMutationObserver();
                break;
            }
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
}

function destroyMutationObserver() {
    observer?.disconnect();
    observer = null;
}

function calculateTooltipPosition(
    targetRect: DOMRect,
    tooltipRect: DOMRect,
    position: TooltipPosition
): { left: string; top: string; } {
    const spacing = 5; // Space between the tooltip and the target element

    switch (position) {
        case TooltipPosition.TOP:
            return {
                left: `${targetRect.left +
                    window.scrollX +
                    targetRect.width / 2 -
                    tooltipRect.width / 2
                    }px`,
                top: `${targetRect.top + window.scrollY - tooltipRect.height - spacing
                    }px`,
            };
        case TooltipPosition.BOTTOM:
            return {
                left: `${targetRect.left +
                    window.scrollX +
                    targetRect.width / 2 -
                    tooltipRect.width / 2
                    }px`,
                top: `${targetRect.bottom + window.scrollY + spacing}px`,
            };
        case TooltipPosition.LEFT:
            return {
                left: `${targetRect.left + window.scrollX - tooltipRect.width - spacing
                    }px`,
                top: `${targetRect.top +
                    window.scrollY +
                    targetRect.height / 2 -
                    tooltipRect.height / 2
                    }px`,
            };
        case TooltipPosition.RIGHT:
            return {
                left: `${targetRect.right + window.scrollX + spacing}px`,
                top: `${targetRect.top +
                    window.scrollY +
                    targetRect.height / 2 -
                    tooltipRect.height / 2
                    }px`,
            };
        case TooltipPosition.TOP_LEFT:
            return {
                left: `${targetRect.right + window.scrollX - tooltipRect.width}px`,
                top: `${targetRect.top + window.scrollY - tooltipRect.height - spacing
                    }px`,
            };
        case TooltipPosition.BOTTOM_LEFT:
            return {
                left: `${targetRect.right + window.scrollX - tooltipRect.width}px`,
                top: `${targetRect.bottom + window.scrollY + spacing}px`,
            };
        case TooltipPosition.TOP_RIGHT:
            return {
                left: `${targetRect.left + window.scrollX}px`,
                top: `${targetRect.top + window.scrollY - tooltipRect.height - spacing
                    }px`,
            };
        case TooltipPosition.BOTTOM_RIGHT:
            return {
                left: `${targetRect.left + window.scrollX}px`,
                top: `${targetRect.bottom + window.scrollY + spacing}px`,
            };
        default:
            return { left: "0px", top: "0px" };
    }
}

// #endregion
