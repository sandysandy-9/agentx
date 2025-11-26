import sys
import traceback

print("Starting debug...")

try:
    print("Importing config...")
    from config import settings
    print("Config imported.")
except Exception:
    traceback.print_exc()

try:
    print("Importing GeminiLLM...")
    from tools.llm import GeminiLLM
    llm = GeminiLLM()
    print("GeminiLLM imported.")
except Exception:
    traceback.print_exc()

try:
    print("Importing WebSearchTool...")
    from tools.web_search import WebSearchTool
    web = WebSearchTool()
    print("WebSearchTool imported.")
except Exception:
    traceback.print_exc()

try:
    print("Importing DocumentSearchEngine...")
    from tools.document_search import DocumentSearchEngine
    doc = DocumentSearchEngine()
    print("DocumentSearchEngine imported.")
except Exception:
    traceback.print_exc()

print("Debug complete.")
