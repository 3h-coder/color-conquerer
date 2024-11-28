import { useEffect, useState } from "react";
import { useMatchInfo } from "../../../contexts/MatchContext";
import { usePlayerInfo } from "../../../contexts/PlayerContext";
import { useTurnInfo } from "../../../contexts/TurnContext";
import { TurnInfoDto } from "../../../dto/TurnInfoDto";
import { round } from "../../../utils/mathUtils";

export default function GameTopInfo() {
    const { playerId } = usePlayerInfo();
    const { matchInfo } = useMatchInfo();
    const { turnInfo } = useTurnInfo();
    const whoseTurnMessage = playerId === turnInfo.currentPlayerId ? "Your turn" : "Opponent turn";

    return (
        <GameTopInfoContainer>
            <h3 className="whose-turn-label adaptive-font-size">{whoseTurnMessage}</h3>
            <TimeCountDownBar turnInfoDto={turnInfo} totalTurnDurationInS={matchInfo.totalTurnDurationInS} />
        </GameTopInfoContainer>
    );
}

interface GameTopInfoContainerProps {
    children: React.ReactNode;
}

function GameTopInfoContainer(props: GameTopInfoContainerProps) {
    const { children } = props;

    return (
        <div className="game-top-info-container">
            {children}
        </div>
    );
}

interface TimeCountDownBarProps {
    turnInfoDto: TurnInfoDto;
    totalTurnDurationInS: number;
}

function TimeCountDownBar(props: TimeCountDownBarProps) {
    const { turnInfoDto, totalTurnDurationInS } = props;

    const initialPercentage = round((turnInfoDto.durationInS * 100) / totalTurnDurationInS, 2);
    const [timePercentage, setTimePercentage] = useState(initialPercentage);


    const advancementfactor = 1.08; // Make sure the client time is always a little bit ahead of the server
    const percentageLostPer500ms = round(1 * 100 / (totalTurnDurationInS * 2), 2) * advancementfactor;

    // Update timePercentage whenever turnInfoDto changes
    useEffect(() => {
        setTimePercentage(round((turnInfoDto.durationInS * 100) / totalTurnDurationInS, 2));
    }, [turnInfoDto, totalTurnDurationInS]);

    useEffect(() => {
        const interval = setInterval(() => {
            setTimePercentage((prevPercentage) => {
                return Math.max(prevPercentage - percentageLostPer500ms, 0);
            });
        }, 500);

        return () => clearInterval(interval);
    }, [percentageLostPer500ms, timePercentage, turnInfoDto]);


    return (
        <div className="countdown-bar-outer">
            <div className="countdown-bar-inner" style={{ width: `${timePercentage}%` }} />
        </div>
    );
}
