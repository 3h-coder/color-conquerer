import { BrowserRouter, Route, Routes } from "react-router-dom";
import NotFound from "./ErrorRoutes/NotFound";
import Home from "./Home/Home";

export default function AppRoutes() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="*" element={<NotFound />} />
            </Routes>
        </BrowserRouter>
    );
}