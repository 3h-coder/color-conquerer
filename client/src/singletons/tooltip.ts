import React, { createElement } from "react";
import { createRoot, Root } from "react-dom/client";
import { EMPTY_STRING, HTMLElements } from "../env";
import { getOrCreateDomElement } from "../utils/domUtils";
import { calculateTooltipPosition, getPositionPriority, isTooltipInViewport } from "../utils/tooltipUtils";

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
let _activeTooltipElement: HTMLElement | null = null;
let _activeReactRoot: Root | null = null;
// We're using a ùutation observer as the target element may be removed from the DOM
// and we need to clean up the tooltip in that case.
let _observer: MutationObserver | null = null;

export let activeTooltipTarget: HTMLElement | null = null;

/** 
 * Utility method for the mouse hover to display a tooltip relative to the given target react reference. 
 * 
 * Returns a cleanup function to remove the tooltip and its event listeners.
 */
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

        activeTooltipTarget = targetElement;
        createActiveTooltip(tooltipContentElement, tooltipText);
        adjustTooltipPosition(targetElement, position);
    };

    const hideTooltip = () => {
        cleanupActiveTooltip();
        activeTooltipTarget = null;
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

    _activeTooltipElement = tooltipElement;
    _activeReactRoot = reactRoot;
}

export function cleanupActiveTooltip() {
    if (_activeTooltipElement) {
        if (_activeReactRoot) {
            _activeReactRoot.unmount();
            _activeReactRoot = null;
        }
        if (_activeTooltipElement.parentElement) {
            _activeTooltipElement.parentElement.removeChild(_activeTooltipElement);
        }
        _activeTooltipElement = null;
    }
}

function adjustTooltipPosition(
    targetElement: HTMLElement,
    position: TooltipPosition | undefined
) {
    setTimeout(() => {
        if (!_activeTooltipElement) return;

        const targetElementRect = targetElement.getBoundingClientRect();
        const tooltipRect = _activeTooltipElement.getBoundingClientRect();

        const actualPosition = position ?? TooltipPosition.TOP;
        const positionsToTry = getPositionPriority(actualPosition);

        let found = false;
        let left = "0px";
        let top = "0px";

        // Try different positions until the tooltip fits in the viewport
        for (const pos of positionsToTry) {
            const coords = calculateTooltipPosition(targetElementRect, tooltipRect, pos);
            const l = parseFloat(coords.left);
            const t = parseFloat(coords.top);

            if (isTooltipInViewport(l, t, tooltipRect)) {
                left = coords.left;
                top = coords.top;
                found = true;
                break;
            }
        }

        // If none fit, fallback to the original position
        if (!found) {
            const coords = calculateTooltipPosition(
                targetElementRect,
                tooltipRect,
                actualPosition
            );
            left = coords.left;
            top = coords.top;
        }

        _activeTooltipElement.style.left = left;
        _activeTooltipElement.style.top = top;
    }, 20);
}

function getTooltipOverlay() {
    const tooltipRoot = getOrCreateDomElement("tooltip-root");
    return getOrCreateDomElement("tooltip-overlay", tooltipRoot);
}

function resetMutationObserver(targetElement: HTMLElement) {
    destroyMutationObserver();

    _observer = new MutationObserver((mutations) => {
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

    _observer.observe(document.body, { childList: true, subtree: true });
}

function destroyMutationObserver() {
    _observer?.disconnect();
    _observer = null;
}

// #endregion
