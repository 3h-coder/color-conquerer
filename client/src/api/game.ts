import { MatchInfoDto } from "../dto/MatchInfoDto";
import { PlayerInfoDto } from "../dto/PlayerInfoDto";
import { DEFAULT_HEADERS, fetchAs } from "./fetch";

export async function fetchPlayerInfo() {
    return await fetchAs<PlayerInfoDto>("/play/player-info", {
        method: "GET",
        headers: DEFAULT_HEADERS,
    });
}

export async function fetchMatchInfo() {
    return await fetchAs<MatchInfoDto>("/play/match-info", {
        method: "GET",
        headers: DEFAULT_HEADERS,
    });
}