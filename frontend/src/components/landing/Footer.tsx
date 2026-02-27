import { Shield } from "lucide-react";

const Footer = () => {
  return (
    <footer className="border-t border-border/30 bg-card/30 backdrop-blur-sm">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="grid md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-7 h-7 rounded-lg glow-button flex items-center justify-center text-[9px] font-bold">
                IX
              </div>
              <span className="text-base font-bold text-foreground">InsightX</span>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              AI-powered UPI analytics that runs entirely on your machine.
            </p>
            <div className="mt-4 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-border/40 bg-card/50 text-xs text-muted-foreground">
              <Shield className="w-3 h-3 text-accent-foreground" />
              Built for local privacy
            </div>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-sm font-semibold text-foreground mb-4">Product</h4>
            <ul className="space-y-2.5 text-sm text-muted-foreground">
              <li className="hover:text-foreground transition-colors cursor-pointer">Dashboard</li>
              <li className="hover:text-foreground transition-colors cursor-pointer">Features</li>
              <li className="hover:text-foreground transition-colors cursor-pointer">Roadmap</li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-sm font-semibold text-foreground mb-4">Resources</h4>
            <ul className="space-y-2.5 text-sm text-muted-foreground">
              <li className="hover:text-foreground transition-colors cursor-pointer">Documentation</li>
              <li className="hover:text-foreground transition-colors cursor-pointer">GitHub</li>
              <li className="hover:text-foreground transition-colors cursor-pointer">API Reference</li>
            </ul>
          </div>

          {/* Community */}
          <div>
            <h4 className="text-sm font-semibold text-foreground mb-4">Community</h4>
            <ul className="space-y-2.5 text-sm text-muted-foreground">
              <li className="hover:text-foreground transition-colors cursor-pointer">Discord</li>
              <li className="hover:text-foreground transition-colors cursor-pointer">Twitter</li>
              <li className="hover:text-foreground transition-colors cursor-pointer">Contributing</li>
            </ul>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-border/20 flex flex-col md:flex-row items-center justify-between gap-3">
          <p className="text-xs text-muted-foreground">
            © 2024 InsightX. Open-source & privacy-first.
          </p>
          <p className="text-xs text-muted-foreground">
            Made with local LLMs 🤖
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
