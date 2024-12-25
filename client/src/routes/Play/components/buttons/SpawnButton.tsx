import { useState } from "react";
import { LocationPinIcon } from "../../../../assets/svg";
import { SvgContainer } from "../../../../components/containers";
import { useTurnInfo } from "../../../../contexts/TurnContext";
import { Events } from "../../../../enums/events";
import { socket } from "../../../../env";

export default function SpawnButton() {
    const { canInteract } = useTurnInfo();

    const spawnIconSize = "max(10px, 0.8vmin)";
    const [text, setText] = useState("Spawn");

    function onClick() {
        socket.emit(Events.CLIENT_SPAWN_BUTTON);
    }

    return (
        <button id="spawn-button" disabled={!canInteract} onClick={onClick}>
            <SvgContainer style={{ height: spawnIconSize, width: spawnIconSize }}>
                <LocationPinIcon />
            </SvgContainer>
            {text}
        </button>
    );
}