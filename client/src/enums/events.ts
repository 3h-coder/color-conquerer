export enum Events {
    SERVER_ERROR = "server-error",
    CLIENT_QUEUE_REGISTER = "queue-register",
    SERVER_QUEUE_REGISTERED = "queue-registered",
    SERVER_QUEUE_OPPONENT_FOUND = "queue-opponentFound",
    CLIENT_MATCH_INFO = "client-match-info",
    SERVER_MATCH_INFO = "server-match-info",
    CLIENT_READY = "client-ready", // ready to start or resume a game,
    CLIENT_CLEAR_SESSION = "client-clear-session",
    CLIENT_CELL_HOVER = "client-cell-hover",
    CLIENT_CELL_HOVER_END = "client-cell-hover-end",
    SERVER_CELL_HOVER = "server-cell-hover",
    SERVER_CELL_HOVER_END = "server-cell-hover-end",
    SERVER_SET_WAITING_TEXT = "server-set-waitingText", // sends to the client the text to display while the user is waiting
    SERVER_MATCH_START = "server-match-start", // used to allow rendering the game on the screen
    SERVER_MATCH_ONGOING = "server-match-ongoing", // same thing, but won't display a match started message on the screen
    SERVER_TURN_SWAP = "server-turn-swap",
    CLIENT_TURN_END = "client-turn-end",  // whenever a player choose's to end their turn
    CLIENT_CELL_CLICK = "client-cell-click",
    SERVER_POSSIBLE_ACTIONS = "server-possibleActions",
    SERVER_PROCESSED_ACTIONS = "server-processedActions",
    SERVER_ACTION_ERROR = "server-actionError",
    SERVER_MATCH_END = "server-matchEnd",
}
