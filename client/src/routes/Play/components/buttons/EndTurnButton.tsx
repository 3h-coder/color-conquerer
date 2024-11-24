import { usePlayerInfo } from "../../../../contexts/PlayerContext";
import { useTurnInfo } from "../../../../contexts/TurnContext";
import { Events } from "../../../../enums/events";
import { socket } from "../../../../env";

export default function EndTurnButton() {
    const { turnInfo } = useTurnInfo();
    const { playerInfo } = usePlayerInfo();

    const isMyTurn = turnInfo.currentPlayerId === playerInfo.playerId;
    const text = "End Turn"

    function onClick() {
        socket.emit(Events.CLIENT_TURN_END);
    }

    return (
        <button className="end-turn" disabled={!isMyTurn} onClick={onClick}>{text}</button>
    );
}