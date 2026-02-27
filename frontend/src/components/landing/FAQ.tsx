import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqs = [
  {
    q: "Does my data leave my computer?",
    a: "No. InsightX runs entirely locally on your machine. Your transaction data, queries, and results never leave your device. Privacy is built into the architecture, not bolted on.",
  },
  {
    q: "Do I need to know SQL?",
    a: "Not at all. Simply type or speak your question in plain English — like \"What did I spend on food last month?\" — and InsightX converts it to SQL automatically using AI.",
  },
  {
    q: "Which AI models are used?",
    a: "InsightX uses a dual-AI pipeline: Vanna AI for Text-to-SQL conversion, and Groq-powered LLMs for natural language synthesis. Whisper handles speech-to-text for voice queries.",
  },
  {
    q: "What databases are supported?",
    a: "Currently, InsightX is optimized for SQLite databases containing UPI transaction data. Support for PostgreSQL and CSV imports is on the roadmap.",
  },
  {
    q: "Is InsightX free to use?",
    a: "Yes, InsightX is open-source and free. Since everything runs locally, there are no API costs or subscription fees.",
  },
];

const FAQ = () => {
  return (
    <div className="max-w-2xl mx-auto">
      <Accordion type="single" collapsible className="space-y-2">
        {faqs.map((faq, i) => (
          <AccordionItem
            key={i}
            value={`item-${i}`}
            className="glass-card px-6 border-none rounded-xl"
          >
            <AccordionTrigger className="text-foreground font-semibold text-left hover:no-underline py-5">
              {faq.q}
            </AccordionTrigger>
            <AccordionContent className="text-muted-foreground text-sm leading-relaxed pb-5">
              {faq.a}
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
};

export default FAQ;
