import FakeGameGrid from './FakeGameGrid';
import './IntroductionCarousel.css';
import { getFullSetup1 } from './Setups/FullSetups';

export default function IntroductionCarousel() {
    return (
        <div id="intro-carousel-container">
            <FakeGameGrid setup={getFullSetup1()} />
        </div>
    );
}