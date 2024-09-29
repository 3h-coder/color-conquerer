import { useEffect, useRef, useState } from "react";
import SingleButtonModal from "../../../components/modals/SingleButtonModal";
import { useHomeError } from "../../../contexts/HomeErrorContext";
import { useUser } from "../../../contexts/UserContext";
import { ClientStoredMatchInfoDto } from "../../../dto/ClientStoredMatchInfoDto";
import { ErrorDto } from "../../../dto/ErrorDto";
import { QueuePlayerDto } from "../../../dto/QueuePlayerDto";
import { Events } from "../../../enums/events";
import { constants, socket } from "../../../env";
import { developmentErrorLog, developmentLog } from "../../../utils/loggingUtils";
import { paths } from "../../paths";
import OpponentSearch from "./OpponentSearch";


export default function HomeButtons() {

    const [modalVisible, setModalVisible] = useState(false);
    const intendedDisconnection = useRef(false);
    const { setHomeError } = useHomeError();
    const { user } = useUser();

    const queuePlayerDto: QueuePlayerDto = {
        user: user,
        playerId: ""
    };

    useEffect(() => {

        function onError(errorDto: ErrorDto) {
            developmentErrorLog("An error occured", errorDto);

            setModalVisible(false);

            if (errorDto.socketConnectionKiller)
                socket.disconnect();

            if (errorDto.displayToUser)
                setHomeError(errorDto.error)
            else
                setHomeError("An unexpected error occured")
        }

        function onDisconnect() {
            setModalVisible(false);
            if (!intendedDisconnection) {
                setHomeError("The connexion with the server has been lost");
            }
            // prevent the socket client from automatically trying to reconnect
            socket.disconnect();
        }

        function onQueueRegistrationSuccess(clientStoredMatchInfoDto: ClientStoredMatchInfoDto) {
            developmentLog(`Registered in the queue, saving into local storage`, clientStoredMatchInfoDto);
            localStorage.setItem(constants.localStoragePlayerId, clientStoredMatchInfoDto.playerId);
            localStorage.setItem(constants.localStorageRoomId, clientStoredMatchInfoDto.roomId);
        }

        function goToPlayRoom() {
            developmentLog("Opponent found!");
            socket.disconnect();
            location.href = `/${paths.play}`;
        }

        socket.on("disconnect", onDisconnect);
        socket.on(Events.SERVER_ERROR, onError);
        socket.on(Events.SERVER_QUEUE_REGISTERED, onQueueRegistrationSuccess)
        socket.on(Events.SERVER_QUEUE_OPPONENT_FOUND, goToPlayRoom);

        return () => {
            socket.off("disconnect", onDisconnect);
            socket.off(Events.SERVER_ERROR, onError);
            socket.off(Events.SERVER_QUEUE_REGISTERED, onQueueRegistrationSuccess);
            socket.off(Events.SERVER_QUEUE_OPPONENT_FOUND, goToPlayRoom);
        };

    });

    function requestMultiplayerMatch() {
        setModalVisible(true);
        intendedDisconnection.current = false;

        if (!socket.connected)
            socket.connect();

        developmentLog("Attempting to register in the queue");
        socket.emit(Events.CLIENT_QUEUE_REGISTER, queuePlayerDto);
    }

    function cancelMultiplayerMatchRequest() {
        setModalVisible(false);
        intendedDisconnection.current = true;

        developmentLog("Queue player dto in cancellation", queuePlayerDto);
        socket.disconnect();
    }

    return (
        <>
            <div className="home-buttons-container">
                <button onClick={requestMultiplayerMatch}>
                    Play
                </button>
            </div>
            {
                modalVisible && (
                    <SingleButtonModal onClose={cancelMultiplayerMatchRequest} buttonText="Cancel">
                        <OpponentSearch />
                    </SingleButtonModal>
                )
            }

        </>
    );
}