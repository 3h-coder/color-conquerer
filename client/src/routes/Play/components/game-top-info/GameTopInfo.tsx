import { useEffect, useState } from "react";
import { usePlayerContext } from "../../../../contexts/PlayerContext";
import { useTurnContext } from "../../../../contexts/TurnContext";
import { TurnContextDto } from "../../../../dto/gameState/TurnContextDto";
import { round } from "../../../../utils/mathUtils";
import "./styles/GameTopInfo.css";

export default function GameTopInfo() {
    const { playerId } = usePlayerContext();
    const { turnContext } = useTurnContext();
    const whoseTurnMessage = playerId === turnContext.currentPlayerId ? "Your turn" : "Opponent turn";

    return (
        <GameTopInfoContainer>
            <h3 id="whose-turn-label">
                {whoseTurnMessage}
            </h3>
            <TimeCountDownBar turnContext={turnContext} />
        </GameTopInfoContainer>
    );
}

interface GameTopInfoContainerProps {
    children: React.ReactNode;
}

function GameTopInfoContainer(props: GameTopInfoContainerProps) {
    const { children } = props;

    return (
        <div id="game-top-info-container">
            {children}
        </div>
    );
}

interface TimeCountDownBarProps {
    turnContext: TurnContextDto;
}

function TimeCountDownBar(props: TimeCountDownBarProps) {
    const { turnContext } = props;
    const totalTurnDurationInS = turnContext.durationInS;

    const initialPercentage = round((turnContext.remainingTimeInS * 100) / totalTurnDurationInS, 2);
    const [timePercentage, setTimePercentage] = useState(initialPercentage);


    const advancementfactor = 1.08; // Make sure the client time is always a little bit ahead of the server
    const percentageLostPer500ms = round(1 * 100 / (totalTurnDurationInS * 2), 2) * advancementfactor;

    // Update timePercentage whenever turnInfoDto changes
    useEffect(() => {
        setTimePercentage(round((turnContext.remainingTimeInS * 100) / totalTurnDurationInS, 2));
    }, [turnContext]);

    // Update timePercentage every 500ms
    useEffect(() => {
        if (turnContext.preMatchStart)
            return;

        const interval = setInterval(() => {
            setTimePercentage((prevPercentage) => {
                return Math.max(prevPercentage - percentageLostPer500ms, 0);
            });
        }, 500);

        return () => clearInterval(interval);
    }, [timePercentage, turnContext]);

    return (
        <div className="countdown-bar-outer">
            <div className="countdown-bar-inner" style={{ width: `${timePercentage}%` }} />
        </div>
    );
}
