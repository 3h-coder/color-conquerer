import { HTMLElements } from "../env";
import { getOrCreateDomElement } from "./domUtils";

export enum TooltipPosition {
    TOP,
    BOTTOM,
    LEFT,
    RIGHT,
}

export function bindTooltip(
    ref: React.RefObject<HTMLElement>,
    tooltipText: string,
    position: TooltipPosition = TooltipPosition.TOP) {
    if (!ref.current) return;

    const element = ref.current;
    let tooltipElement: HTMLElement | null = null;

    const showTooltip = () => {
        tooltipElement = document.createElement(HTMLElements.div);
        tooltipElement.className = "tooltip";
        tooltipElement.innerText = tooltipText;

        const tooltipOverlay = getTooltipOverlay();
        tooltipOverlay.appendChild(tooltipElement);

        const rect = element.getBoundingClientRect();

        switch (position) {
            case TooltipPosition.TOP:
                tooltipElement.style.left = `${rect.left + window.scrollX + rect.width / 2}px`;
                tooltipElement.style.top = `${rect.top + window.scrollY - tooltipElement.offsetHeight - 5}px`;
                break;
            case TooltipPosition.BOTTOM:
                tooltipElement.style.left = `${rect.left + window.scrollX + rect.width / 2}px`;
                tooltipElement.style.top = `${rect.bottom + window.scrollY + 5}px`;
                break;
            case TooltipPosition.LEFT:
                tooltipElement.style.left = `${rect.left + window.scrollX - tooltipElement.offsetWidth - 5}px`;
                tooltipElement.style.top = `${rect.top + window.scrollY + rect.height / 2 - tooltipElement.offsetHeight / 2}px`;
                break;
            case TooltipPosition.RIGHT:
                tooltipElement.style.left = `${rect.right + window.scrollX + 5}px`;
                tooltipElement.style.top = `${rect.top + window.scrollY + rect.height / 2 - tooltipElement.offsetHeight / 2}px`;
                break;
        }
    };

    const hideTooltip = () => {
        if (tooltipElement && tooltipElement.parentElement) {
            tooltipElement.parentElement.removeChild(tooltipElement);
            tooltipElement = null;
        }
    };

    element.addEventListener("mouseenter", showTooltip);
    element.addEventListener("mouseleave", hideTooltip);

    return () => {
        element.removeEventListener("mouseenter", showTooltip);
        element.removeEventListener("mouseleave", hideTooltip);
    };
}

function getTooltipOverlay() {
    const tooltipRoot = getOrCreateDomElement("tooltip-root");
    return getOrCreateDomElement("tooltip-overlay", tooltipRoot);
}