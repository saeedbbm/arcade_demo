#!/usr/bin/env python3
"""
LangChain + Arcade Weather Tools Integration Example

This demonstrates how to integrate deployed weather tools with LangChain
using Arcade's official langchain-arcade package.

Reference: https://docs.arcade.dev/home/langchain/use-arcade-tools
"""

import os

# Load .env file from demo directory
try:
    from dotenv import load_dotenv
    load_dotenv()  # This will load from demo/.env
    print("✅ Loaded environment from .env file")
except ImportError:
    print("⚠️ python-dotenv not available, using system environment")

try:
    from langchain_arcade import ArcadeToolManager
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent
    from langgraph.checkpoint.memory import MemorySaver
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    print(f"❌ Install: pip install langchain-arcade langchain-openai langgraph")


def weather_langchain_demo():
    """Demo showing LangChain integration with deployed weather tools."""
    print("🤖 LangChain + Arcade Weather Tools - LIVE DEMO")
    print("=" * 55)
    
    if not LANGCHAIN_AVAILABLE:
        return
    
    # Get API keys from .env file
    arcade_api_key = "arc_o19usaCegaoBJDD3xqmQGYktA8hm3syPBeLQeGdSgDtuJR4QsHnK"
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        print("❌ Add OPENAI_API_KEY to demo/.env file:")
        print("   OPENAI_API_KEY=your_openai_key_here")
        return
    
    try:
        print("🔗 Connecting to your deployed weather tools...")
        
        # Connect to your deployed tools
        manager = ArcadeToolManager(api_key=arcade_api_key)
        tools = manager.get_tools(toolkits=["weather"])
        
        print(f"✅ Connected to weather tools: {len(tools)} available")

        # Create LangChain agent
        model = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key)
        agent = create_react_agent(
            model=model, 
            tools=tools, 
            checkpointer=MemorySaver()
        )
        
        # Configuration
        config = {
            "configurable": {
                "thread_id": "weather_demo_live",
                "user_id": "demo_user"
            }
        }
        
        print("\n🎯 Testing REAL weather queries:")
        
        queries = [
            "What's the current weather in Tokyo?",
            "Give me a 3-day forecast for London", 
            "Are there any weather alerts for Miami?"
        ]
        
        for query in queries:
            print(f"\n❓ Query: {query}")
            print("🤖 Agent response:")
            
            try:
                response = agent.invoke({
                    "messages": [("user", query)]
                }, config)
                
                # Show the actual response
                print(f"   {response['messages'][-1].content}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            print("-" * 40)
        
        print("\n🎉 Demo completed!")
        print("💡 Weather tools integrated with LangChain successfully!")

    except Exception as e:
        print(f"❌ Demo error: {e}")


if __name__ == "__main__":
    weather_langchain_demo()