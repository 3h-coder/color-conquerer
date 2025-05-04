import { useGameContext } from "../../../../contexts/GameContext";
import { usePlayerContext } from "../../../../contexts/PlayerContext";
import PlayerResourcesInfo from "./PlayerResourcesInfo";

export default function MyPlayerResources() {
    const { isPlayer1 } = usePlayerContext();
    const { gameContext } = useGameContext();
    const playerResourceBundle = gameContext.playerResourceBundle;

    const playerResources = isPlayer1
        ? playerResourceBundle.player1Resources
        : playerResourceBundle.player2Resources;

    return (
        <PlayerResourcesInfo
            playerResourcesDto={playerResources}
            own={true}
        />
    );
}
