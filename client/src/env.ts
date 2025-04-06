import { io } from "socket.io-client";
import { getPixiApp } from "./singletons/pixi";

// #region Constants

export const isDevelopment = import.meta.env.DEV;

export const API_URL = import.meta.env.VITE_API_URL || "https://api.color-conquerer.net";

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

export const EMPTY_STRING = "";
export const WHITE_SPACE = " ";
export const NEW_LINE = "\n";

// #endregion

// #region Singleton instances

export const pixiApp = getPixiApp();

// Docs : https://socket.io/how-to/use-with-react
export const socket = io(API_URL, {
  autoConnect: false,
  withCredentials: true,
});

// #endregion
