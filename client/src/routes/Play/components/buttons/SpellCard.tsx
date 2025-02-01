import { useEffect, useRef, useState } from "react";
import { InfoIcon } from "../../../../assets/svg";
import { useTurnInfo } from "../../../../contexts/TurnContext";
import { SpellDto } from "../../../../dto/SpellDto";
import { socket, WHITE_SPACE } from "../../../../env";
import { Events } from "../../../../enums/events";

interface SpellCardProps {
    spell: SpellDto;
}

export default function SpellCard(props: SpellCardProps) {
    const { spell } = props;
    const { canInteract } = useTurnInfo();
    const [showDescription, setShowDescription] = useState(false);
    const isBeingTouched = useRef(false);
    const touchTimeout = useRef<NodeJS.Timeout | null>(null); // Store timeout reference

    useEffect(() => {
        if (!canInteract) setShowDescription(false);
    }, [canInteract]);

    function onMouseEnter() {
        if (!canInteract) return;

        setShowDescription(true);
    }

    function onMouseLeave() {
        if (!canInteract) return;

        setShowDescription(false);
    }

    /**
     * Show the description after 300ms of holding the touch.
     */
    function onTouchStart() {
        if (!canInteract) return;

        isBeingTouched.current = true;
        touchTimeout.current = setTimeout(() => {
            if (isBeingTouched.current) setShowDescription(true);
        }, 300);
    }

    /**
     * Stop showing the description when the touch ends.
     */
    function onTouchEnd() {
        if (!canInteract) return;

        isBeingTouched.current = false;
        if (touchTimeout.current) {
            clearTimeout(touchTimeout.current);
            touchTimeout.current = null;
        }
        setShowDescription(false);
    }

    function onClick() {
        socket.emit(Events.CLIENT_SPELL_BUTTON, spell.id);
    }

    return (
        <>
            <button
                className="spell-card"
                disabled={!canInteract}
                onMouseEnter={onMouseEnter}
                onMouseLeave={onMouseLeave}
                onTouchStart={onTouchStart}
                onTouchEnd={onTouchEnd}
                onClick={onClick}
            >
                <div className="spell-mana-cost">{spell.manaCost}</div>
                <div>{spell.name} ({spell.count}/{spell.maxCount})</div>
            </button>
            {showDescription &&
                <div className="spell-description">
                    <InfoIcon style={{ width: "0.9rem" }} />
                    {WHITE_SPACE}
                    {spell.description}
                </div>}
        </>
    );
}
