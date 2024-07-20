import { io } from 'socket.io-client';

export const isDevelopment = import.meta.env.DEV;

export const API_URL = import.meta.env.VITE_API_URL || "https://api.color-conquerer.net";

// Docs : https://socket.io/how-to/use-with-react
export const socket = io(API_URL, {
    autoConnect: false,
    withCredentials: true
});
