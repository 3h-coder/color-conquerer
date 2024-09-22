export enum Events {
    SERVER_ERROR = "server-error",
    CLIENT_QUEUE_REGISTER = "queue-register",
    SERVER_QUEUE_REGISTERED = "queue-registered",
    SERVER_QUEUE_OPPONENT_FOUND = "queue-opponentFound",
    CLIENT_MATCH_INFO = "client-match-info",
    SERVER_MATCH_INFO = "server-match-info",
    CLIENT_READY = "client-ready", // ready to start or resume a game
    SERVER_START_MATCH = "server-start-match",
    SERVER_TURN_SWAP = "server-turn-swap",
    SERVER_MATCH_END = "server-matchEnd",
}
