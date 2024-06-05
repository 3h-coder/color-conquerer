import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import CancelModal from "../../../components/modals/CancelModal";
import { QueueDataDto } from "../../../dto/QueueDataDto";
import { socket } from "../../../env";
import { paths } from "../../paths";
import OpponentSearch from "./OpponentSearch";


export default function HomeButtons() {

    const [modalVisible, setModalVisible] = useState(false);
    const [idInQueue, setIdInQueue] = useState("");

    useEffect(() => {

        function registerInQueue() {
            console.log("connected");
            socket.emit("queue-register", { message: "lalala" });
        }

        function onQueueRegistrationSuccess(data: QueueDataDto) {
            setIdInQueue(data.idInQueue);
        }

        function waitToEnterPlayRoom() {

        }

        function goToPlayRoom() {

        }


        socket.on("connect", registerInQueue);
        socket.on("queue-registered", onQueueRegistrationSuccess)
        // TODO: remove the cancel button while waiting to enter the play room
        socket.on("match-opponentFound", waitToEnterPlayRoom);
        socket.on("match-ready", goToPlayRoom)

        return () => {
            socket.off("connect", registerInQueue);
            socket.off("match-opponentFound", waitToEnterPlayRoom);
            socket.off("match-ready", goToPlayRoom);
        };

    }, []);

    function requestMultiplayerMatch() {
        setModalVisible(true);
        socket.connect();
    }

    function cancelMultiplayerMatchRequest() {
        setModalVisible(false);
        socket.emit("queue-widthdrawal", idInQueue);
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