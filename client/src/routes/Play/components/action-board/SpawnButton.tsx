import { useEffect, useState } from "react";
import { LocationPinIcon } from "../../../../assets/svg";
import { SvgContainer } from "../../../../components/containers";
import { useTurnContext } from "../../../../contexts/TurnContext";
import { Events } from "../../../../enums/events";
import { socket } from "../../../../env";
import { usePlayerMode } from "../../../../contexts/PlayerModeContext";
import { PlayerMode } from "../../../../enums/playerMode";

export default function SpawnButton() {
    const { canInteract } = useTurnContext();
    const { playerMode } = usePlayerMode();

    const buttonKey = "s";
    const iconSize = "max(10px, 0.8vmin)";
    const [text, setText] = useState(`Spawn (${buttonKey})`);

    function onClick() {
        socket.emit(Events.CLIENT_SPAWN_BUTTON);
    }

    useEffect(() => {
        if (playerMode === PlayerMode.CELL_SPAWN) {
            setText(`Cancel (${buttonKey})`);
        } else {
            setText(`Spawn (${buttonKey})`);
        }
    }, [playerMode]);

    // Key press event listener (button shortcut)
    useEffect(() => {
        function handleKeyPress(event: KeyboardEvent) {
            if (!canInteract)
                return;

            if (event.key === buttonKey)
                onClick();
            else if (event.key === "Escape" && playerMode === PlayerMode.CELL_SPAWN)
                onClick();
        }

        window.addEventListener("keydown", handleKeyPress);

        return () => {
            window.removeEventListener("keydown", handleKeyPress);
        };
    }, [playerMode, canInteract]);

    return (
        <button id="spawn-button" disabled={!canInteract} onClick={onClick}>
            <SvgContainer style={{ height: iconSize, width: iconSize }}>
                <LocationPinIcon />
            </SvgContainer>
            {text}
        </button>
    );
}