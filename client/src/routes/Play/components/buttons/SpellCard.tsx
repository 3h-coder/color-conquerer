import { useEffect, useRef, useState } from "react";
import { BombIcon, InfoIcon } from "../../../../assets/svg";
import { SvgContainer } from "../../../../components/containers";
import { usePlayerMode } from "../../../../contexts/PlayerModeContext";
import { useTurnContext } from "../../../../contexts/TurnContext";
import { SpellDto } from "../../../../dto/SpellDto";
import { Events } from "../../../../enums/events";
import { PlayerMode } from "../../../../enums/playerMode";
import { SpellId } from "../../../../enums/spellId";
import { socket, WHITE_SPACE } from "../../../../env";

interface SpellCardProps {
    spell: SpellDto;
}

export default function SpellCard(props: SpellCardProps) {
    const { spell } = props;
    const { canInteract } = useTurnContext();
    const { playerMode } = usePlayerMode();
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
                    {spell.name} ({spell.count}/{spell.maxCount})
                </div>
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

function getSpellIcon(spellId: number) {
    switch (spellId) {
        case SpellId.MINE_TRAP:
            return <BombIcon />;

        default:
            return <></>;
    }
}
