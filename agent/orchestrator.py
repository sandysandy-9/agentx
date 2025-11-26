from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class AgentState(BaseModel):
    """State of the agent during task execution"""
    user_input: str
    session_id: str
    user_id: str = "default_user"
    csv_data: Optional[str] = None
    
    # Thinking phase
    intent: Optional[str] = None
    task_components: List[str] = []
    required_tools: List[str] = []
    
    # Action phase
    tool_calls: List[Dict[str, Any]] = []
    tool_outputs: List[Dict[str, Any]] = []
    
    # Observe phase
    success: bool = False
    errors: List[str] = []
    
    # Answer phase
    final_answer: Optional[str] = None
    
    # Metadata
    created_at: datetime = datetime.utcnow()
    
    class Config:
        arbitrary_types_allowed = True


from tools.calculator import CalculatorTool

class AgentOrchestrator:
    """
    Core agent orchestration logic implementing Think → Act → Observe → Answer loop
    """
    
    def __init__(
        self,
        task_manager=None,
        document_search=None,
        web_search=None,
        memory=None,
        llm=None,
        visualizer=None
    ):
        self.task_manager = task_manager
        self.document_search = document_search
        self.web_search = web_search
        self.memory = memory
        self.llm = llm
        self.visualizer = visualizer
        self.calculator = CalculatorTool()
        
        self.tool_registry = {
            "task_manager": task_manager,
            "document_search": document_search,
            "web_search": web_search,
            "visualizer": visualizer,
            "calculator": self.calculator,
        }
    
    # ============== THINK PHASE ==============
    
    def think(self, state: AgentState) -> AgentState:
        """
        Analyze user input and determine:
        1. User intent
        2. Task components
        3. Required tools
        """
        user_input = state.user_input.lower()
        
        # Detect intent
        state.intent = self._detect_intent(user_input)
        
        # Break down task
        state.task_components = self._extract_task_components(user_input, state.intent)
        
        # Determine required tools
        state.required_tools = self._select_tools(user_input, state.intent)
        
        logger.info(f"THINK: Intent={state.intent}, Tools={state.required_tools}")
        
        return state
    
    def _detect_intent(self, user_input: str) -> str:
        """Detect user intent from input"""
        # Task management intents
        if any(word in user_input for word in ["create task", "add task", "new task", "remind me"]):
            return "task_create"
        elif any(word in user_input for word in ["list tasks", "show tasks", "my tasks"]):
            return "task_list"
        elif any(word in user_input for word in ["update task", "modify task", "change task"]):
            return "task_update"
        elif any(word in user_input for word in ["delete task", "remove task"]):
            return "task_delete"
        
        # Document search intents
        elif any(word in user_input for word in ["my files", "the pdf", "uploaded", "document"]):
            return "document_search"
        elif "summarize" in user_input or "summary" in user_input:
            return "document_summarize"
        
        # Web search intents
        elif any(word in user_input for word in ["latest", "current", "news", "search web"]):
            return "web_search"
        
        # Visualization intents
        elif any(word in user_input for word in ["plot", "graph", "chart", "visualize", "show me a", "bar chart", "line graph", "pie chart", "draw", "analyze data", "plot this"]):
            return "visualization"
        
        # General Q&A
        elif "?" in user_input or any(word in user_input for word in ["what", "how", "why", "when", "who"]):
            return "question_answer"
            
        # Calculator intents
        elif any(word in user_input for word in ["calculate", "solve", "math", "plus", "minus", "multiply", "divide"]) or any(c in user_input for c in "+-*/"):
            return "calculator"
        
        return "general"
    
    def _extract_task_components(self, user_input: str, intent: str) -> List[str]:
        """Extract task components from user input"""
        # For now, return the user input as single component
        # In production, use NLP to extract entities, dates, actions, etc.
        return [user_input]
    
    def _select_tools(self, user_input: str, intent: str) -> List[str]:
        """Select appropriate tools based on intent"""
        tool_mapping = {
            "task_create": ["task_manager"],
            "task_list": ["task_manager"],
            "task_update": ["task_manager"],
            "task_delete": ["task_manager"],
            "document_search": ["document_search"],
            "document_summarize": ["document_search"],
            "web_search": ["web_search"],
            "web_search": ["web_search"],
            "visualization": ["visualizer"],
            "calculator": ["calculator"],
            "question_answer": []  # Use LLM reasoning only
        }
        
        return tool_mapping.get(intent, [])
    
    # ============== ACT PHASE ==============
    
    def act(self, state: AgentState) -> AgentState:
        """
        Execute tool calls based on selected tools
        """
        for tool_name in state.required_tools:
            try:
                tool = self.tool_registry.get(tool_name)
                if not tool:
                    state.errors.append(f"Tool {tool_name} not available")
                    continue
                
                # Execute tool based on intent
                result = self._execute_tool(tool_name, tool, state)
                
                state.tool_calls.append({
                    "tool": tool_name,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                state.tool_outputs.append({
                    "tool": tool_name,
                    "result": result
                })
                
                logger.info(f"ACT: Executed {tool_name}")
                
            except Exception as e:
                error_msg = f"Error executing {tool_name}: {str(e)}"
                state.errors.append(error_msg)
                logger.error(error_msg)
        
        return state
    
    def _execute_tool(self, tool_name: str, tool: Any, state: AgentState) -> Any:
        """Execute a specific tool based on intent"""
        intent = state.intent
        user_input = state.user_input
        
        # Task Manager operations
        if tool_name == "task_manager":
            if intent == "task_list":
                return tool.list_tasks()
            # Other task operations would require parsing parameters from user_input
            # For now, return placeholder
            return {"status": "Tool execution placeholder"}
        
        # Document Search operations
        elif tool_name == "document_search":
            if intent == "document_search":
                return tool.search(user_input)
            elif intent == "document_summarize":
                return tool.summarize(user_input)
        
        # Web Search operations
        elif tool_name == "web_search":
            return tool.search(user_input)
        
        # Visualizer operations
        elif tool_name == "visualizer":
            viz_request = tool.detect_visualization_request(user_input)
            if viz_request:
                custom_data = None
                if state.csv_data:
                    try:
                        custom_data = tool.parse_csv_data(state.csv_data)
                    except Exception as e:
                        logger.error(f"Error parsing CSV data: {e}")
                
                return tool.generate_visualization(user_input, viz_request, custom_data)
            return {"success": False, "error": "Could not determine visualization type"}
        
            return {"success": False, "error": "Could not determine visualization type"}
        
        # Calculator operations
        elif tool_name == "calculator":
            return tool.execute(user_input)
        
        return None
    
    # ============== OBSERVE PHASE ==============
    
    def observe(self, state: AgentState) -> AgentState:
        """
        Evaluate tool outputs and determine success
        """
        # Check for errors
        if state.errors:
            state.success = False
            logger.warning(f"OBSERVE: Errors detected - {state.errors}")
        else:
            state.success = True
            logger.info("OBSERVE: All tools executed successfully")
        
        # Validate outputs
        for output in state.tool_outputs:
            if not output.get("result"):
                state.errors.append(f"Tool {output['tool']} returned empty result")
                state.success = False
        
        return state
    
    # ============== ANSWER PHASE ==============
    
    def answer(self, state: AgentState) -> AgentState:
        """
        Generate final answer based on tool outputs
        """
        if not state.success:
            state.final_answer = self._generate_error_response(state)
        else:
            state.final_answer = self._synthesize_answer(state)
        
        logger.info("ANSWER: Generated final response")
        
        return state
    
    def _synthesize_answer(self, state: AgentState) -> str:
        """Synthesize final answer from tool outputs"""
        intent = state.intent
        outputs = state.tool_outputs
        
        # Handle visualization intent specially (don't use LLM synthesis)
        if intent == "visualization":
            result = outputs[0]["result"] if outputs else {}
            if result.get("success"):
                viz_type = result.get("visualization_type", "chart")
                filepath = result.get("filepath", "")
                interactive = result.get("interactive", True)
                insights = result.get("insights")
                
                # Build response
                response = f"![Visualization](/visualizations/{filepath})\n\n"
                response += f"I've created an {'interactive ' if interactive else ''}{viz_type.replace('_', ' ')} for you.\n\n"
                
                # Add insights if available
                if insights and insights.get('trends'):
                    response += "**📊 Key Insights:**\n"
                    for trend in insights['trends']:
                        response += f"- {trend['column']} is {trend['direction']} (confidence: {trend['confidence']})\n"
                    
                if insights and insights.get('summary'):
                    response += "\n**📈 Statistics:**\n"
                    for col, stats in list(insights['summary'].items())[:2]:  # Show first 2 columns
                        response += f"- {col}: avg={stats['mean']:.1f}, range={stats['min']:.1f}-{stats['max']:.1f}\n"
                
                if insights and insights.get('predictions'):
                    pred = insights['predictions']
                    response += f"\n**🔮 Prediction:** Next values for {pred['column']}: {', '.join([f'{v:.1f}' for v in pred['next_values']])}\n"
                
                if interactive:
                    response += "\n*Tip: This is an interactive chart - you can zoom, pan, and hover for details!*"
                
                return response
            else:
                return f"I couldn't generate the visualization: {result.get('error', 'Unknown error')}"
        
        # Use LLM for synthesis if available (for non-visualization intents)
        if self.llm and outputs and intent != "visualization":
            try:
                return self.llm.synthesize_answer(
                    user_query=state.user_input,
                    tool_outputs=outputs,
                    intent=intent
                )
            except Exception as e:
                logger.error(f"LLM synthesis error: {e}")
                # Fall back to manual synthesis
        
        # Manual synthesis for specific intents
        if intent == "task_list":
            tasks = outputs[0]["result"] if outputs else []
            if not tasks:
                return "You have no tasks at the moment."
            
            response = f"You have {len(tasks)} task(s):\n\n"
            for i, task in enumerate(tasks, 1):
                response += f"{i}. {task.title} [{task.status}] - Priority: {task.priority}\n"
            return response
        
        elif intent == "document_search":
            results = outputs[0]["result"] if outputs else []
            if not results:
                return "No relevant information found in your documents."
            
            response = "Here's what I found:\n\n"
            for result in results[:3]:
                response += f"• {result['content'][:200]}...\n"
                response += f"  Source: {result['metadata']['filename']}\n\n"
            return response
        
        elif intent == "web_search":
            results = outputs[0]["result"] if outputs else {}
            answer = results.get("answer", "")
            sources = results.get("results", [])
            
            response = f"{answer}\n\n"
            if sources:
                response += "Sources:\n"
                for source in sources[:3]:
                    response += f"• {source.get('title', 'N/A')}: {source.get('url', 'N/A')}\n"
            return response
        
        elif intent == "calculator":
            result = outputs[0]["result"] if outputs else {}
            if result.get("success"):
                return f"The result of `{result.get('expression')}` is **{result.get('result')}**."
            else:
                return f"I couldn't calculate that. Error: {result.get('error')}"
        
        elif intent == "question_answer" or intent == "general":
            # Use LLM for general questions with conversation history
            if self.llm:
                # Get conversation history from memory if available
                conversation_history = []
                if self.memory:
                    history = self.memory.get_conversation(state.session_id, limit=6)
                    # Convert to format expected by LLM
                    for msg in history:
                        conversation_history.append({
                            "role": msg.get("role", "user"),
                            "content": msg.get("content", "")
                        })
                
                return self.llm.generate_response(
                    state.user_input,
                    conversation_history=conversation_history
                )
            return "I'm not sure how to answer that. Please try rephrasing your question."
        
        return "Task completed successfully."
    
    def _generate_error_response(self, state: AgentState) -> str:
        """Generate error response"""
        return f"I encountered some issues:\n\n" + "\n".join(f"• {error}" for error in state.errors)
    
    # ============== MAIN EXECUTION LOOP ==============
    
    def run(self, user_input: str, session_id: str, user_id: str = "default_user", csv_data: Optional[str] = None) -> str:
        """
        Execute the full Think → Act → Observe → Answer loop
        """
        logger.info(f"Starting agent run for input: {user_input}")
        
        # Initialize state
        state = AgentState(
            user_input=user_input,
            session_id=session_id,
            user_id=user_id,
            csv_data=csv_data
        )
        
        # Execute loop
        state = self.think(state)
        state = self.act(state)
        state = self.observe(state)
        state = self.answer(state)
        
        # Save to memory if available
        if self.memory:
            self.memory.save_conversation(session_id, {
                "role": "user",
                "content": user_input
            })
            self.memory.save_conversation(session_id, {
                "role": "assistant",
                "content": state.final_answer
            })
            self.memory.log_action(user_id, state.intent, {
                "tools_used": state.required_tools,
                "success": state.success
            })
        
        logger.info(f"Agent run completed. Success: {state.success}")
        
        return state.final_answer
