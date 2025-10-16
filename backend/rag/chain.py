import os
from typing import Any, Dict, List, Optional

from openai import OpenAI

from backend.rag.vectorstore import PineconeVectorStore


SYSTEM_PROMPT = (
    "You are a helpful AI assistant that can answer questions about uploaded documents and engage in general conversation. "
    "When you have relevant document context provided, use it to give accurate, detailed answers. "
    "When no relevant context is available, you can still help with general questions using your knowledge. "
    "Always be friendly, helpful, and conversational. If you reference information from the provided documents, "
    "mention that it's from the uploaded content."
)


class RAGChain:
    def __init__(self) -> None:
        self.vectorstore = PineconeVectorStore()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self.client = OpenAI()
        self.chat_model = os.getenv("CHAT_MODEL", "gpt-4o-mini")

    def _build_context(self, docs: List[Dict[str, Any]]) -> str:
        lines: List[str] = []
        for d in docs:
            meta = d.get("metadata", {})
            source = meta.get("source", "unknown")
            snippet = meta.get("text") or meta.get("content") or ""
            header = f"Source: {source}"
            lines.append(header)
            lines.append(snippet)
            lines.append("")
        return "\n".join(lines)

    def _is_general_conversation(self, message: str) -> bool:
        """Check if the message is a general greeting or conversation starter that shouldn't use document context."""
        message_lower = message.lower().strip()
        
        # Common greetings and general conversation starters
        greetings = [
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
            "how are you", "how's it going", "what's up", "how do you do",
            "thanks", "thank you", "bye", "goodbye", "see you later",
            "nice to meet you", "pleasure to meet you"
        ]
        
        # Check if the message is a greeting or very short general statement
        if message_lower in greetings:
            return True
            
        # Check if it's a very short message (likely conversational)
        if len(message.split()) <= 2 and any(word in message_lower for word in ["hi", "hello", "hey", "ok", "yes", "no"]):
            return True
            
        return False

    def invoke(self, message: str, history: Optional[List[Dict[str, str]]] = None, top_k: int = 5, namespace: Optional[str] = None) -> Dict[str, Any]:
        history = history or []
        
        # Check if this is general conversation that shouldn't use document context
        is_general_conversation = self._is_general_conversation(message)
        
        if is_general_conversation:
            # For general conversation, don't retrieve documents
            retrieved = []
            context_text = ""
            user_content = message
        else:
            # For document-related queries, retrieve and use context
            retrieved = self.vectorstore.query(message, top_k=top_k, namespace=namespace)
            context_text = self._build_context(retrieved)
            
            # Only use context if we found relevant documents with good scores
            relevant_docs = [doc for doc in retrieved if doc.get("score", 0) > 0.3]
            if relevant_docs and context_text.strip():
                user_content = f"Here's some relevant information from uploaded documents:\n\n{context_text}\n\nNow, please answer this question: {message}"
            else:
                user_content = f"Question: {message}\n\n(Note: No relevant document context was found for this query, so please answer using your general knowledge.)"

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]
        # Optional: include last 3 turns of history (truncated)
        for turn in history[-3:]:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            messages.append({"role": role, "content": content})

        completion = self.client.chat.completions.create(
            model=self.chat_model,
            messages=messages,
            temperature=0.2,
        )

        answer = completion.choices[0].message.content
        citations = [
            {
                "id": d.get("id"),
                "score": d.get("score"),
                "source": d.get("metadata", {}).get("source"),
            }
            for d in retrieved
        ]

        return {"answer": answer, "citations": citations}


