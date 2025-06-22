# Install `uv`

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

# Create env

```
uv venv
source .venv/bin/activate
```

# Zero-Shot Agent: AI That Just Works

## What Inspired Us
Our team has been frustrated by the gap between AI's potential and reality. While MCP (Model Context Protocol) has made AI agents incredibly powerful, setting them up feels like assembling IKEA furniture without instructions. In other words, it's technically possible, but painfully tedious. We imagined a world where you could simply say "Schedule a dinner with Sarah next Tuesday and send her the new restaurant menu" and it would just happen. No server configurations, no technical setup--just pure intention to action.

## What We Built
**Zero-Shot Agent** is an AI assistant that requires zero setup and zero coding knowledge. It automatically discovers and connects to the right tools for any task through intelligent semantic matching. For example, tell it "Check my calendar for my next free evening and email John to invite him to dinner at the new Italian place near my house" and watch it:

1. Search your Google Calendar for availability
2. Find the right restaurant through Google Maps
3. Draft a personalized email with restaurant details
4. Send the invitation through your email client
All without you touching a single configuration file

In constructing this AI powerhouse, we developed an architecture we call **Web7** that we feel is highly representative of what the future of the internet will look like. You can think of it as a network of railroads allowing AI agents to work and travel with zero friction.

## How We Built It
### The Architecture That Makes Magic Possible
- **Frontend**: React + Next.js + Tailwind CSS with real-time polling for live agent status updates
- **Backend**: FastAPI serving our core orchestration logic
- **AI Brain**: Letta-powered agent with persistent memory for complex, multi-step reasoning
- **Discovery Engine**: Qdrant vector database enabling semantic search across 100+ MCP servers (The backbone of Web7!)
- **Speed Layer**: Groq hardware for blazingly fast inference and real-time summarization
### The Technical Innovation
A key component of our application is the semantic MCP discovery system. Instead of manually configuring each service, we:

- Embed and Index: Convert MCP server descriptions into vector embeddings stored in Qdrant
- Parse and Match: Break user queries into actionable chunks, then find the best-matching services using cosine similarity
- Execute and Orchestrate: Dynamically connect the agent to the right tools and execute tasks sequentially
- Visualize and Update: Stream progress updates to a live graph showing real-time agent reasoning

This creates an experience where the complexity of AI agent orchestration becomes invisible to the user.

## Key Technical Challenges We Conquered
### Challenge 1: The MCP Server Discovery Problem
Issue: How do you find and connect to the right tools without manual setup?
Solution: We built a semantic search system and populated our vector database with hundreds of available servers. This enables fast but intelligent search so the AI agent always has access to the right tools to get the job done.
### Challenge 2: Query Decomposition at Scale
Issue: Real user requests are messy and multi-faceted ("Check calendar AND email John AND include restaurant info").
Solution: We developed an intelligent query parsing system using the AI agent itself and structured prompting that breaks complex requests into discrete, executable actions while maintaining context between them.
### Challenge 4: User Experience During Complex Operations
Issue: Multi-step AI operations can feel like black boxes to users, especially if the operations take time.
Solution: Real-time progress visualization with Groq-powered summarization, so users see exactly what's happening and why.

## What Makes This Special
In Web7, your intent seamlessly flows across any combination of services without human intervention. Instead of you jumping between Gmail, Google Calendar, Notion, and Slack to coordinate a project, AI agents orchestrate these workflows automatically. Zero-Shot Agent is the first working prototype of this future - a glimpse into an internet where friction between services simply disappears.

This isn't incremental improvement; it's infrastructural transformation. We're building the foundation for a world where every application becomes a node in an intelligent, interconnected web that serves human intention rather than demanding human navigation.

## Real-World Impact & Future Vision
We see this service representing the right infrastructure for the future of human-AI interaction, a reimaginaton of the internet that we like to call Web7. As more applications develop MCP servers, Zero-Shot Agent becomes exponentially more useful. We envision a world where applications register their AI capabilities as easily as websites register domain names today.

## Immediate applications:
- Small business owners automating workflows without hiring developers
- Students coordinating group projects across multiple platforms
- Professionals managing complex scheduling and communication tasks
The possibilities are literally endless!
