import pytest
from unittest.mock import MagicMock, patch
from tools.llm import GeminiLLM
import os

# Mock settings to avoid needing real env vars for basic test
@patch('tools.llm.settings')
@patch('tools.llm.genai')
def test_gemini_llm_init(mock_genai, mock_settings):
    mock_settings.gemini_api_key = "test_key"
    mock_settings.gemini_model = "gemini-2.5-flash-preview-09-2025"
    
    llm = GeminiLLM()
    
    mock_genai.configure.assert_called_with(api_key="test_key")
    mock_genai.GenerativeModel.assert_called_with("gemini-2.5-flash-preview-09-2025")

@patch('tools.llm.settings')
@patch('tools.llm.genai')
def test_gemini_chat(mock_genai, mock_settings):
    mock_settings.gemini_api_key = "test_key"
    mock_settings.gemini_model = "gemini-2.5-flash-preview-09-2025"
    
    # Mock the model and chat session
    mock_model = MagicMock()
    mock_chat = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Hello from Gemini"
    
    mock_genai.GenerativeModel.return_value = mock_model
    mock_model.start_chat.return_value = mock_chat
    mock_chat.send_message.return_value = mock_response
    
    llm = GeminiLLM()
    response = llm.chat([{"role": "user", "content": "Hi"}])
    
    assert response == "Hello from Gemini"
    mock_model.start_chat.assert_called()
    mock_chat.send_message.assert_called()

if __name__ == "__main__":
    # Manual run check (requires real key)
    try:
        from config import settings
        if settings.gemini_api_key:
            print("Testing with REAL API key...")
            # Force the model that we know exists
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")
            response = model.generate_content("Hello, who are you?")
            print(f"Response: {response.text}")
        else:
            print("Skipping real API test (no key configured)")
    except Exception as e:
        print(f"Manual test failed: {e}")
