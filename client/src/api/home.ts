import { HomeStateDto } from "../dto/HomeStateDto";
import { DEFAULT_HEADERS, fetchAs } from "./fetch";

export async function fetchHomeState() {
    return await fetchAs<HomeStateDto>("/home-state", {
        method: "GET",
        headers: DEFAULT_HEADERS,
        credentials: "include"
    })
}