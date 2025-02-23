import { ActionCallbackId } from "../enums/actionCallbackId";
import { GameContextDto } from "./GameContextDto";
import { MatchActionDto } from "./MatchActionDto";

export interface ActionCallbackDto {
    id: ActionCallbackId;
    parentAction: MatchActionDto;
    updatedGameContext: GameContextDto;
}