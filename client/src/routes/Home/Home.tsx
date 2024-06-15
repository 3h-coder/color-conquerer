import HomeErrorContextProvider from "../../contexts/HomeErrorContext";
import HomeButtons from "./components/HomeButtons";
import HomeError from "./components/HomeError";

export default function Home() {

    return (
        <HomeErrorContextProvider>
            <div className="home-container">
                <h1 className="main-title">Welcome to Color Conquerer</h1>
                <HomeButtons />
                <HomeError />
            </div>
        </HomeErrorContextProvider>
    );
}