import { useEffect, useRef } from "react";
import { bindTooltip } from "../../../../../singletons/tooltip";

export function ManaBubble() {
    const bubbleRef = useRef<HTMLDivElement>(null);
    const description =
        "Gain an extra mana point when moving to this cell or spawning on it";

    useEffect(() => {
        const cleanup = bindTooltip(bubbleRef, {
            tooltipText: description,
        });
        return cleanup;
    }, [description, bubbleRef]);

    return (
        <div className="mana-bubble" ref={bubbleRef}>
        </div>
    );
}