import { io } from "socket.io-client";
import { getPixiApp } from "./singletons/pixi";

// #region Constants

export const EMPTY_STRING = "";
export const WHITE_SPACE = " ";
export const NEW_LINE = "\n";

export const isDevelopment = import.meta.env.DEV;

// Backend host only (no trailing slash, no `/api`)
const HOST = isDevelopment
  ? import.meta.env.VITE_DEV_BACKEND_HOST || "http://localhost:5000"
  : window.location.origin;

// Prefix for Flask API routes (e.g. /api)
const BACKEND_PREFIX = isDevelopment ? EMPTY_STRING : "/api";

// Full API base URL for fetch/axios requests
export const API_URL = `${HOST}${BACKEND_PREFIX}`;

export const localStorageKeys = {
  homePage: {
    error: "homeError"
  },
  playPage: {
    spellActionDescription: "spellActionDescription"
  }
};

export const HTMLElements = {
  div: "div",
};

// #endregion

// #region Singleton instances

export const pixiApp = getPixiApp();

// https://socket.io/how-to/use-with-react
// https://socket.io/docs/v4/client-options/
// ⚠️ The path must match the one set in the Flask socketio app (-> https://socket.io/docs/v4/client-options/#path)
export const socket = io(HOST, {
  path: `/${BACKEND_PREFIX}/socket.io/`,
  autoConnect: false,
  withCredentials: true,
});

// #endregion
