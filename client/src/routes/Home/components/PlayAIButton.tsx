import { useEffect, useState } from "react";
import SingleButtonModal from "../../../components/modals/SingleButtonModal";
import { useHomeState } from "../../../contexts/HomeStateContext";
import { useUser } from "../../../contexts/UserContext";
import { QueuePlayerDto } from "../../../dto/player/QueuePlayerDto";
import { Events } from "../../../enums/events";
import { EMPTY_STRING, socket } from "../../../env";
import {
    developmentLog,
} from "../../../utils/loggingUtils";
import OpponentSearch from "./OpponentSearch";
import { HomeState } from "../../../enums/homeState";

interface PlayAIButtonProps {
    socketManager: {
        markIntentionalDisconnection: () => void;
        clearIntentionalDisconnection: () => void;
        registerModalCloseCallback: (callback: () => void) => () => void;
    };
}

export default function PlayAIButton({ socketManager }: PlayAIButtonProps) {
    const { user } = useUser();
    const { homeState, loading: homeStateLoading } = useHomeState();
    const [modalOpen, setModalOpen] = useState(false);

    const queuePlayerDto: QueuePlayerDto = {
        user: user,
        playerId: EMPTY_STRING,
    };

    useEffect(() => {
        // Register callback to close modal on disconnect/error
        const unregister = socketManager.registerModalCloseCallback(() => {
            setModalOpen(false);
        });

        return unregister;
    }, [socketManager]);

    useEffect(() => {
        function onQueueRegistrationSuccess() {
            developmentLog("Registered in the AI queue");
        }

        socket.on(Events.SERVER_QUEUE_REGISTERED, onQueueRegistrationSuccess);

        return () => {
            socket.off(Events.SERVER_QUEUE_REGISTERED, onQueueRegistrationSuccess);
        };
    }, []);

    function requestAIMatch() {
        setModalOpen(true);
        socketManager.clearIntentionalDisconnection();

        if (!socket.connected) socket.connect();

        developmentLog("Attempting to register in the AI queue");
        socket.emit(Events.CLIENT_QUEUE_AI_REGISTER, queuePlayerDto);
    }

    function cancelAIMatchRequest() {
        setModalOpen(false);
        socketManager.markIntentionalDisconnection();

        socket.disconnect();
    }

    if (homeStateLoading || homeState.state === HomeState.JOIN_BACK) {
        return null;
    }

    return (
        <>
            <button
                onClick={requestAIMatch}
                id="play-ai-button"
                className={homeStateLoading ? "skeleton" : EMPTY_STRING}
                disabled={homeStateLoading}
            >
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
