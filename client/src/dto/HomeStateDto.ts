import { HomeState } from "../enums/homeState";

export interface HomeStateDto {
    state: HomeState;
    topMessage: string;
    clearMatchSession: boolean;
}