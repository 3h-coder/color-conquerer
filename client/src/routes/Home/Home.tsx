import { ContainerProps } from "../../components/containers";
import HomeStateContextProvider from "../../contexts/HomeStateContext";
import HomeError from "./components/HomeError";
import HomeTopMessage from "./components/HomeTopMessage";
import IntroductionCarousel from "./components/introduction-carousel/IntroductionCarousel";
import PlayButton from "./components/PlayButton";
import './styles/Home.css';

export default function Home() {


    return (
        <HomeStateContextProvider>
            <HomeContainer>
                <HomeTopMessage />
                <h1 className="main-title">Welcome to Color Conquerer</h1>
                <IntroductionCarousel />
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