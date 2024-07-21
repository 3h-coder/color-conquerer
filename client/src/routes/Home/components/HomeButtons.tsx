import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import CancelModal from "../../../components/modals/CancelModal";
import { useHomeError } from "../../../contexts/HomeErrorContext";
import { useUser } from "../../../contexts/UserContext";
import { QueuePlayerDto } from "../../../dto/QueuePlayerDto";
import { Events } from "../../../enums/events";
import { socket } from "../../../env";
import { developmentErrorLog, developmentLog } from "../../../utils/loggingUtils";
import { paths } from "../../paths";
import OpponentSearch from "./OpponentSearch";
import { ErrorDto } from "../../../dto/ErrorDto";


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
        }

        function registerInQueue() {
            developmentLog("Attempting to register in the queue");
            socket.emit(Events.CLIENT_QUEUE_REGISTER, queuePlayerDto);
        }

        function onAlreadyRegistered() {
            setModalVisible(false);
            setHomeError("You are already registered in the queue");
        }

        function onQueueFull() {
            setModalVisible(false);
            socket.disconnect();
            setHomeError("The server has reached its maximum capacity, please try again later");
        }

        function onQueueRegistrationSuccess(playerId: string) {
            queuePlayerDto.playerId = playerId;
            developmentLog(`Registered in the queue ${queuePlayerDto.playerId}`);
        }

        function goToPlayRoom() {
            developmentLog("Opponent found!");
            location.href = `/${paths.play}`;
        }

        socket.on("connect", registerInQueue);
        socket.on("disconnect", onDisconnect);
        socket.on(Events.SERVER_ERROR, onError);
        socket.on(Events.SERVER_QUEUE_FULL, onQueueFull);
        socket.on(Events.SERVER_QUEUE_REGISTERED, onQueueRegistrationSuccess)
        socket.on(Events.SERVER_QUEUE_OPPONENT_FOUND, goToPlayRoom);
        socket.on(Events.SERVER_MATCH_OPPONENT_LEFT, onDisconnect)

        return () => {
            socket.off("connect", registerInQueue);
            socket.off("disconnect", onDisconnect);
            socket.off(Events.SERVER_ERROR, onError);
            socket.off(Events.SERVER_QUEUE_FULL, onQueueFull);
            socket.off(Events.SERVER_QUEUE_REGISTERED, onQueueRegistrationSuccess);
            socket.off(Events.SERVER_QUEUE_OPPONENT_FOUND, goToPlayRoom);
            socket.off(Events.SERVER_MATCH_OPPONENT_LEFT, onDisconnect);
        };

    });

    function requestMultiplayerMatch() {
        setModalVisible(true);
        intendedDisconnection.current = false;
        if (!socket.connected)
            socket.connect();
    }

    function cancelMultiplayerMatchRequest() {
        setModalVisible(false);
        intendedDisconnection.current = true;
        developmentLog("Queue player dto in cancellation", queuePlayerDto);
        socket.emit(Events.CLIENT_QUEUE_WITHDRAWAL, queuePlayerDto);
        socket.disconnect();
    }

    return (
        <>
            <div className="home-buttons-container">
                <Link to={paths.play} className="play button">
                    Play vs AI
                </Link>
                <button onClick={requestMultiplayerMatch}>
                    Play vs Player
                </button>
            </div>
            {
                modalVisible && (
                    <CancelModal onClose={cancelMultiplayerMatchRequest}>
                        <OpponentSearch />
                    </CancelModal>
                )
            }

        </>
    );
}