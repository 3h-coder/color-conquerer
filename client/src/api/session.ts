import { DEFAULT_HEADERS, callFetch } from "./fetch";

export async function initSession() {
    return await callFetch("/session", {
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