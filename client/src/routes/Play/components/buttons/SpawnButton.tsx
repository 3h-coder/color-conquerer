import { useEffect, useState } from "react";
import { LocationPinIcon } from "../../../../assets/svg";
import { SvgContainer } from "../../../../components/containers";
import { useTurnInfo } from "../../../../contexts/TurnContext";
import { Events } from "../../../../enums/events";
import { socket } from "../../../../env";
import { usePlayerMode } from "../../../../contexts/PlayerModeContext";
import { PlayerMode } from "../../../../enums/playerMode";
import { developmentLog } from "../../../../utils/loggingUtils";

export default function SpawnButton() {
    const buttonKey = "s";
    const { canInteract } = useTurnInfo();
    const { playerMode } = usePlayerMode();

    const spawnIconSize = "max(10px, 0.8vmin)";
    const [text, setText] = useState(`Spawn (${buttonKey})`);

    function onClick() {
        socket.emit(Events.CLIENT_SPAWN_BUTTON);
    }

    function handleKeyPress(event: KeyboardEvent) {
        if (event.key === buttonKey)
            onClick();
        else if (event.key === "Escape" && playerMode === PlayerMode.CELL_SPAWN)
            onClick();
    }

    useEffect(() => {
        if (playerMode === PlayerMode.CELL_SPAWN) {
            setText(`Cancel (${buttonKey})`);
        } else {
            setText(`Spawn (${buttonKey})`);
        }
    }, [playerMode]);

    useEffect(() => {
        window.addEventListener('keydown', handleKeyPress);

        return () => {
            window.removeEventListener('keydown', handleKeyPress);
        };
    }, []);

    return (
        <button id="spawn-button" disabled={!canInteract} onClick={onClick}>
            <SvgContainer style={{ height: spawnIconSize, width: spawnIconSize }}>
                <LocationPinIcon />
            </SvgContainer>
            {text}
        </button>
    );
}