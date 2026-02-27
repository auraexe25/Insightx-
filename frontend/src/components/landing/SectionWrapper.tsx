import { motion } from "framer-motion";
import { ReactNode } from "react";

interface SectionWrapperProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  className?: string;
}

const SectionWrapper = ({ children, title, subtitle, className = "" }: SectionWrapperProps) => {
  return (
    <motion.section
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.5 }}
      className={`relative z-10 px-6 py-20 md:py-28 ${className}`}
    >
      {(title || subtitle) && (
        <div className="text-center mb-14">
          {title && (
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-foreground mb-4">
              {title}
            </h2>
          )}
          {subtitle && (
            <p className="text-base md:text-lg text-muted-foreground max-w-xl mx-auto">
              {subtitle}
            </p>
          )}
        </div>
      )}
      {children}
    </motion.section>
  );
};

export default SectionWrapper;
