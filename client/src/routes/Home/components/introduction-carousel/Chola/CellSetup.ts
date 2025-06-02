import { CoordinatesDto } from "../../../../../dto/misc/CoordinatesDto";
import { CellState } from "../../../../../enums/cellState";

export interface CellSetup extends CoordinatesDto {
    state?: CellState;
}