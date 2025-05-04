import { useGameContext } from "../../../../contexts/GameContext";
import { usePlayerInfo } from "../../../../contexts/PlayerContext";
import PlayerResourcesInfo from "./PlayerResourcesInfo";

export default function OpponentResources() {
    const { isPlayer1 } = usePlayerInfo();
    const { gameContext } = useGameContext();
    const playerResourceBundle = gameContext.playerResourceBundle;

    const opponentResources = isPlayer1
        ? playerResourceBundle.player2Resources
        : playerResourceBundle.player1Resources;

    return (
        <PlayerResourcesInfo playerResourcesDto={opponentResources} own={false} />
    );
}
