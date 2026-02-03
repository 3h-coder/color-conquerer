import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import SingleButtonModal from "../../../components/modals/SingleButtonModal";
import { useHomeError } from "../../../contexts/HomeErrorContext";
import { useHomeState } from "../../../contexts/HomeStateContext";
import { useUser } from "../../../contexts/UserContext";
import { ErrorDto } from "../../../dto/misc/ErrorDto";
import { QueuePlayerDto } from "../../../dto/player/QueuePlayerDto";
import { Events } from "../../../enums/events";
import { HomeState } from "../../../enums/homeState";
import { EMPTY_STRING, socket } from "../../../env";
import {
    developmentErrorLog,
    developmentLog,
} from "../../../utils/loggingUtils";
import { fullPaths } from "../../paths";
import OpponentSearch from "./OpponentSearch";

export default function PlayButton() {
    const navigate = useNavigate();
    const { user } = useUser();
    const { setHomeError } = useHomeError();
    const { homeState, loading: homeStateLoading } = useHomeState();
    const [mainButtonVisible, setMainButtonVisible] = useState(false);
    const [mainButtonFunction, setMainButtonFunction] = useState<() => void>(
        () => { }
    );
    const [mainButtonText, setMainButtonText] = useState(EMPTY_STRING);
    const [opponentSearchText, setOpponentSearchText] = useState("Searching for an opponent...");
    const [modalOpen, setModalOpen] = useState(false);
    const [modalCanBeClosed, setModalCanBeClosed] = useState(true);
    const intendedDisconnection = useRef(false);

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
        function onError(errorDto: ErrorDto) {
            developmentErrorLog("An error occured", errorDto);

            setModalOpen(false);

            if (errorDto.socketConnectionKiller) socket.disconnect();

            if (errorDto.displayToUser) setHomeError(errorDto.error);
            else setHomeError("An unexpected error occured");
        }

        function onDisconnect() {
            setModalOpen(false);
            setModalCanBeClosed(true);
            if (!intendedDisconnection) {
                setHomeError("The connexion with the server has been lost");
            }
            // prevent the socket client from automatically trying to reconnect
            socket.disconnect();
        }

        function onQueueRegistrationSuccess() {
            developmentLog("Registered in the queue");
        }

        function onOpponentFound() {
            developmentLog("Opponent found!");
            setOpponentSearchText("Opponent found");
            setModalCanBeClosed(false);
        }

        function onGoToMatchRoom() {
            socket.disconnect();
            navigate(fullPaths.play);
        }

        socket.on(Events.DISCONNECT, onDisconnect);
        socket.on(Events.SERVER_ERROR, onError);
        socket.on(Events.SERVER_QUEUE_REGISTERED, onQueueRegistrationSuccess);
        socket.on(Events.SERVER_QUEUE_OPPONENT_FOUND, onOpponentFound);
        socket.on(Events.SERVER_GO_TO_MATCH_ROOM, onGoToMatchRoom);

        return () => {
            socket.off(Events.DISCONNECT, onDisconnect);
            socket.off(Events.SERVER_ERROR, onError);
            socket.off(Events.SERVER_QUEUE_REGISTERED, onQueueRegistrationSuccess);
            socket.off(Events.SERVER_QUEUE_OPPONENT_FOUND, onOpponentFound);
            socket.off(Events.SERVER_GO_TO_MATCH_ROOM, onGoToMatchRoom);
        };
    }, []);

    function requestMultiplayerMatch() {
        setModalOpen(true);
        intendedDisconnection.current = false;

        if (!socket.connected) socket.connect();

        developmentLog("Attempting to register in the queue");
        socket.emit(Events.CLIENT_QUEUE_REGISTER, queuePlayerDto);
    }

    function cancelMultiplayerMatchRequest() {
        setModalOpen(false);
        intendedDisconnection.current = true;

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
