import { ActionCallbackId } from "../enums/actionCallbackId";
import { MatchActionDto } from "./MatchActionDto";

export interface ActionCallbackDto {
    id: ActionCallbackId;
    parentAction: MatchActionDto;
}