import { BooleanDto } from "../dto/BooleanDto";
import { DEFAULT_HEADERS, callFetch, fetchAs } from "./fetch";

export async function initSession() {
    return await callFetch("/session", {
        method: "GET",
        headers: DEFAULT_HEADERS,
        credentials: "include"
    });
}

export async function checkIfInMatch() {
    return await fetchAs<BooleanDto>("/session/is-in-match", {
        method: "GET",
        headers: DEFAULT_HEADERS,
        credentials: "include"
    });
}

export async function clearMatchInfoFromSession() {
    return await callFetch("/match-session", {
        method: "DELETE",
        headers: DEFAULT_HEADERS,
        credentials: "include"
    });
}