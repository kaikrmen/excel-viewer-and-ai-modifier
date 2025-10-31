"use client";
import { motion } from "framer-motion";

export default function Hero() {
  return (
    <section className="relative overflow-hidden rounded-2xl p-10 text-center text-white">
      <div className="absolute inset-0 bg-gradient-to-r from-brand-900/70 via-brand-700/60 to-brand-800/70" />
      <motion.div
        className="absolute top-[-10%] left-[10%] h-72 w-72 rounded-full bg-blue-600/20 blur-3xl"
        animate={{ x: [0, 30, 0], y: [0, 20, 0] }}
        transition={{ repeat: Infinity, duration: 10, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute bottom-[-15%] right-[15%] h-72 w-72 rounded-full bg-blue-400/20 blur-3xl"
        animate={{ x: [0, -30, 0], y: [0, -20, 0] }}
        transition={{ repeat: Infinity, duration: 9, ease: "easeInOut" }}
      />

      <div className="relative z-10 flex flex-col items-center gap-4">
        <motion.h1
          className="text-4xl md:text-6xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-blue-300 to-cyan-300"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}>
          Excel Viewer & AI Modifier
        </motion.h1>

        <p className="text-blue-200/80 max-w-2xl text-sm md:text-lg leading-relaxed">
          Upload an <code>.xlsx</code>, preview sheets, and export an
          AI-enriched file using JSON rules.
        </p>
      </div>
    </section>
  );
}
