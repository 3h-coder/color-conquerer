import { useTurnContext } from "../../../../contexts/TurnContext";
import { Events } from "../../../../enums/events";
import { socket } from "../../../../env";

export default function EndTurnButton() {
    const { canInteract } = useTurnContext();

    const text = "End Turn";

    function onClick() {
        socket.emit(Events.CLIENT_TURN_END);
    }

    return (
        <button className="end-turn" disabled={!canInteract} onClick={onClick}>
            {text}
        </button>
    );
}