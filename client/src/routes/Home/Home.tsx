import { Link } from "react-router-dom";
import { paths } from "../paths";

export default function Home() {
    return (
        <>
            <h1>Welcome to Color Conquerer</h1>
            <Link to={`/${paths.play}`} className="play button">
                Solo
            </Link>
            <button className="create-room">
                Multiplayer
            </button>
        </>
    );
}