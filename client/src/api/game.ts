import { PartialMatchInfoDto } from "../dto/PartialMatchInfoDto";
import { PartialPlayerInfoDto } from "../dto/PartialPlayerInfoDto";
import { DEFAULT_HEADERS, fetchAs } from "./fetch";

export async function fetchPlayerInfo() {
    return await fetchAs<PartialPlayerInfoDto>("/play/player-info", {
        method: "GET",
        headers: DEFAULT_HEADERS,
        credentials: "include"
    });
}

export async function fetchMatchInfo() {
    return await fetchAs<PartialMatchInfoDto>("/play/match-info", {
        method: "GET",
        headers: DEFAULT_HEADERS,
        credentials: "include"
    });
}