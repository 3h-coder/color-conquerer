import { MatchContextDto } from "../dto/MatchContextDto";
import { PlayerDto } from "../dto/PlayerDto";
import { DEFAULT_HEADERS, fetchAs } from "./fetch";

export async function fetchPlayerInfo() {
    return await fetchAs<PlayerDto>("/play/player-info", {
        method: "GET",
        headers: DEFAULT_HEADERS,
        credentials: "include"
    });
}

export async function fetchMatchInfo() {
    return await fetchAs<MatchContextDto>("/play/match-info", {
        method: "GET",
        headers: DEFAULT_HEADERS,
        credentials: "include"
    });
}