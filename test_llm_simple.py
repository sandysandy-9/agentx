"""
Simple LLM Feature Testing Script - Tests key features with plain text output
"""

from tools.llm import GeminiLLM
from config import settings
import time


def test_basic_features():
    """Test basic LLM features"""
    print("\n" + "=" * 70)
    print("  GEMINI LLM FEATURE TESTING")
    print("=" * 70)
    
    # Check API key
    if not settings.gemini_api_key:
        print("\nERROR: GEMINI_API_KEY not configured")
        return
    
    print(f"\nUsing Model: {settings.gemini_model}")
    print(f"API Key: {settings.gemini_api_key[:10]}...")
    
    llm = GeminiLLM()
    
    # Test 1: Basic conversation
    print("\n\nTEST 1: Basic Conversation")
    print("-" * 70)
    response = llm.generate_response("Hello! What is 2+2?")
    print(f"Prompt: Hello! What is 2+2?")
    print(f"Response: {response}")
    
    time.sleep(1)
    
    # Test 2: Conversation with history
    print("\n\nTEST 2: Conversation History")
    print("-" * 70)
    history = []
    
    msg1 = "My name is Alice"
    resp1 = llm.generate_response(msg1, conversation_history=history)
    print(f"User: {msg1}")
    print(f"AI: {resp1}")
    
    history.append({"role": "user", "content": msg1})
    history.append({"role": "assistant", "content": resp1})
    
    time.sleep(1)
    
    msg2 = "What is my name?"
    resp2 = llm.generate_response(msg2, conversation_history=history)
    print(f"\nUser: {msg2}")
    print(f"AI: {resp2}")
    
    time.sleep(1)
    
    # Test 3: Custom system prompt
    print("\n\nTEST 3: Custom System Prompt")
    print("-" * 70)
    system_prompt = "You are a helpful assistant who always answers in haiku format."
    response = llm.generate_response(
        "Tell me about Python programming",
        system_prompt=system_prompt
    )
    print(f"System Prompt: Answer in haiku format")
    print(f"Prompt: Tell me about Python programming")
    print(f"Response: {response}")
    
    time.sleep(1)
    
    # Test 4: Context handling
    print("\n\nTEST 4: Context Handling")
    print("-" * 70)
    context = "User is a Python developer learning Machine Learning"
    response = llm.generate_response(
        "What should I learn next?",
        context=context
    )
    print(f"Context: {context}")
    print(f"Prompt: What should I learn next?")
    print(f"Response: {response}")
    
    time.sleep(1)
    
    # Test 5: Temperature variation
    print("\n\nTEST 5: Temperature Variations")
    print("-" * 70)
    prompt = "Complete this sentence: The future of AI is"
    
    messages = [{"role": "user", "content": prompt}]
    resp_low = llm.chat(messages, temperature=0.3)
    print(f"Prompt: {prompt}")
    print(f"Response (temp=0.3): {resp_low}")
    
    time.sleep(1)
    
    messages = [{"role": "user", "content": prompt}]
    resp_high = llm.chat(messages, temperature=0.9)
    print(f"Response (temp=0.9): {resp_high}")
    
    time.sleep(1)
    
    # Test 6: Code generation
    print("\n\nTEST 6: Code Generation")
    print("-" * 70)
    response = llm.generate_response(
        "Write a Python function to reverse a string"
    )
    print(f"Prompt: Write a Python function to reverse a string")
    print(f"Response:\n{response}")
    
    time.sleep(1)
    
    # Test 7: Complex reasoning
    print("\n\nTEST 7: Complex Reasoning")
    print("-" * 70)
    response = llm.generate_response(
        "If a train leaves New York at 2 PM traveling at 60 mph, and another train leaves Boston at 3 PM traveling at 80 mph, when will they meet if the cities are 200 miles apart?"
    )
    print(f"Prompt: [Train problem - complex reasoning]")
    print(f"Response: {response}")
    
    time.sleep(1)
    
    # Test 8: Tool synthesis
    print("\n\nTEST 8: Tool Output Synthesis")
    print("-" * 70)
    tool_outputs = [
        {
            "tool": "calculator",
            "result": {"success": True, "result": 144, "expression": "12 * 12"}
        },
        {
            "tool": "search",
            "result": "144 is a perfect square, also known as a gross (12 dozen)"
        }
    ]
    response = llm.synthesize_answer(
        user_query="What is 12 times 12 and what's special about this number?",
        tool_outputs=tool_outputs,
        intent="calculation_and_facts"
    )
    print(f"Query: What is 12 times 12 and what's special about it?")
    print(f"Tool outputs: calculator=144, search=fun facts")
    print(f"Synthesized Response: {response}")
    
    # Summary
    print("\n\n" + "=" * 70)
    print("  TESTING COMPLETE - All 8 test categories executed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_basic_features()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
