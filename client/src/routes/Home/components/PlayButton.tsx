import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import SingleButtonModal from "../../../components/modals/SingleButtonModal";
import { useHomeState } from "../../../contexts/HomeStateContext";
import { useUser } from "../../../contexts/UserContext";
import { QueuePlayerDto } from "../../../dto/player/QueuePlayerDto";
import { Events } from "../../../enums/events";
import { HomeState } from "../../../enums/homeState";
import { EMPTY_STRING, socket } from "../../../env";
import {
    developmentLog,
} from "../../../utils/loggingUtils";
import { fullPaths } from "../../paths";
import OpponentSearch from "./OpponentSearch";

interface PlayButtonProps {
    socketManager: {
        markIntentionalDisconnection: () => void;
        clearIntentionalDisconnection: () => void;
        registerModalCloseCallback: (callback: () => void) => () => void;
    };
}

export default function PlayButton({ socketManager }: PlayButtonProps) {
    const navigate = useNavigate();
    const { user } = useUser();
    const { homeState, loading: homeStateLoading } = useHomeState();
    const [mainButtonVisible, setMainButtonVisible] = useState(false);
    const [mainButtonFunction, setMainButtonFunction] = useState<() => void>(
        () => { }
    );
    const [mainButtonText, setMainButtonText] = useState(EMPTY_STRING);
    const [opponentSearchText, setOpponentSearchText] = useState("Searching for an opponent...");
    const [modalOpen, setModalOpen] = useState(false);
    const [modalCanBeClosed, setModalCanBeClosed] = useState(true);

    const queuePlayerDto: QueuePlayerDto = {
        user: user,
        playerId: EMPTY_STRING,
    };

    useEffect(() => {
        handleHomeState();

        function handleHomeState() {
            if (homeStateLoading) {
                setMainButtonVisible(false);
                return;
            }

            switch (homeState.state) {
                case HomeState.JOIN_BACK:
                    setButtonToRejoin();
                    break;

                default:
                    setButtonToPlay();
                    break;
            }
        }

        function setButtonToRejoin() {
            setMainButtonFunction(() => {
                return () => navigate(fullPaths.play);
            });
            setMainButtonText("Rejoin");
            setMainButtonVisible(true);
        }

        function setButtonToPlay() {
            setMainButtonFunction(() => {
                return () => requestMultiplayerMatch();
            });
            setMainButtonText("Play vs Player");
            setMainButtonVisible(true);
        }
    }, [homeState.state, homeStateLoading]);

    useEffect(() => {
        // Register callback to close modal on disconnect/error
        const unregister = socketManager.registerModalCloseCallback(() => {
            setModalOpen(false);
            setModalCanBeClosed(true);
        });

        return unregister;
    }, [socketManager]);

    useEffect(() => {
        function onQueueRegistrationSuccess() {
            developmentLog("Registered in the queue");
        }

        function onOpponentFound() {
            developmentLog("Opponent found!");
            setOpponentSearchText("Opponent found");
            setModalCanBeClosed(false);
        }

        socket.on(Events.SERVER_QUEUE_REGISTERED, onQueueRegistrationSuccess);
        socket.on(Events.SERVER_QUEUE_OPPONENT_FOUND, onOpponentFound);

        return () => {
            socket.off(Events.SERVER_QUEUE_REGISTERED, onQueueRegistrationSuccess);
            socket.off(Events.SERVER_QUEUE_OPPONENT_FOUND, onOpponentFound);
        };
    }, []);

    function requestMultiplayerMatch() {
        setModalOpen(true);
        socketManager.clearIntentionalDisconnection();

        if (!socket.connected) socket.connect();

        developmentLog("Attempting to register in the queue");
        socket.emit(Events.CLIENT_QUEUE_REGISTER, queuePlayerDto);
    }

    function cancelMultiplayerMatchRequest() {
        setModalOpen(false);
        socketManager.markIntentionalDisconnection();

        developmentLog("Queue player dto in cancellation", queuePlayerDto);
        socket.disconnect();
    }

    return (
        <>
            <div id="home-buttons-container">
                <button
                    onClick={mainButtonFunction}
                    style={{ opacity: mainButtonVisible ? 1 : 0 }}
                    className={homeState.state === HomeState.JOIN_BACK ? "box-shadow-glow" : EMPTY_STRING}
                >
                    {mainButtonText}
                </button>
            </div>
            <SingleButtonModal
                enableClosing={modalCanBeClosed}
                isOpenState={[modalOpen, setModalOpen]}
                onClose={cancelMultiplayerMatchRequest}
                buttonText="Cancel"
            >
                <OpponentSearch text={opponentSearchText} />
            </SingleButtonModal>
        </>
    );
}
