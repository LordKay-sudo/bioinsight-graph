import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import About from "./pages/About";
import GeneDetail from "./pages/GeneDetail";
import Search from "./pages/Search";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Search />} />
        <Route path="/gene/:geneId" element={<GeneDetail />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </Layout>
  );
}
