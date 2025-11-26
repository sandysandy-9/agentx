from typing import List, Dict, Any, Optional
import httpx
from config import settings
import logging
import json
import re

logger = logging.getLogger(__name__)


class WebSearchTool:
    """Web search integration using Perplexity API (includes built-in search)"""
    
    def __init__(self):
        if not settings.perplexity_api_key:
            raise ValueError("PERPLEXITY_API_KEY not configured")
        
        self.api_key = settings.perplexity_api_key
        self.base_url = "https://api.perplexity.ai"
        self.model = settings.perplexity_model
        self.max_searches = settings.max_web_searches_per_query
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform a web search using Perplexity
        """
        try:
            # Build enhanced query with domain filters
            enhanced_query = query
            if include_domains:
                enhanced_query += f" (focus on sources: {', '.join(include_domains)})"
            if exclude_domains:
                enhanced_query += f" (exclude sources: {', '.join(exclude_domains)})"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides accurate, well-researched answers with citations."
                    },
                    {
                        "role": "user",
                        "content": enhanced_query
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 1024
            }
            
            # Use httpx directly
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
            
            answer = data["choices"][0]["message"]["content"]
            
            # Extract citations if present
            citations = self._extract_citations(answer)
            
            logger.info(f"Web search completed for: {query}")
            return {
                "query": query,
                "answer": answer,
                "results": citations,
                "model": self.model
            }
        
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return {
                "query": query,
                "results": [],
                "answer": f"Search failed: {str(e)}",
                "error": str(e)
            }
    
    def _extract_citations(self, text: str) -> List[Dict[str, Any]]:
        """Extract citation-like patterns from Perplexity response"""
        citations = []
        
        # Find citation numbers like [1], [2]
        citation_nums = re.findall(r'\[(\d+)\]', text)
        
        if citation_nums:
            for num in set(citation_nums):
                citations.append({
                    "title": f"Source {num}",
                    "url": f"Cited in response [{num}]",
                    "content": "Citation embedded in response"
                })
        
        return citations
    
    def get_answer(self, query: str) -> str:
        """Get a direct answer to a query"""
        result = self.search(query, max_results=3, search_depth="advanced")
        return result.get("answer", "No answer found.")
    
    def search_news(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for recent news articles"""
        result = self.search(
            query=f"{query} news",
            max_results=max_results,
            search_depth="advanced"
        )
        return result.get("results", [])
    
    def compare_sources(self, query: str, sources: List[str]) -> Dict[str, Any]:
        """Compare information across specific sources"""
        results = {}
        
        for source in sources[:self.max_searches]:
            search_result = self.search(
                query=query,
                include_domains=[source]
            )
            results[source] = search_result.get("answer", "")
        
        return {
            "query": query,
            "sources": results,
            "comparison_summary": self._generate_comparison(results)
        }
    
    def _generate_comparison(self, results: Dict[str, str]) -> str:
        """Generate a comparison summary"""
        summaries = []
        for source, answer in results.items():
            if answer and not answer.startswith("Search failed"):
                summaries.append(f"{source}: Information found")
            else:
                summaries.append(f"{source}: No results")
        
        return "; ".join(summaries)
