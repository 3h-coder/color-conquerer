import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import SingleButtonModal from "../../../components/modals/SingleButtonModal";
import { useHomeError } from "../../../contexts/HomeErrorContext";
import { useUser } from "../../../contexts/UserContext";
import { ErrorDto } from "../../../dto/misc/ErrorDto";
import { QueuePlayerDto } from "../../../dto/player/QueuePlayerDto";
import { Events } from "../../../enums/events";
import { EMPTY_STRING, socket } from "../../../env";
import {
    developmentErrorLog,
    developmentLog,
} from "../../../utils/loggingUtils";
import { fullPaths } from "../../paths";
import OpponentSearch from "./OpponentSearch";

export default function PlayAIButton() {
    const navigate = useNavigate();
    const { user } = useUser();
    const { setHomeError } = useHomeError();
    const [modalOpen, setModalOpen] = useState(false);
    const intendedDisconnection = { current: false };

    const queuePlayerDto: QueuePlayerDto = {
        user: user,
        playerId: EMPTY_STRING,
    };

    useEffect(() => {
        function onError(errorDto: ErrorDto) {
            developmentErrorLog("An error occured", errorDto);

            setModalOpen(false);

            if (errorDto.socketConnectionKiller) socket.disconnect();

            if (errorDto.displayToUser) setHomeError(errorDto.error);
            else setHomeError("An unexpected error occured");
        }

        function onDisconnect() {
            setModalOpen(false);
            if (!intendedDisconnection.current) {
                setHomeError("The connexion with the server has been lost");
            }
            socket.disconnect();
        }

        function onQueueRegistrationSuccess() {
            developmentLog("Registered in the AI queue");
        }

        function onGoToMatchRoom() {
            socket.disconnect();
            navigate(fullPaths.play);
        }

        socket.on(Events.DISCONNECT, onDisconnect);
        socket.on(Events.SERVER_ERROR, onError);
        socket.on(Events.SERVER_QUEUE_REGISTERED, onQueueRegistrationSuccess);
        socket.on(Events.SERVER_GO_TO_MATCH_ROOM, onGoToMatchRoom);

        return () => {
            socket.off(Events.DISCONNECT, onDisconnect);
            socket.off(Events.SERVER_ERROR, onError);
            socket.off(Events.SERVER_QUEUE_REGISTERED, onQueueRegistrationSuccess);
            socket.off(Events.SERVER_GO_TO_MATCH_ROOM, onGoToMatchRoom);
        };
    }, []);

    function requestAIMatch() {
        setModalOpen(true);
        intendedDisconnection.current = false;

        if (!socket.connected) socket.connect();

        developmentLog("Attempting to register in the AI queue");
        socket.emit(Events.CLIENT_QUEUE_AI_REGISTER, queuePlayerDto);
    }

    function cancelAIMatchRequest() {
        setModalOpen(false);
        intendedDisconnection.current = true;

        socket.disconnect();
    }

    return (
        <>
            <button onClick={requestAIMatch} id="play-ai-button">
                Play vs AI
            </button>
            <SingleButtonModal
                enableClosing={true}
                isOpenState={[modalOpen, setModalOpen]}
                onClose={cancelAIMatchRequest}
                buttonText="Cancel"
            >
                <OpponentSearch text="Starting AI match..." />
            </SingleButtonModal>
        </>
    );
}
