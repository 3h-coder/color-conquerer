import { BrowserRouter, Route, Routes } from "react-router-dom";
import NotFound from "./ErrorRoutes/NotFound";
import Home from "./Home/Home";
import { paths } from "./paths";
import Play from "./Play/Play";

export default function AppRoutes() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path={paths.play} element={<Play />} />
                <Route path="*" element={<NotFound />} />
            </Routes>
        </BrowserRouter>
    );
}