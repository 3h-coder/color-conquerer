import { useMatchInfo } from "../../../contexts/MatchContext";
import { usePlayerInfo } from "../../../contexts/PlayerContext";
import { TurnInfoDto } from "../../../dto/TurnInfoDto";

interface GameTopInfoProps {
    turnInfoDto: TurnInfoDto
}

export default function GameTopInfo(props: GameTopInfoProps) {
    const { playerInfo } = usePlayerInfo();
    const { matchInfo } = useMatchInfo();
    const { turnInfoDto } = props;
    const whoseTurnMessage = playerInfo.playerId === turnInfoDto.currentPlayerId ? "Your turn" : "Your opponent's turn";
    const timePercentage = Math.round(turnInfoDto.durationInS * 100 / matchInfo.totalTurnDurationInS);
    console.log("timePercentage", `${timePercentage} %`);

    return (
        <GameTopInfoContainer>
            <h3 className="whose-turn-label">{whoseTurnMessage}</h3>
            <TimeCountDownBar timePercentage={timePercentage} />
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
    timePercentage: number;
}

function TimeCountDownBar(props: TimeCountDownBarProps) {
    const { timePercentage } = props;

    return (
        <div className="countdown-bar-outer">
            <div className="countdown-bar-inner" style={{ width: `${timePercentage}%` }} />
        </div>
    );
}