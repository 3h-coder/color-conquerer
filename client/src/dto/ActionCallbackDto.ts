import { ActionCallbackId } from "../enums/actionCallbackId";
import { CellDto } from "./CellDto";
import { MatchActionDto } from "./MatchActionDto";

export interface ActionCallbackDto {
    id: ActionCallbackId;
    parentAction: MatchActionDto;
    updatedGameBoard: CellDto[][];
}