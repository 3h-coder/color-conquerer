import { useEffect, useState } from "react";
import { useMatchInfo } from "../../../contexts/MatchContext";
import { usePlayerInfo } from "../../../contexts/PlayerContext";
import { TurnInfoDto } from "../../../dto/TurnInfoDto";
import { round } from "../../../utils/mathUtils";

interface GameTopInfoProps {
    turnInfoDto: TurnInfoDto;
}

export default function GameTopInfo(props: GameTopInfoProps) {
    const { playerInfo } = usePlayerInfo();
    const { matchInfo } = useMatchInfo();
    const { turnInfoDto } = props;
    const whoseTurnMessage = playerInfo.playerId === turnInfoDto.currentPlayerId ? "Your turn" : "Your opponent's turn";

    return (
        <GameTopInfoContainer>
            <h3 className="whose-turn-label">{whoseTurnMessage}</h3>
            <TimeCountDownBar turnInfoDto={turnInfoDto} totalTurnDurationInS={matchInfo.totalTurnDurationInS} />
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
    const colors = {
        green: "green",
        orange: "orange",
        red: "red",
    }

    const initialPercentage = round((turnInfoDto.durationInS * 100) / totalTurnDurationInS, 2);
    const [timePercentage, setTimePercentage] = useState(initialPercentage);
    const [color, setColor] = useState(colors.green);


    const advancementfactor = 1.08; // Make sure the client time is always a little bit ahead of the server
    const percentageLostPer500ms = round(1 * 100 / (totalTurnDurationInS * 2), 2) * advancementfactor;

    // Update timePercentage whenever turnInfoDto changes
    useEffect(() => {
        setTimePercentage(round((turnInfoDto.durationInS * 100) / totalTurnDurationInS, 2));
        setColor(colors.green);
    }, [turnInfoDto, totalTurnDurationInS, colors.green]);

    useEffect(() => {
        const interval = setInterval(() => {
            setTimePercentage((prevPercentage) => {
                return Math.max(prevPercentage - percentageLostPer500ms, 0);
            });
        }, 500);

        return () => clearInterval(interval);
    }, [percentageLostPer500ms, timePercentage, turnInfoDto]);

    // Update color whenever timePercentage changes
    useEffect(() => {
        function updateColor(percentage: number) {
            if (percentage >= 50) {
                setColor(colors.green);
            } else if (percentage >= 20) {
                setColor(colors.orange);
            } else {
                setColor(colors.red);
            }
        }

        updateColor(timePercentage);
    }, [colors.green, colors.orange, colors.red, timePercentage]);


    return (
        <div className="countdown-bar-outer">
            <div className="countdown-bar-inner" style={{ width: `${timePercentage}%`, backgroundColor: color }} />
        </div>
    );
}
