import { ContainerProps } from "../../components/containers";
import HomeStateContextProvider from "../../contexts/HomeStateContext";
import HomeError from "./components/HomeError";
import HomeTopMessage from "./components/HomeTopMessage";
import IntroductionCarousel from "./components/introduction-carousel/IntroductionCarousel";
import LogoAndTitle from "./components/LogoAndTitle";
import PlayButton from "./components/PlayButton";
import './styles/Home.css';

export default function Home() {


    return (
        <HomeStateContextProvider>
            <HomeContainer>
                <HomeTopMessage />
                <LogoAndTitle />
                <IntroductionCarousel />
                <PlayButton />
                <HomeError />
            </HomeContainer>
        </HomeStateContextProvider>
    );
}

function HomeContainer(props: ContainerProps) {
    return (
        <div id="home-container">
            {props.children}
        </div>
    );
}