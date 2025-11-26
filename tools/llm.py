from typing import List, Dict, Any, Optional
import google.generativeai as genai
from config import settings
import logging

logger = logging.getLogger(__name__)


class GeminiLLM:
    """Gemini LLM for general chat and reasoning"""
    
    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        genai.configure(api_key=settings.gemini_api_key)
        print(f"DEBUG: Gemini Model used: {settings.gemini_model}")
        self.model = genai.GenerativeModel(settings.gemini_model)
        logger.info(f"GeminiLLM initialized with model: {settings.gemini_model}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Generate a chat response using Gemini
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
        
        Returns:
            Generated response text
        """
        try:
            # Convert OpenAI-style messages to Gemini history
            history = []
            last_user_message = ""
            system_instruction = None
            
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                
                if role == "system":
                    if system_instruction:
                        system_instruction += "\n" + content
                    else:
                        system_instruction = content
                elif role == "user":
                    last_user_message = content
                    # Don't add the last user message to history yet, it's the prompt
                elif role == "assistant":
                    history.append({"role": "model", "parts": [content]})
                
                # If we have a user message that isn't the last one, add it to history
                if role == "user" and msg != messages[-1]:
                     history.append({"role": "user", "parts": [content]})

            # Configure generation config
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            # Start chat session
            chat_session = self.model.start_chat(history=history)
            
            # Send message
            # Note: Gemini supports system instructions in the model constructor or via prompt engineering.
            # For simplicity, we'll prepend system instructions to the last user message if needed,
            # or rely on the history context.
            
            prompt = last_user_message
            if system_instruction:
                prompt = f"System Instruction: {system_instruction}\n\nUser Message: {last_user_message}"
            
            response = chat_session.send_message(
                prompt,
                generation_config=generation_config
            )
            
            answer = response.text
            logger.info(f"LLM response generated ({len(answer)} chars)")
            return answer
        
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return f"I encountered an error: {str(e)}"
    
    def generate_response(
        self,
        user_input: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a response with optional context
        
        Args:
            user_input: User's message
            context: Additional context to include
            system_prompt: Custom system prompt
            conversation_history: Previous conversation messages
        
        Returns:
            Generated response
        """
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system",
                "content": """You are AgentX, a friendly and helpful AI assistant. 
IMPORTANT GUIDELINES:
- For greetings (hi, hello, hey, etc.), respond with a brief, friendly greeting only.
- For small talk, keep responses natural and conversational.
- For follow-up requests, use conversation history.
- For questions needing detailed answers, provide comprehensive responses.
- Be concise and direct unless detailed info is requested."""
            })
        
        # Add context if provided
        if context:
            messages.append({
                "role": "system",
                "content": f"Context: {context}"
            })
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-6:]:
                messages.append(msg)
        
        # Add user input
        messages.append({"role": "user", "content": user_input})
        
        return self.chat(messages)
    
    def synthesize_answer(
        self,
        user_query: str,
        tool_outputs: List[Dict[str, Any]],
        intent: str
    ) -> str:
        """
        Synthesize a final answer from tool outputs
        """
        context_parts = []
        
        for output in tool_outputs:
            tool_name = output.get("tool", "unknown")
            result = output.get("result", {})
            context_parts.append(f"[{tool_name}] {str(result)[:500]}")
        
        context = "\n\n".join(context_parts)
        
        system_prompt = f"""You are AgentX, a helpful AI assistant. 
Based on the tool outputs below, provide a clear and concise answer to the user's query.

User Intent: {intent}

Tool Outputs:
{context}

Provide a natural, conversational response that directly addresses the user's query."""
        
        return self.generate_response(user_query, system_prompt=system_prompt)
