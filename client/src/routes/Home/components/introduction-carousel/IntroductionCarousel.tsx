import FakeGameGrid from './FakeGameGrid';
import './IntroductionCarousel.css';
import { getFullSetup1 } from './Setups/fullSetups';

export default function IntroductionCarousel() {
    return (
        <div id="intro-carousel-container">
            <FakeGameGrid gridId="fake-game-grid-1" setup={getFullSetup1()} />
        </div>
    );
}