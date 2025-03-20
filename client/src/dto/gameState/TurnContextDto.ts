import { EMPTY_STRING } from "../../env";
import { GameContextDto, undefinedGameContextDto } from "./GameContextDto";

export interface TurnContextDto {
    currentPlayerId: string;
    isPlayer1Turn: boolean;
    remainingTimeInS: number;
    durationInS: number;
    notifyTurnChange: boolean;
    gameContext: GameContextDto;
}

export const undefinedTurnContext: TurnContextDto = {
    currentPlayerId: EMPTY_STRING,
    isPlayer1Turn: false,
    remainingTimeInS: 0,
    durationInS: 0,
    notifyTurnChange: false,
    gameContext: undefinedGameContextDto
};
