"""
Comprehensive LLM Feature Testing Script
Tests various features of the Gemini LLM implementation
"""

from tools.llm import GeminiLLM
from config import settings
import time
from typing import Dict, Any


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_test(test_name: str, prompt: str, response: str, metadata: Dict[str, Any] = None):
    """Print formatted test results"""
    print(f"\n📝 Test: {test_name}")
    print(f"📥 Prompt: {prompt}")
    print(f"📤 Response: {response}")
    if metadata:
        print(f"ℹ️  Metadata: {metadata}")
    print("-" * 70)


def test_basic_conversation():
    """Test basic conversation capabilities"""
    print_section("TEST 1: Basic Conversation")
    
    llm = GeminiLLM()
    
    # Test 1.1: Simple greeting
    response = llm.generate_response("Hello! How are you?")
    print_test("Simple Greeting", "Hello! How are you?", response)
    
    # Test 1.2: Question answering
    response = llm.generate_response("What is the capital of France?")
    print_test("Question Answering", "What is the capital of France?", response)
    
    # Test 1.3: Complex reasoning
    response = llm.generate_response(
        "Explain the concept of recursion in programming with a simple example."
    )
    print_test("Complex Reasoning", "Explain recursion...", response[:200] + "...")


def test_conversation_history():
    """Test conversation history handling"""
    print_section("TEST 2: Conversation History")
    
    llm = GeminiLLM()
    
    # Build conversation history
    history = []
    
    # First message
    user_msg1 = "My favorite color is blue."
    response1 = llm.generate_response(user_msg1, conversation_history=history)
    print_test("Message 1", user_msg1, response1)
    
    history.append({"role": "user", "content": user_msg1})
    history.append({"role": "assistant", "content": response1})
    
    # Follow-up message
    user_msg2 = "What did I just tell you about my favorite color?"
    response2 = llm.generate_response(user_msg2, conversation_history=history)
    print_test("Follow-up (testing memory)", user_msg2, response2)


def test_system_prompts():
    """Test custom system prompts"""
    print_section("TEST 3: Custom System Prompts")
    
    llm = GeminiLLM()
    
    # Test 3.1: Pirate personality
    system_prompt = "You are a helpful AI assistant who speaks like a pirate. Always respond in pirate speak."
    response = llm.generate_response(
        "Tell me about the weather today.",
        system_prompt=system_prompt
    )
    print_test("Pirate Personality", "Tell me about the weather", response)
    
    # Test 3.2: Technical expert
    system_prompt = "You are a senior software engineer with expertise in Python. Provide technical, detailed responses."
    response = llm.generate_response(
        "What are decorators in Python?",
        system_prompt=system_prompt
    )
    print_test("Technical Expert", "What are decorators?", response[:200] + "...")


def test_context_handling():
    """Test context integration"""
    print_section("TEST 4: Context Handling")
    
    llm = GeminiLLM()
    
    # Test with context
    context = """
    User Profile:
    - Name: John Doe
    - Age: 30
    - Occupation: Software Developer
    - Location: San Francisco
    - Interests: AI, Machine Learning, Hiking
    """
    
    response = llm.generate_response(
        "What are some good weekend activities for me?",
        context=context
    )
    print_test("Context-Aware Response", "Weekend activities?", response)


def test_temperature_variations():
    """Test different temperature settings for creativity"""
    print_section("TEST 5: Temperature Variations")
    
    llm = GeminiLLM()
    prompt = "Write a creative one-sentence story about a robot."
    
    # Low temperature (more focused)
    messages_low = [{"role": "user", "content": prompt}]
    response_low = llm.chat(messages_low, temperature=0.3)
    print_test("Low Temperature (0.3)", prompt, response_low, {"temperature": 0.3})
    
    # Medium temperature
    messages_med = [{"role": "user", "content": prompt}]
    response_med = llm.chat(messages_med, temperature=0.7)
    print_test("Medium Temperature (0.7)", prompt, response_med, {"temperature": 0.7})
    
    # High temperature (more creative)
    messages_high = [{"role": "user", "content": prompt}]
    response_high = llm.chat(messages_high, temperature=0.9)
    print_test("High Temperature (0.9)", prompt, response_high, {"temperature": 0.9})


def test_tool_synthesis():
    """Test synthesizing answers from tool outputs"""
    print_section("TEST 6: Tool Output Synthesis")
    
    llm = GeminiLLM()
    
    # Simulate tool outputs
    tool_outputs = [
        {
            "tool": "calculator",
            "result": {"success": True, "result": 42, "expression": "6 * 7"}
        },
        {
            "tool": "web_search",
            "result": "The answer to life, the universe, and everything is 42, according to 'The Hitchhiker's Guide to the Galaxy'."
        }
    ]
    
    response = llm.synthesize_answer(
        user_query="What is 6 times 7, and is there any significance to this number?",
        tool_outputs=tool_outputs,
        intent="calculation_and_information"
    )
    print_test("Tool Synthesis", "6*7 and significance?", response)


def test_multi_turn_chat():
    """Test multi-turn conversation using chat method"""
    print_section("TEST 7: Multi-Turn Chat")
    
    llm = GeminiLLM()
    
    messages = [
        {"role": "user", "content": "Let's play a word association game. I'll say a word, you respond with the first word that comes to mind."},
    ]
    
    response1 = llm.chat(messages)
    print_test("Round 1", messages[0]["content"], response1)
    
    messages.append({"role": "assistant", "content": response1})
    messages.append({"role": "user", "content": "Ocean"})
    
    response2 = llm.chat(messages)
    print_test("Round 2", "Ocean", response2)
    
    messages.append({"role": "assistant", "content": response2})
    messages.append({"role": "user", "content": "Mountain"})
    
    response3 = llm.chat(messages)
    print_test("Round 3", "Mountain", response3)


def test_edge_cases():
    """Test edge cases and error handling"""
    print_section("TEST 8: Edge Cases")
    
    llm = GeminiLLM()
    
    # Test 8.1: Empty-ish input
    response = llm.generate_response("hi")
    print_test("Very Short Input", "hi", response)
    
    # Test 8.2: Long, complex query
    long_query = """
    I'm building a web application that needs to handle user authentication, 
    store data in a database, process images, send emails, and integrate with 
    third-party APIs. What technology stack would you recommend and why? 
    Please consider scalability, security, and maintainability.
    """
    response = llm.generate_response(long_query)
    print_test("Long Complex Query", "Web app tech stack...", response[:200] + "...")
    
    # Test 8.3: Multiple questions
    response = llm.generate_response(
        "What is Python? What is JavaScript? Which one should I learn first?"
    )
    print_test("Multiple Questions", "Python vs JavaScript?", response[:200] + "...")


def test_code_generation():
    """Test code generation capabilities"""
    print_section("TEST 9: Code Generation")
    
    llm = GeminiLLM()
    
    system_prompt = "You are a helpful coding assistant. Provide clean, well-commented code."
    
    response = llm.generate_response(
        "Write a Python function to calculate the Fibonacci sequence up to n terms.",
        system_prompt=system_prompt
    )
    print_test("Code Generation", "Fibonacci function", response)


def test_max_tokens():
    """Test max tokens limitation"""
    print_section("TEST 10: Max Tokens Control")
    
    llm = GeminiLLM()
    
    prompt = "Write a detailed essay about the history of artificial intelligence."
    
    # Short response
    messages_short = [{"role": "user", "content": prompt}]
    response_short = llm.chat(messages_short, max_tokens=100)
    print_test("Short Max Tokens (100)", prompt, response_short, 
               {"max_tokens": 100, "length": len(response_short)})
    
    # Long response
    messages_long = [{"role": "user", "content": prompt}]
    response_long = llm.chat(messages_long, max_tokens=500)
    print_test("Long Max Tokens (500)", prompt, response_long[:200] + "...", 
               {"max_tokens": 500, "length": len(response_long)})


def main():
    """Run all tests"""
    print("\n" + "🧪" * 30)
    print("  GEMINI LLM COMPREHENSIVE FEATURE TESTING")
    print("🧪" * 30)
    
    # Check if API key is configured
    if not settings.gemini_api_key:
        print("\n❌ ERROR: GEMINI_API_KEY not configured in .env file")
        print("Please set your Gemini API key in the .env file before running tests.")
        return
    
    print(f"\n✅ Using Gemini Model: {settings.gemini_model}")
    print(f"✅ API Key configured: {settings.gemini_api_key[:10]}...")
    
    try:
        # Run all test suites
        test_basic_conversation()
        time.sleep(1)  # Rate limiting
        
        test_conversation_history()
        time.sleep(1)
        
        test_system_prompts()
        time.sleep(1)
        
        test_context_handling()
        time.sleep(1)
        
        test_temperature_variations()
        time.sleep(1)
        
        test_tool_synthesis()
        time.sleep(1)
        
        test_multi_turn_chat()
        time.sleep(1)
        
        test_edge_cases()
        time.sleep(1)
        
        test_code_generation()
        time.sleep(1)
        
        test_max_tokens()
        
        # Summary
        print_section("TESTING COMPLETE")
        print("\n✅ All tests executed successfully!")
        print("📊 Review the outputs above to verify LLM behavior")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
