import { DEFAULT_HEADERS, callFetch } from "./fetch";

export async function initSession() {
    return await callFetch("/session", {
        method: "GET",
        headers: DEFAULT_HEADERS,
        credentials: "include"
    });
}