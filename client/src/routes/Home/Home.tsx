import HomeErrorContextProvider from "../../contexts/HomeErrorContext";
import HomeStateContextProvider from "../../contexts/HomeStateContext";
import '../../style/css/Home.css';
import HomeButtons from "./components/HomeButtons";
import HomeError from "./components/HomeError";
import HomeTopMessage from "./components/HomeTopMessage";

export default function Home() {


    return (
        <HomeStateContextProvider>
            <HomeErrorContextProvider>
                <div className="home-container">
                    <HomeTopMessage />
                    <h1 className="main-title">Welcome to Color Conquerer</h1>
                    <HomeButtons />
                    <HomeError />
                </div>
            </HomeErrorContextProvider>
        </HomeStateContextProvider>
    );
}