import { motion } from "framer-motion";
import type { ButtonHTMLAttributes } from "react";
import { cn } from "../utils";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  icon?: string;
  variant?: "primary" | "ghost";
}

export function GlowButton({ icon, children, variant = "primary", className, ...props }: ButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.03, y: -2 }}
      whileTap={{ scale: 0.97 }}
      className={cn(
        "flex items-center gap-2 rounded-full px-4 py-2 transition-colors",
        variant === "primary"
          ? "bg-accent/20 text-accent hover:bg-accent/30"
          : "bg-surfaceAlt text-muted hover:text-text",
        className
      )}
      {...props}
    >
      {icon ? <span className="text-lg">{icon}</span> : null}
      <span>{children}</span>
    </motion.button>
  );
}
