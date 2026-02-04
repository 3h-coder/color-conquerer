import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useHomeError } from "../../../contexts/HomeErrorContext";
import { ErrorDto } from "../../../dto/misc/ErrorDto";
import { Events } from "../../../enums/events";
import { socket } from "../../../env";
import { developmentErrorLog } from "../../../utils/loggingUtils";
import { fullPaths } from "../../paths";

/**
 * Centralized hook for managing socket connections on the home page.
 * Prevents duplicate event listeners from PlayButton and PlayAIButton.
 */
export function useHomeSocketManager() {
    const navigate = useNavigate();
    const location = useLocation();
    const { setHomeError } = useHomeError();
    const intendedDisconnection = useRef(false);
    const [modalCloseCallbacks] = useState<Set<() => void>>(new Set());

    // Check if navigation came from an intentional disconnect (e.g., match end)
    useEffect(() => {
        if (location.state?.intentionalDisconnect) {
            intendedDisconnection.current = true;
        }
    }, [location.state]);

    useEffect(() => {
        function onError(errorDto: ErrorDto) {
            developmentErrorLog("An error occured", errorDto);

            // Close any open modals
            modalCloseCallbacks.forEach(callback => callback());

            if (errorDto.socketConnectionKiller)
                socket.disconnect();

            if (errorDto.displayToUser)
                setHomeError(errorDto.error);
            else
                setHomeError("An unexpected error occured");
        }

        function onDisconnect() {
            // Close any open modals
            modalCloseCallbacks.forEach(callback => callback());

            if (!intendedDisconnection.current) {
                setHomeError("The connexion with the server has been lost");
            }
            // prevent the socket client from automatically trying to reconnect
            socket.disconnect();
        }

        function onGoToMatchRoom() {
            intendedDisconnection.current = true;
            socket.disconnect();
            navigate(fullPaths.play);
        }

        socket.on(Events.DISCONNECT, onDisconnect);
        socket.on(Events.SERVER_ERROR, onError);
        socket.on(Events.SERVER_GO_TO_MATCH_ROOM, onGoToMatchRoom);

        return () => {
            socket.off(Events.DISCONNECT, onDisconnect);
            socket.off(Events.SERVER_ERROR, onError);
            socket.off(Events.SERVER_GO_TO_MATCH_ROOM, onGoToMatchRoom);
        };
    }, [navigate, setHomeError, modalCloseCallbacks]);

    const markIntentionalDisconnection = () => {
        intendedDisconnection.current = true;
    };

    const clearIntentionalDisconnection = () => {
        intendedDisconnection.current = false;
    };

    const registerModalCloseCallback = (callback: () => void) => {
        modalCloseCallbacks.add(callback);
        return () => {
            modalCloseCallbacks.delete(callback);
        };
    };

    return {
        markIntentionalDisconnection,
        clearIntentionalDisconnection,
        registerModalCloseCallback,
    };
}
