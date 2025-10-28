import { AnimatePresence, motion } from "framer-motion";
import { useMemo } from "react";
import { Allocate } from "./pages/Allocate";
import { DataAndSettings } from "./pages/DataAndSettings";
import { LongTable } from "./pages/LongTable";
import { Topbar } from "./components/Topbar";
import { useUIStore } from "./store/useUI";

const variants = {
  initial: { opacity: 0, y: 6 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -6 }
};

export default function App() {
  const activeTab = useUIStore((state) => state.activeTab);
  const Component = useMemo(() => {
    switch (activeTab) {
      case "allocate":
        return <Allocate />;
      case "long":
        return <LongTable />;
      default:
        return <DataAndSettings />;
    }
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-bg text-text">
      <Topbar />
      <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
        <AnimatePresence mode="wait">
          <motion.div key={activeTab} variants={variants} initial="initial" animate="animate" exit="exit" transition={{ duration: 0.3 }}>
            {Component}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
