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
import { bindTooltip, TooltipPosition } from "../../../../singletons/tooltip";
import { getSpellIcon } from "../shared";

interface SpellCardProps {
    spell: SpellDto;
}

export default function SpellCard(props: SpellCardProps) {
    const { spell } = props;
    const { emit } = useMatchContext();
    const { canInteract } = useTurnContext();
    const { playerMode } = usePlayerMode();
    const [showNameAndCount, setShowNameAndCount] = useState(false);
    const cardRef = useRef<HTMLButtonElement>(null);
    const isBeingTouched = useRef(false);
    const touchTimeout = useRef<NodeJS.Timeout | null>(null); // Store timeout reference

    useEffect(() => {
        if (!canInteract) setShowNameAndCount(false);
    }, [canInteract]);

    const spellDescription = (
        <div className="spell-description">
            <InfoIcon />
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

        setShowNameAndCount(true);
    }

    function onMouseLeave() {
        if (!canInteract) return;

        setShowNameAndCount(false);
    }

    /**
     * Show the name and count after 200ms of holding the touch.
     */
    function onTouchStart() {
        if (!canInteract) return;

        isBeingTouched.current = true;
        touchTimeout.current = setTimeout(() => {
            if (isBeingTouched.current) setShowNameAndCount(true);
        }, 200);
    }

    /**
     * Stop showing the name and count when the touch ends.
     */
    function onTouchEnd() {
        if (!canInteract) return;

        isBeingTouched.current = false;
        if (touchTimeout.current) {
            clearTimeout(touchTimeout.current);
            touchTimeout.current = null;
        }
        setShowNameAndCount(false);
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
                className={`spell-card ${isBeingTouched.current ? "touched" : undefined} ${spell.count === 0 ? "greyed-out" : undefined}`.trim()}
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
                    <span className="spell-card-name-and-count" style={{ display: showNameAndCount ? "block" : "none" }}>
                        {spell.name} {spell.count}/{spell.maxCount}
                    </span>
                </div>
            </button>
        </>
    );
}


