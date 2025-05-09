import { EMPTY_STRING } from "../../env";
import { GameContextDto, undefinedGameContextDto } from "./GameContextDto";
import { TurnProcessingResultDto } from "./TurnProcessingResultDto";

export interface TurnContextDto {
    currentPlayerId: string;
    isPlayer1Turn: boolean;
    remainingTimeInS: number;
    durationInS: number;
    notifyTurnChange: boolean;
    preMatchStart: boolean;
    gameContext: GameContextDto;
    newTurnProcessingInfo: TurnProcessingResultDto | null;
}

export const undefinedTurnContext: TurnContextDto = {
    currentPlayerId: EMPTY_STRING,
    isPlayer1Turn: false,
    remainingTimeInS: 0,
    durationInS: 0,
    notifyTurnChange: false,
    preMatchStart: false,
    gameContext: undefinedGameContextDto,
    newTurnProcessingInfo: null
};
