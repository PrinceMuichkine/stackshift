import os
import asyncio
from dotenv import load_dotenv
from anthropic import AsyncAnthropic

# Load environment variables
load_dotenv()
load_dotenv(".env.local")

# Claude 3.5 Sonnet model identifier
CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20240620"

async def test_claude_api():
    """Test the Claude API with a simple question"""
    try:
        # Initialize the client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        # Use AsyncAnthropic instead of Anthropic
        async with AsyncAnthropic(api_key=api_key) as client:
            # Simple test message
            response = await client.messages.create(
                model=CLAUDE_3_5_SONNET,
                max_tokens=1000,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": "What is the capital of France? Please respond in one word."
                }]
            )
            
            # Print the response
            print("\nResponse object type:", type(response))
            print("\nResponse content type:", type(response.content))
            print("\nFull response:", response)
            print("\nContent:", response.content)
            
            # Try to access the text
            if response.content:
                for content in response.content:
                    print("\nContent item type:", type(content))
                    print("Content item:", content)
                    if hasattr(content, 'text'):
                        print("Text:", content.text)
                    if hasattr(content, 'type'):
                        print("Type:", content.type)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    asyncio.run(test_claude_api()) 