import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import CancelModal from "../../../components/modals/CancelModal";
import { QueueDataDto } from "../../../dto/QueueDataDto";
import { Events } from "../../../enums/events";
import { socket } from "../../../env";
import { paths } from "../../paths";
import OpponentSearch from "./OpponentSearch";


export default function HomeButtons() {

    const [modalVisible, setModalVisible] = useState(false);
    const [idInQueue, setIdInQueue] = useState("");

    useEffect(() => {

        function registerInQueue() {
            socket.emit(Events.QUEUE_REGISTER, { message: "lalala" });
        }

        function onQueueRegistrationSuccess(data: QueueDataDto) {
            setIdInQueue(data.idInQueue);
        }

        function waitToEnterPlayRoom() {

        }

        function goToPlayRoom() {

        }


        socket.on("connect", registerInQueue);
        socket.on(Events.QUEUE_REGISTERED, onQueueRegistrationSuccess)
        // TODO: remove the cancel button while waiting to enter the play room
        socket.on(Events.MATCH_OPPONENT_FOUND, waitToEnterPlayRoom);
        socket.on(Events.MATCH_READY, goToPlayRoom)

        return () => {
            socket.off("connect", registerInQueue);
            socket.off(Events.MATCH_OPPONENT_FOUND, waitToEnterPlayRoom);
            socket.off(Events.MATCH_READY, goToPlayRoom);
        };

    }, []);

    function requestMultiplayerMatch() {
        setModalVisible(true);
        socket.connect();
    }

    function cancelMultiplayerMatchRequest() {
        setModalVisible(false);
        socket.emit(Events.QUEUE_WITHDRAWAL, idInQueue);
        socket.disconnect();
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