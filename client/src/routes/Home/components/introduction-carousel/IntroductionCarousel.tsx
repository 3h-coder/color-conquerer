import Slider from '../../../../components/slider/Slider';
import FakeGameGrid from './FakeGameGrid';
import { allSetups } from './Setups/fullSetupsy';
import './styles/IntroductionCarousel.css';

export default function IntroductionCarousel() {
    const fakeGameGrids = allSetups.map((setup, index) => (
        <FakeGameGrid
            key={`fake-game-grid-${index}`}
            gridId={`fake-game-grid-${index}`}
            index={index}
            setup={setup}
        />
    ));

    return (
        <div id="intro-carousel-container">
            <Slider slidesContent={fakeGameGrids} />
        </div>
    );
}