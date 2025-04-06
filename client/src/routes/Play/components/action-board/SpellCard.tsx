import { useEffect, useRef, useState } from "react";
import { InfoIcon } from "../../../../assets/svg";
import { SvgContainer } from "../../../../components/containers";
import { useMatchContext } from "../../../../contexts/MatchContext";
import { usePlayerMode } from "../../../../contexts/PlayerModeContext";
import { useTurnContext } from "../../../../contexts/TurnContext";
import { SpellDto } from "../../../../dto/spell/SpellDto";
import { Events } from "../../../../enums/events";
import { PlayerMode } from "../../../../enums/playerMode";
import { WHITE_SPACE } from "../../../../env";
import { bindTooltip, TooltipPosition } from "../../../../utils/tooltipUtils";
import { getSpellIcon } from "../shared";

interface SpellCardProps {
    spell: SpellDto;
}

export default function SpellCard(props: SpellCardProps) {
    const { spell } = props;
    const { emit } = useMatchContext();
    const { canInteract } = useTurnContext();
    const { playerMode } = usePlayerMode();
    const [showDescription, setShowDescription] = useState(false);
    const cardRef = useRef<HTMLButtonElement>(null);
    const isBeingTouched = useRef(false);
    const touchTimeout = useRef<NodeJS.Timeout | null>(null); // Store timeout reference

    useEffect(() => {
        if (!canInteract) setShowDescription(false);
    }, [canInteract]);

    const spellDescription = (
        <div>
            <InfoIcon style={{ width: "0.9rem" }} />
            {WHITE_SPACE}
            {spell.description}
        </div>
    );

    useEffect(() => {
        const cleanup = bindTooltip(cardRef, {
            position: TooltipPosition.TOP_LEFT,
            tooltipContentElement: spellDescription,
        });
        return cleanup;
    }, [spell.description]);

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
        if (!canInteract) return;

        emit(Events.CLIENT_SPELL_BUTTON, spell.id);
    }

    // Use the escape key to cancel the spell selection
    useEffect(() => {
        function handleKeyPress(event: KeyboardEvent) {
            if (!canInteract)
                return;

            else if (event.key === "Escape" && playerMode === PlayerMode.SPELL_SELECTED)
                onClick();
        }

        window.addEventListener("keydown", handleKeyPress);

        return () => {
            window.removeEventListener("keydown", handleKeyPress);
        };
    }, [playerMode, canInteract]);

    const iconSize = "1rem";

    return (
        <>
            <button
                ref={cardRef}
                className="spell-card"
                disabled={!canInteract}
                onMouseEnter={onMouseEnter}
                onMouseLeave={onMouseLeave}
                onTouchStart={onTouchStart}
                onTouchEnd={onTouchEnd}
                onClick={onClick}
            >
                <div className="spell-mana-cost">{spell.manaCost}</div>
                <div className="spell-card-content">
                    <SvgContainer style={{ width: iconSize, height: iconSize }}>
                        {getSpellIcon(spell.id)}
                    </SvgContainer>
                    <span className="spell-card-name-and-count" style={{ display: showDescription ? "block" : "none" }}>
                        {spell.name} {spell.count}/{spell.maxCount}
                    </span>
                </div>
            </button>
        </>
    );
}


