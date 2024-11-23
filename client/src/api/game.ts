import { PartialMatchInfoDto } from "../dto/PartialMatchInfoDto";
import { PlayerInfoBundleDto } from "../dto/PlayerInfoBundleDto";
import { DEFAULT_HEADERS, fetchAs } from "./fetch";

export async function fetchPlayerInfoBundle() {
    return await fetchAs<PlayerInfoBundleDto>("/play/player-info", {
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