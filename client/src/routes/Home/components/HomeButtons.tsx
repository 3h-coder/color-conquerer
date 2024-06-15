import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import CancelModal from "../../../components/modals/CancelModal";
import { useHomeError } from "../../../contexts/HomeErrorContext";
import { useUser } from "../../../contexts/UserContext";
import { QueuePlayerDto } from "../../../dto/QueuePlayerDto";
import { Events } from "../../../enums/events";
import { socket } from "../../../env";
import { developmentLog } from "../../../utils/loggingUtils";
import { paths } from "../../paths";
import OpponentSearch from "./OpponentSearch";


export default function HomeButtons() {

    const [modalVisible, setModalVisible] = useState(false);
    const [intendedDisconnection, setIntendedDisconnection] = useState(false);
    const { setHomeError } = useHomeError();
    const { user } = useUser();

    const queueRegisterDto: QueuePlayerDto = {
        user: user,
        playerId: `p-${crypto.randomUUID()}`
    };

    useEffect(() => {

        function registerInQueue() {
            developmentLog("Registering in queue");
            socket.emit(Events.CLIENT_QUEUE_REGISTER, queueRegisterDto);
        }

        function onQueueFull() {
            setModalVisible(false);
            socket.disconnect();
            setHomeError("The server has reached its maximum capacity, please try again later");
        }

        function onQueueRegistrationSuccess() {
            developmentLog("Registered in the queue");
        }

        function goToPlayRoom() {
            developmentLog("Opponent found!");
            location.href = `/${paths.play}`;
        }


        socket.on("connect", registerInQueue);
        socket.on("disconnect", onDisconnect);
        socket.on(Events.SERVER_QUEUE_FULL, onQueueFull);
        socket.on(Events.SERVER_QUEUE_REGISTERED, onQueueRegistrationSuccess)
        socket.on(Events.SERVER_QUEUE_OPPONENT_FOUND, goToPlayRoom);
        socket.on(Events.SERVER_MATCH_OPPONENT_LEFT, onDisconnect)

        return () => {
            socket.off("connect", registerInQueue);
            socket.off("disconnect", onDisconnect);
            socket.off(Events.SERVER_QUEUE_FULL, onQueueFull);
            socket.off(Events.SERVER_QUEUE_REGISTERED, onQueueRegistrationSuccess);
            socket.off(Events.SERVER_QUEUE_OPPONENT_FOUND, goToPlayRoom);
            socket.off(Events.SERVER_MATCH_OPPONENT_LEFT, onDisconnect);
        };

    });

    function requestMultiplayerMatch() {
        setModalVisible(true);
        setIntendedDisconnection(false);
        socket.connect();
    }

    function cancelMultiplayerMatchRequest() {
        setModalVisible(false);
        setIntendedDisconnection(true);
        socket.emit(Events.CLIENT_QUEUE_WITHDRAWAL, queueRegisterDto);
        socket.disconnect();
    }

    function onDisconnect() {
        setModalVisible(false);
        if (!intendedDisconnection) {
            setHomeError("The connexion with the server has been lost");
        }
    }

    return (
        <>
            <div className="home-buttons-container">
                <Link to={paths.play} className="play button">
                    Solo
                </Link>
                <button onClick={requestMultiplayerMatch}>
                    Multiplayer
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