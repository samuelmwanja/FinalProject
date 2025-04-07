import React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowRight, Shield, Bot, BarChart3, Settings } from "lucide-react";

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <header className="w-full bg-gradient-to-r from-primary/10 to-primary/5 border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col md:flex-row items-center justify-between">
          <div className="flex items-center space-x-2">
            <Shield className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold">SpamShield</h1>
          </div>
          <div className="flex items-center space-x-4 mt-4 md:mt-0">
            <Button variant="ghost" onClick={() => navigate("/features")}>
              Features
            </Button>
            <Button variant="ghost" onClick={() => navigate("/pricing")}>
              Pricing
            </Button>
            <Button variant="ghost" onClick={() => navigate("/about")}>
              About
            </Button>
            <Button variant="outline" onClick={() => navigate("/login")}>
              Login
            </Button>
            <Button onClick={() => navigate("/signup")}>Sign Up Free</Button>
          </div>
        </div>
      </header>

      {/* Main Hero */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 flex flex-col md:flex-row items-center">
        <div className="md:w-1/2 space-y-6">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight">
            Protect Your YouTube Channel From Spam
          </h1>
          <p className="text-xl text-muted-foreground">
            AI-powered spam detection that automatically identifies and removes
            unwanted comments, keeping your community safe and engaged.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Button size="lg" onClick={() => navigate("/signup")}>
              Get Started Free
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              onClick={() => navigate("/demo")}
            >
              Watch Demo
            </Button>
          </div>
          <p className="text-sm text-muted-foreground">
            No credit card required. Free plan includes up to 3 YouTube
            channels.
          </p>
        </div>
        <div className="md:w-1/2 mt-10 md:mt-0">
          <div className="relative rounded-lg overflow-hidden border shadow-xl">
            <img
              src="https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=800&q=80"
              alt="Dashboard Preview"
              className="w-full h-auto"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent"></div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-muted/50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">Key Features</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Bot className="h-10 w-10 text-primary" />}
              title="AI-Powered Detection"
              description="Our machine learning algorithms identify spam patterns and bot accounts with high accuracy."
            />
            <FeatureCard
              icon={<BarChart3 className="h-10 w-10 text-primary" />}
              title="Comprehensive Analytics"
              description="Track spam trends, most targeted videos, and effectiveness of your protection measures."
            />
            <FeatureCard
              icon={<Settings className="h-10 w-10 text-primary" />}
              title="Customizable Settings"
              description="Fine-tune detection sensitivity and create custom rules for your specific channel needs."
            />
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">
            Trusted by Content Creators
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <TestimonialCard
              quote="SpamShield has saved me hours of moderation time. Now I can focus on creating content instead of fighting spam."
              author="Alex Chen"
              channel="TechReviews"
              avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=Alex"
            />
            <TestimonialCard
              quote="The automated detection is incredibly accurate. It catches spam that I would have missed manually."
              author="Sarah Johnson"
              channel="Fitness Journey"
              avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah"
            />
            <TestimonialCard
              quote="Setting up was easy and the dashboard gives me great insights into what's happening in my comments section."
              author="Michael Rodriguez"
              channel="Gaming Central"
              avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=Michael"
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary text-primary-foreground py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to protect your YouTube channel?
          </h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Join thousands of content creators who trust SpamShield to keep
            their comment sections clean and engaging.
          </p>
          <Button
            size="lg"
            variant="secondary"
            onClick={() => navigate("/signup")}
            className="bg-white text-primary hover:bg-white/90"
          >
            Start Your Free Trial
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-background border-t py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2">
                <li>
                  <a
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Features
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Pricing
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Integrations
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Changelog
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Resources</h3>
              <ul className="space-y-2">
                <li>
                  <a
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Documentation
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Guides
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    API Reference
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Community
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2">
                <li>
                  <a
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    About
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Blog
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Careers
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Contact
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Legal</h3>
              <ul className="space-y-2">
                <li>
                  <a
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Privacy Policy
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Terms of Service
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    Cookie Policy
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    GDPR
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2">
              <Shield className="h-5 w-5 text-primary" />
              <span className="font-semibold">SpamShield</span>
            </div>
            <p className="text-sm text-muted-foreground mt-4 md:mt-0">
              © {new Date().getFullYear()} SpamShield. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

const FeatureCard = ({ icon, title, description }: FeatureCardProps) => {
  return (
    <div className="bg-background p-6 rounded-lg border shadow-sm hover:shadow-md transition-shadow">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </div>
  );
};

interface TestimonialCardProps {
  quote: string;
  author: string;
  channel: string;
  avatar: string;
}

const TestimonialCard = ({
  quote,
  author,
  channel,
  avatar,
}: TestimonialCardProps) => {
  return (
    <div className="bg-background p-6 rounded-lg border shadow-sm">
      <p className="italic mb-4">"{quote}"</p>
      <div className="flex items-center">
        <div className="h-10 w-10 rounded-full overflow-hidden mr-3">
          <img
            src={avatar}
            alt={author}
            className="h-full w-full object-cover"
          />
        </div>
        <div>
          <p className="font-semibold">{author}</p>
          <p className="text-sm text-muted-foreground">{channel}</p>
        </div>
      </div>
    </div>
  );
};

export default LandingPage; 