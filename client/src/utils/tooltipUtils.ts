import React, { createElement } from "react";
import { createRoot, Root } from "react-dom/client";
import { EMPTY_STRING, HTMLElements } from "../env";
import { getOrCreateDomElement } from "./domUtils";

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

let activeTooltipElement: HTMLElement | null = null;
let activeReactRoot: Root | null = null;
let observer: MutationObserver | null = null;

export function bindTooltip(
    ref: React.RefObject<HTMLElement>,
    options: BindTooltipOptions = {}
) {
    const {
        tooltipText,
        position,
        tooltipContentElement,
    } = options;

    cleanupActiveTooltip();

    if (!ref.current) return;

    const element = ref.current;
    let tooltipElement: HTMLElement | null = null;
    let reactRoot: Root | null = null;

    const showTooltip = () => {
        cleanupActiveTooltip();

        ({ tooltipElement, reactRoot } = createActiveTooltip(tooltipElement, tooltipContentElement, reactRoot, tooltipText));

        // Defer position calculation slightly after the tooltip is rendered
        setTimeout(() => {
            if (!tooltipElement) return;

            const targetElementRect = element.getBoundingClientRect();
            const tooltipRect = tooltipElement.getBoundingClientRect();

            const { left, top } = calculateTooltipPosition(
                targetElementRect,
                tooltipRect,
                position ?? TooltipPosition.TOP
            );
            tooltipElement.style.left = left;
            tooltipElement.style.top = top;
        }, 20);
    };

    observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.type === "childList" && !document.body.contains(element)) {
                cleanupActiveTooltip();
                observer?.disconnect();
                observer = null;
                break;
            }
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });

    const hideTooltip = () => {
        cleanupActiveTooltip();
    };

    element.addEventListener("mouseenter", showTooltip);
    element.addEventListener("mouseleave", hideTooltip);

    return () => {
        element.removeEventListener("mouseenter", showTooltip);
        element.removeEventListener("mouseleave", hideTooltip);
    };
}

function createActiveTooltip(tooltipElement: HTMLElement | null, tooltipContentElement: string | number | boolean | HTMLElement | React.ReactElement<any, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | React.ReactPortal | null | undefined, reactRoot: Root | null, tooltipText: string | undefined) {
    tooltipElement = document.createElement(HTMLElements.div);
    tooltipElement.className = "tooltip";

    if (tooltipContentElement instanceof HTMLElement) {
        tooltipElement.appendChild(tooltipContentElement);
    } else if (tooltipContentElement) {
        reactRoot = createRoot(tooltipElement);
        reactRoot.render(createElement(React.Fragment, null, tooltipContentElement));
    } else {
        tooltipElement.innerText = tooltipText ?? EMPTY_STRING;
    }

    const tooltipOverlay = getTooltipOverlay();
    tooltipOverlay.appendChild(tooltipElement);

    // Update the shared reference to the active tooltip
    activeTooltipElement = tooltipElement;
    activeReactRoot = reactRoot;
    return { tooltipElement, reactRoot };
}

function getTooltipOverlay() {
    const tooltipRoot = getOrCreateDomElement("tooltip-root");
    return getOrCreateDomElement("tooltip-overlay", tooltipRoot);
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

function calculateTooltipPosition(
    targetRect: DOMRect,
    tooltipRect: DOMRect,
    position: TooltipPosition,
): { left: string; top: string; } {
    const spacing = 5; // Space between the tooltip and the target element

    switch (position) {
        case TooltipPosition.TOP:
            return {
                left: `${targetRect.left + window.scrollX + targetRect.width / 2 - tooltipRect.width / 2}px`,
                top: `${targetRect.top + window.scrollY - tooltipRect.height - spacing}px`,
            };
        case TooltipPosition.BOTTOM:
            return {
                left: `${targetRect.left + window.scrollX + targetRect.width / 2 - tooltipRect.width / 2}px`,
                top: `${targetRect.bottom + window.scrollY + spacing}px`,
            };
        case TooltipPosition.LEFT:
            return {
                left: `${targetRect.left + window.scrollX - tooltipRect.width - spacing}px`,
                top: `${targetRect.top + window.scrollY + targetRect.height / 2 - tooltipRect.height / 2}px`,
            };
        case TooltipPosition.RIGHT:
            return {
                left: `${targetRect.right + window.scrollX + spacing}px`,
                top: `${targetRect.top + window.scrollY + targetRect.height / 2 - tooltipRect.height / 2}px`,
            };
        case TooltipPosition.TOP_LEFT:
            return {
                left: `${targetRect.right + window.scrollX - tooltipRect.width}px`,
                top: `${targetRect.top + window.scrollY - tooltipRect.height - spacing}px`,
            };
        case TooltipPosition.BOTTOM_LEFT:
            return {
                left: `${targetRect.right + window.scrollX - tooltipRect.width}px`,
                top: `${targetRect.bottom + window.scrollY + spacing}px`,
            };
        case TooltipPosition.TOP_RIGHT:
            return {
                left: `${targetRect.left + window.scrollX}px`,
                top: `${targetRect.top + window.scrollY - tooltipRect.height - spacing}px`,
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