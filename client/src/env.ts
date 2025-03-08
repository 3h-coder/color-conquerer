import { io } from "socket.io-client";
import { getPixiApp } from "./board-animations/pixi";

export const isDevelopment = import.meta.env.DEV;

export const API_URL =
  import.meta.env.VITE_API_URL || "https://api.color-conquerer.net";

// Docs : https://socket.io/how-to/use-with-react
export const socket = io(API_URL, {
  autoConnect: false,
  withCredentials: true,
});

export const pixiApp = getPixiApp();

export const constants = {
  localStorageKeys: {
    homeError: "homeError",
  }
};

export const HTMLElements = {
  div: "div",
};

export const EMPTY_STRING = "";
export const WHITE_SPACE = " ";
