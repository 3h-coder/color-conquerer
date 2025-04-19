import { ContainerProps } from "../../components/containers";
import HomeStateContextProvider from "../../contexts/HomeStateContext";
import './Home.css';
import HomeError from "./components/HomeError";
import HomeTopMessage from "./components/HomeTopMessage";
import PlayButton from "./components/PlayButton";

export default function Home() {


    return (
        <HomeStateContextProvider>
            <HomeContainer>
                <HomeTopMessage />
                <h1 className="main-title">Welcome to Color Conquerer</h1>
                <PlayButton />
                <HomeError />
            </HomeContainer>
        </HomeStateContextProvider>
    );
}

function HomeContainer(props: ContainerProps) {
    return (
        <div className="home-container">
            {props.children}
        </div>
    );
}