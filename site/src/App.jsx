import manifest from "../../academy/manifest.json";
const modules = manifest.stages.flatMap(stage => stage.modules);
import Hero from "./sections/Hero.jsx";
import PathSection from "./sections/PathSection.jsx";
import MachineSection from "./sections/MachineSection.jsx";
import ConstellationSection from "./sections/ConstellationSection.jsx";
import CampSection from "./sections/CampSection.jsx";

export default function App() {
  return (
    <>
      <a className="skip-link" href="#machine">
        跳到核心裝置
      </a>
      <Hero />
      <main>
        <MachineSection />
        <CampSection />
        <PathSection />
        <ConstellationSection />
      </main>
      <section className="finale wrap" aria-label="尾聲">
        <p>紙還在寫，機器還在轉。</p>
        <p className="small">MINIACADEMY · {modules.filter(module => module.status === "ready").length} READY / {modules.length} MODULES · PYTHON RUNTIME: STDLIB</p>
      </section>
      <div className="wrap">
        <footer>
          <span>MiniHarness · MIT License</span>
          <span>互動示範依教程設計 · 學習狀態由本人記錄</span>
          <span>手稿成機 · 2026</span>
        </footer>
      </div>
    </>
  );
}
