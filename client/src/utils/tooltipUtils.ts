import { TooltipPosition } from "../singletons/tooltip";

/**
 * Calculates the tooltip coordinates based on the target element's position, tooltip size, and the desired position.
 * If the tooltip does not fit in the viewport, it will try different positions until it finds one that fits.
 */
export function getTooltipCoordinates(targetElementRect: DOMRect, tooltipRect: DOMRect, actualPosition: TooltipPosition) {
    let found = false;
    let left = "0px";
    let top = "0px";

    const positionsToTry = getPositionPriority(actualPosition);

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
    return { left, top };
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

function isTooltipInViewport(left: number, top: number, tooltipRect: DOMRect): boolean {
    const right = left + tooltipRect.width;
    const bottom = top + tooltipRect.height;
    return (
        left >= 0 &&
        top >= 0 &&
        right <= window.innerWidth &&
        bottom <= window.innerHeight
    );
}

/**
 * Returns the sequence of positions to try (in case of screen clipping) for a tooltip based on the original position.
 * @param original 
 * @returns 
 */
function getPositionPriority(original: TooltipPosition): TooltipPosition[] {

    switch (original) {
        case TooltipPosition.TOP:
            return [
                original,
                TooltipPosition.BOTTOM,
                TooltipPosition.RIGHT,
                TooltipPosition.LEFT,
                TooltipPosition.TOP_RIGHT,
                TooltipPosition.TOP_LEFT,
                TooltipPosition.BOTTOM_RIGHT,
                TooltipPosition.BOTTOM_LEFT,
            ];
        case TooltipPosition.BOTTOM:
            return [
                original,
                TooltipPosition.TOP,
                TooltipPosition.RIGHT,
                TooltipPosition.LEFT,
                TooltipPosition.BOTTOM_RIGHT,
                TooltipPosition.BOTTOM_LEFT,
                TooltipPosition.TOP_RIGHT,
                TooltipPosition.TOP_LEFT,
            ];
        case TooltipPosition.LEFT:
            return [
                original,
                TooltipPosition.RIGHT,
                TooltipPosition.TOP,
                TooltipPosition.BOTTOM,
                TooltipPosition.TOP_LEFT,
                TooltipPosition.BOTTOM_LEFT,
                TooltipPosition.TOP_RIGHT,
                TooltipPosition.BOTTOM_RIGHT,
            ];
        case TooltipPosition.RIGHT:
            return [
                original,
                TooltipPosition.LEFT,
                TooltipPosition.TOP,
                TooltipPosition.BOTTOM,
                TooltipPosition.TOP_RIGHT,
                TooltipPosition.BOTTOM_RIGHT,
                TooltipPosition.TOP_LEFT,
                TooltipPosition.BOTTOM_LEFT,
            ];
        case TooltipPosition.TOP_LEFT:
            return [
                original,
                TooltipPosition.BOTTOM_LEFT,
                TooltipPosition.TOP_RIGHT,
                TooltipPosition.BOTTOM_RIGHT,
                TooltipPosition.TOP,
                TooltipPosition.BOTTOM,
                TooltipPosition.LEFT,
                TooltipPosition.RIGHT,
            ];
        case TooltipPosition.BOTTOM_LEFT:
            return [
                original,
                TooltipPosition.TOP_LEFT,
                TooltipPosition.BOTTOM_RIGHT,
                TooltipPosition.TOP_RIGHT,
                TooltipPosition.BOTTOM,
                TooltipPosition.TOP,
                TooltipPosition.LEFT,
                TooltipPosition.RIGHT,
            ];
        case TooltipPosition.TOP_RIGHT:
            return [
                original,
                TooltipPosition.BOTTOM_RIGHT,
                TooltipPosition.TOP_LEFT,
                TooltipPosition.BOTTOM_LEFT,
                TooltipPosition.TOP,
                TooltipPosition.BOTTOM,
                TooltipPosition.RIGHT,
                TooltipPosition.LEFT,
            ];
        case TooltipPosition.BOTTOM_RIGHT:
            return [
                original,
                TooltipPosition.TOP_RIGHT,
                TooltipPosition.BOTTOM_LEFT,
                TooltipPosition.TOP_LEFT,
                TooltipPosition.BOTTOM,
                TooltipPosition.TOP,
                TooltipPosition.RIGHT,
                TooltipPosition.LEFT,
            ];
        default:
            return [
                original,
                TooltipPosition.BOTTOM,
                TooltipPosition.TOP,
                TooltipPosition.RIGHT,
                TooltipPosition.LEFT,
                TooltipPosition.BOTTOM_RIGHT,
                TooltipPosition.BOTTOM_LEFT,
                TooltipPosition.TOP_RIGHT,
                TooltipPosition.TOP_LEFT,
            ];
    }
}