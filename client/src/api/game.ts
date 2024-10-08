import { ClientStoredMatchInfoDto } from "../dto/ClientStoredMatchInfoDto";
import { GameContextDto } from "../dto/GameContextDto";
import { MatchInfoDto } from "../dto/MatchInfoDto";
import { PartialPlayerInfoDto } from "../dto/PlayerInfoDto";
import { constants } from "../env";
import { DEFAULT_HEADERS, fetchAs } from "./fetch";

export async function fetchPlayerInfo() {
    return await fetchAs<PartialPlayerInfoDto>("/play/player-info", {
        method: "GET",
        headers: DEFAULT_HEADERS,
        credentials: "include"
    });
}

export async function fetchMatchInfo() {
    return await fetchAs<MatchInfoDto>("/play/match-info", {
        method: "GET",
        headers: DEFAULT_HEADERS,
        credentials: "include"
    });
}

export async function fetchGameContextInfoFromLocalStorage() {
    const playerId = localStorage.getItem(constants.localStoragePlayerId);
    const roomId = localStorage.getItem(constants.localStorageRoomId);

    return await fetchAs<GameContextDto>("/play/game-context", {
        method: "POST",
        headers: DEFAULT_HEADERS,
        credentials: "include",
        body: JSON.stringify({ playerId, roomId } as ClientStoredMatchInfoDto)
    });
}