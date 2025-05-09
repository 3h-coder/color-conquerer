// ⚠️ Must be in sync with the server-side enum
export enum Events {
    // Common Events
    DISCONNECT = "disconnect",

    // Client Events
    CLIENT_CELL_CLICK = "client-cell-click",
    CLIENT_MATCH_CONCEDE = "client-match-concede",
    CLIENT_MATCH_INFO = "client-match-info",
    CLIENT_QUEUE_REGISTER = "queue-register",
    CLIENT_READY = "client-ready", // ready to start or resume a game,
    CLIENT_SPAWN_BUTTON = "client-spawn-button",
    CLIENT_SPELL_BUTTON = "client-spell-button",
    CLIENT_TURN_END = "client-turn-end",  // whenever a player choose's to end their turn

    // Server Events
    SERVER_ACTION_CALLBACK = "server-action-callback",
    SERVER_ACTION_ERROR = "server-actionError",
    SERVER_COUNTDOWN = "server-countdown",
    SERVER_ERROR = "server-error",
    SERVER_INACTIVITY_WARNING = "server-inactivity-warning",
    SERVER_MATCH_END = "server-match-end",
    SERVER_MATCH_INFO = "server-match-info",
    SERVER_MATCH_ONGOING = "server-match-ongoing", // same thing, but won't display a match started message on the screen
    SERVER_MATCH_START = "server-match-start", // used to allow rendering the game on the screen
    SERVER_POSSIBLE_ACTIONS = "server-possibleActions",
    SERVER_PROCESSED_ACTIONS = "server-processedActions",
    SERVER_QUEUE_OPPONENT_FOUND = "queue-opponentFound",
    SERVER_QUEUE_REGISTERED = "queue-registered",
    SERVER_HOME_ERROR_REDIRECT = "server-home-error-redirect",
    SERVER_SPAWN_ACTIVATED = "server-spawn-activated",
    SERVER_TURN_SWAP = "server-turn-swap",
    SERVER_WAITING_FOR_OPPONENT = "server-waiting-for-opponent",
}
