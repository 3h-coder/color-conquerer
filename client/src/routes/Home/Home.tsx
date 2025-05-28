import { ContainerProps } from "../../components/containers";
import HomeStateContextProvider from "../../contexts/HomeStateContext";
import GameRulesHelp from "./components/GameRulesHelp";
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
                <PlayButtonWrapper>
                    <PlayButton />
                    <GameRulesHelp />
                </PlayButtonWrapper>
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

function PlayButtonWrapper(props: ContainerProps) {
    return (
        <div id="play-button-wrapper">
            {props.children}
        </div>
    );
}