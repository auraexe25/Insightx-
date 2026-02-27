import { motion } from "framer-motion";
import { MessageSquareText, Cpu, BarChart3 } from "lucide-react";

const steps = [
  {
    icon: MessageSquareText,
    title: "Ask",
    subtitle: "NLP",
    description: "Speak or type in plain English. No SQL knowledge needed.",
  },
  {
    icon: Cpu,
    title: "Process",
    subtitle: "Vanna AI + Groq",
    description: "Converts your query to complex SQL instantly using local AI.",
  },
  {
    icon: BarChart3,
    title: "Visualize",
    subtitle: "Local SQLite",
    description: "Renders beautiful, actionable charts from your data.",
  },
];

const HowItWorks = () => {
  return (
    <div className="max-w-5xl mx-auto">
      <div className="grid md:grid-cols-3 gap-0 items-start relative">
        {steps.map((step, i) => (
          <div key={step.title} className="flex flex-col items-center text-center relative z-10">
            {/* Step Number + Icon */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.4, delay: i * 0.15 }}
              className="relative"
            >
              <div className="w-20 h-20 rounded-2xl glass-card flex items-center justify-center mb-5">
                <step.icon className="w-8 h-8 text-accent-foreground" />
              </div>
              <span className="absolute -top-2 -right-2 w-7 h-7 rounded-full glow-button flex items-center justify-center text-xs font-bold text-primary-foreground">
                {i + 1}
              </span>
            </motion.div>

            {/* Connecting Line (between steps) */}
            {i < steps.length - 1 && (
              <motion.div
                className="hidden md:block absolute top-10 left-[calc(50%+40px)] w-[calc(100%-80px)] h-[2px]"
                style={{ background: "hsl(var(--border) / 0.3)" }}
                initial={{ scaleX: 0 }}
                whileInView={{ scaleX: 1 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.6, delay: 0.3 + i * 0.15 }}
              >
                <motion.div
                  className="h-full w-full origin-left"
                  style={{
                    background: "linear-gradient(90deg, hsl(var(--gradient-start)), hsl(var(--gradient-end)))",
                  }}
                  initial={{ scaleX: 0 }}
                  whileInView={{ scaleX: 1 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{ duration: 0.8, delay: 0.5 + i * 0.2 }}
                />
              </motion.div>
            )}

            {/* Text */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.4, delay: 0.1 + i * 0.15 }}
            >
              <h3 className="text-xl font-bold text-foreground">{step.title}</h3>
              <span className="text-xs font-mono text-accent-foreground/70 tracking-wider uppercase">
                {step.subtitle}
              </span>
              <p className="text-sm text-muted-foreground mt-3 max-w-[220px] mx-auto leading-relaxed">
                {step.description}
              </p>
            </motion.div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HowItWorks;
