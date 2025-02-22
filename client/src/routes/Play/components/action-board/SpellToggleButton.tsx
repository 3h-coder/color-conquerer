import { useEffect } from "react";
import { ChevronRightIcon, MagicWandIcon } from "../../../../assets/svg";
import { SvgContainer } from "../../../../components/containers";
import { useTurnContext } from "../../../../contexts/TurnContext";

export interface SpellToggleButtonProps {
    spellsVisible: boolean;
    setSpellsVisible: (value: boolean) => void;
}

export default function SpellToggleButton(props: SpellToggleButtonProps) {
    const { spellsVisible, setSpellsVisible } = props;
    const { canInteract } = useTurnContext();
    const buttonKey = "d";
    const wandIconSize = "max(14px, 2.2vmin)";
    const chevronIconSize = "max(10px, 0.8vmin)";
    const text = `Spells (${buttonKey})`;

    function onClick() {
        setSpellsVisible(!spellsVisible);
    }

    useEffect(() => {
        function handleKeyPress(event: KeyboardEvent) {
            if (!canInteract)
                return;

            if (event.key === buttonKey)
                onClick();
        }

        window.addEventListener("keydown", handleKeyPress);

        return () => {
            window.removeEventListener("keydown", handleKeyPress);
        };
    });

    return (
        <button id="spell-toggle-button" disabled={!canInteract} onClick={onClick}>
            <SvgContainer style={{ width: chevronIconSize, height: chevronIconSize, transform: spellsVisible ? "rotate(90deg)" : undefined }}>
                <ChevronRightIcon />
            </SvgContainer>
            <SvgContainer style={{ width: wandIconSize, height: wandIconSize }}>
                <MagicWandIcon />
            </SvgContainer>
            <div>{text}</div>
        </button>
    );
}