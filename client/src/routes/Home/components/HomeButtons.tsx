import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import CancelModal from "../../../components/modals/CancelModal";
import { useUser } from "../../../contexts/UserContext";
import { QueuePlayerDto } from "../../../dto/QueuePlayerDto";
import { Events } from "../../../enums/events";
import { socket } from "../../../env";
import { developmentLog } from "../../../utils/loggingUtils";
import { paths } from "../../paths";
import OpponentSearch from "./OpponentSearch";


export default function HomeButtons() {

    const [modalVisible, setModalVisible] = useState(false);
    const [opponentFound, setOpponentFound] = useState(false);
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

        function onQueueRegistrationSuccess() {
            developmentLog("Registered in the queue");
        }

        function waitToEnterPlayRoom() {
            setOpponentFound(true);
            developmentLog("Opponent found!");
        }

        function goToPlayRoom() {
            window.location.href = `/${paths.play}`;
        }


        socket.on("connect", registerInQueue);
        socket.on("disconnect", getOutOfModal);
        socket.on(Events.SERVER_QUEUE_REGISTERED, onQueueRegistrationSuccess)
        // TODO: remove the cancel button while waiting to enter the play room
        socket.on(Events.SERVER_QUEUE_OPPONENT_FOUND, waitToEnterPlayRoom);
        socket.on(Events.SERVER_MATCH_OPPONENT_LEFT, getOutOfModal)
        socket.on(Events.SERVER_MATCH_READY, goToPlayRoom)

        return () => {
            socket.off("connect", registerInQueue);
            socket.off("disconnect", getOutOfModal);
            socket.off(Events.SERVER_QUEUE_REGISTERED, onQueueRegistrationSuccess);
            socket.off(Events.SERVER_QUEUE_OPPONENT_FOUND, waitToEnterPlayRoom);
            socket.off(Events.SERVER_MATCH_OPPONENT_LEFT, getOutOfModal);
            socket.off(Events.SERVER_MATCH_READY, goToPlayRoom);
        };

    });

    function requestMultiplayerMatch() {
        setModalVisible(true);
        socket.connect();
    }

    function cancelMultiplayerMatchRequest() {
        getOutOfModal();
        socket.emit(Events.CLIENT_QUEUE_WITHDRAWAL, queueRegisterDto);
        socket.disconnect();
    }

    function getOutOfModal() {
        setModalVisible(false);
        setOpponentFound(false);
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
                    <CancelModal onClose={cancelMultiplayerMatchRequest} enableClosing={!opponentFound}>
                        <OpponentSearch opponentFound={opponentFound} />
                    </CancelModal>
                )
            }

        </>

    );
}