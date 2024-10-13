export enum Events {
    SERVER_ERROR = "server-error",
    CLIENT_QUEUE_REGISTER = "queue-register",
    SERVER_QUEUE_REGISTERED = "queue-registered",
    SERVER_QUEUE_OPPONENT_FOUND = "queue-opponentFound",
    CLIENT_MATCH_INFO = "client-match-info",
    SERVER_MATCH_INFO = "server-match-info",
    CLIENT_READY = "client-ready", // ready to start or resume a game,
    CLIENT_CLEAR_SESSION = "client-clear-session",
    SERVER_SET_WAITING_TEXT = "server-set-waitingText", // sends to the client the text to display while the user is waiting
    SERVER_MATCH_STARTED = "server-match-started", // used to allow rendering the game on the screen
    SERVER_TURN_SWAP = "server-turn-swap",
    SERVER_MATCH_END = "server-matchEnd",
}
