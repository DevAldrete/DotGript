"""
AI-powered codebase analysis and comprehension system.
Handles embedding generation, vector storage, and intelligent code understanding.
"""
import json
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

import chromadb
import tiktoken
from sentence_transformers import SentenceTransformer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from gript.core.settings import settings


@dataclass
class CodeChunk:
    """Represents a chunk of code with metadata."""
    content: str
    file_path: str
    start_line: int
    end_line: int
    chunk_hash: str
    language: str
    file_size: int
    last_modified: float


@dataclass
class UsageStats:
    """Tracks AI usage statistics."""
    total_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    monthly_requests: int = 0
    monthly_tokens: int = 0
    monthly_cost_usd: float = 0.0
    last_reset_date: Optional[str] = None
    last_index_update: Optional[str] = None


class CodebaseAnalysisContext(BaseModel):
    """Context for codebase analysis queries."""
    query: str
    relevant_chunks: List[Dict[str, Any]] = Field(default_factory=list)
    file_structure: Dict[str, Any] = Field(default_factory=dict)
    project_info: Dict[str, Any] = Field(default_factory=dict)


class CodebaseWatcher(FileSystemEventHandler):
    """Watches for file changes and triggers re-indexing."""
    
    def __init__(self, indexer: 'CodebaseIndexer'):
        self.indexer = indexer
        self.last_update = time.time()
        self.update_threshold = 2.0  # Minimum seconds between updates
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        current_time = time.time()
        if current_time - self.last_update < self.update_threshold:
            return
        
        file_path = Path(event.src_path)
        if self.indexer._should_index_file(file_path):
            print(f"🔄 File changed: {file_path.name}, scheduling re-index...")
            self.indexer.index_file(file_path)
            self.last_update = current_time


class CodebaseIndexer:
    """Handles codebase indexing using embeddings and vector storage."""
    
    def __init__(self, project_root: Path, config_path: Path):
        self.project_root = project_root
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize vector database
        self.chroma_client = chromadb.PersistentClient(
            path=str(project_root / ".gript" / "vector_db")
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name="codebase_chunks",
            metadata={"description": "Code chunks with embeddings"}
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize tokenizer for token counting
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # File watcher for auto-indexing
        self.observer = None
        if self.config.get("ai_config", {}).get("auto_index_on_change", True):
            self._setup_file_watcher()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from .gript/.conf.json"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_config(self):
        """Save configuration back to .gript/.conf.json"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _setup_file_watcher(self):
        """Setup file system watcher for auto-indexing."""
        self.observer = Observer()
        event_handler = CodebaseWatcher(self)
        self.observer.schedule(event_handler, str(self.project_root), recursive=True)
        self.observer.start()
    
    def _should_index_file(self, file_path: Path) -> bool:
        """Check if a file should be indexed."""
        ai_config = self.config.get("ai_config", {})
        include_types = ai_config.get("index_file_types", [".py", ".js", ".ts", ".md"])
        exclude_patterns = ai_config.get("exclude_patterns", ["__pycache__", ".git"])
        
        # Check file extension
        if file_path.suffix not in include_types:
            return False
        
        # Check exclude patterns
        for pattern in exclude_patterns:
            if pattern in str(file_path):
                return False
        
        return True
    
    def _chunk_code(self, content: str, file_path: Path) -> List[CodeChunk]:
        """Split code into manageable chunks."""
        ai_config = self.config.get("ai_config", {})
        chunk_size = ai_config.get("chunk_size", 1000)
        chunk_overlap = ai_config.get("chunk_overlap", 200)
        
        lines = content.split('\n')
        chunks = []
        
        i = 0
        while i < len(lines):
            # Calculate chunk end
            chunk_lines = []
            char_count = 0
            start_line = i + 1
            
            while i < len(lines) and char_count < chunk_size:
                line = lines[i]
                chunk_lines.append(line)
                char_count += len(line) + 1  # +1 for newline
                i += 1
            
            # Create overlap for next chunk
            if i < len(lines):
                overlap_lines = min(chunk_overlap // 50, len(chunk_lines) // 2)
                i -= overlap_lines
            
            chunk_content = '\n'.join(chunk_lines)
            chunk_hash = hashlib.md5(chunk_content.encode()).hexdigest()
            
            chunk = CodeChunk(
                content=chunk_content,
                file_path=str(file_path.relative_to(self.project_root)),
                start_line=start_line,
                end_line=start_line + len(chunk_lines) - 1,
                chunk_hash=chunk_hash,
                language=file_path.suffix[1:] if file_path.suffix else "text",
                file_size=len(content),
                last_modified=file_path.stat().st_mtime
            )
            chunks.append(chunk)
        
        return chunks
    
    def index_file(self, file_path: Path):
        """Index a single file."""
        if not self._should_index_file(file_path):
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, PermissionError):
            return
        
        # Remove existing chunks for this file
        try:
            existing_ids = self.collection.get(
                where={"file_path": str(file_path.relative_to(self.project_root))}
            )["ids"]
            if existing_ids:
                self.collection.delete(ids=existing_ids)
        except Exception:
            pass
        
        # Create new chunks
        chunks = self._chunk_code(content, file_path)
        
        if not chunks:
            return
        
        # Generate embeddings
        embeddings = self.embedding_model.encode([chunk.content for chunk in chunks])
        
        # Store in vector database
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=[chunk.content for chunk in chunks],
            ids=[f"{chunk.file_path}:{chunk.start_line}:{chunk.chunk_hash}" for chunk in chunks],
            metadatas=[{
                "file_path": chunk.file_path,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "language": chunk.language,
                "file_size": chunk.file_size,
                "last_modified": chunk.last_modified,
                "chunk_hash": chunk.chunk_hash
            } for chunk in chunks]
        )
        
        print(f"✅ Indexed {len(chunks)} chunks from {file_path.name}")
    
    def index_codebase(self, force_reindex: bool = False):
        """Index the entire codebase."""
        print("🚀 Starting codebase indexing...")
        
        indexed_files = 0
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and self._should_index_file(file_path):
                self.index_file(file_path)
                indexed_files += 1
        
        # Update last index time
        self.config.setdefault("ai_usage_stats", {})["last_index_update"] = datetime.now().isoformat()
        self._save_config()
        
        print(f"🎉 Indexing complete! Processed {indexed_files} files.")
    
    def search_similar_code(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for code similar to the query."""
        query_embedding = self.embedding_model.encode([query])
        
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        similar_chunks = []
        for i in range(len(results["documents"][0])):
            similar_chunks.append({
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "similarity": 1 - results["distances"][0][i]  # Convert distance to similarity
            })
        
        return similar_chunks
    
    def get_file_structure(self) -> Dict[str, Any]:
        """Get project file structure."""
        structure = {}
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and self._should_index_file(file_path):
                rel_path = file_path.relative_to(self.project_root)
                parts = rel_path.parts
                current = structure
                
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                current[parts[-1]] = {
                    "size": file_path.stat().st_size,
                    "language": file_path.suffix[1:] if file_path.suffix else "text",
                    "last_modified": file_path.stat().st_mtime
                }
        
        return structure
    
    def update_usage_stats(self, tokens_used: int, cost: float = 0.0):
        """Update AI usage statistics."""
        stats = self.config.setdefault("ai_usage_stats", {})
        
        # Check if we need to reset monthly stats
        last_reset = stats.get("last_reset_date")
        if last_reset:
            last_reset_date = datetime.fromisoformat(last_reset)
            if datetime.now() - last_reset_date > timedelta(days=30):
                stats["monthly_requests"] = 0
                stats["monthly_tokens"] = 0
                stats["monthly_cost_usd"] = 0.0
                stats["last_reset_date"] = datetime.now().isoformat()
        else:
            stats["last_reset_date"] = datetime.now().isoformat()
        
        # Update stats
        stats["total_requests"] = stats.get("total_requests", 0) + 1
        stats["total_tokens"] = stats.get("total_tokens", 0) + tokens_used
        stats["total_cost_usd"] = stats.get("total_cost_usd", 0.0) + cost
        stats["monthly_requests"] = stats.get("monthly_requests", 0) + 1
        stats["monthly_tokens"] = stats.get("monthly_tokens", 0) + tokens_used
        stats["monthly_cost_usd"] = stats.get("monthly_cost_usd", 0.0) + cost
        
        self._save_config()
    
    def get_usage_stats(self) -> UsageStats:
        """Get current usage statistics."""
        stats_data = self.config.get("ai_usage_stats", {})
        return UsageStats(**stats_data)
    
    def cleanup(self):
        """Cleanup resources."""
        if self.observer:
            self.observer.stop()
            self.observer.join()


class CodebaseAnalysisAgent:
    """AI agent specialized in codebase analysis and comprehension."""
    
    def __init__(self, indexer: CodebaseIndexer):
        self.indexer = indexer
        self.config = indexer.config
        
        # Initialize AI model
        ai_config = self.config.get("ai_config", {})
        model_name = ai_config.get("chat_model", "gpt-4o-mini")
        provider = ai_config.get("chat_provider", "openai")
        
        if provider == "openai":
            self.model = OpenAIModel(model_name, api_key=settings.openai_api_key)
        elif provider == "openrouter":
            self.model = OpenAIModel(model_name, provider=OpenRouterProvider(api_key=settings.openrouter_api_key))
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
        
        # Create agent
        self.agent = Agent(
            self.model,
            deps_type=CodebaseAnalysisContext,
        )
        
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.tokenizer.encode(text))
    
    async def analyze_codebase(self, query: str, personality: str = "geek") -> str:
        """Analyze codebase and answer questions about it."""
        
        # Search for relevant code chunks
        relevant_chunks = self.indexer.search_similar_code(query, n_results=8)
        
        # Get file structure
        file_structure = self.indexer.get_file_structure()
        
        # Get project information
        project_info = {
            "name": "DotGript",
            "description": "AI-powered DevOps CLI tool",
            "languages": list(set([chunk["metadata"]["language"] for chunk in relevant_chunks])),
            "total_files": len([f for f in Path(self.indexer.project_root).rglob("*") if f.is_file()])
        }
        
        # Create context
        context = CodebaseAnalysisContext(
            query=query,
            relevant_chunks=relevant_chunks,
            file_structure=file_structure,
            project_info=project_info
        )
        
        @self.agent.instructions
        def analysis_instructions(ctx: RunContext[CodebaseAnalysisContext]) -> str:
            personality_prompts = {
                "geek": "You are a caffeinated code geek who gets excited about clean architecture and clever solutions. Use emojis and technical jargon.",
                "wizard": "You are an ancient code wizard who speaks in mystical terms about the arcane arts of programming.",
                "mom": "You are a caring coding mom who explains things gently and worries about code quality.",
                "hater": "You are a grumpy but brilliant code critic who roasts bad practices while providing perfect solutions.",
                "sexy": "You are a charming AI who flirts harmlessly while delivering solid technical insights.",
            }
            
            base_prompt = f"""You are an AI assistant specialized in analyzing codebases. {personality_prompts.get(personality, '')}

You have access to the following information about the codebase:

**Project Information:**
- Name: {ctx.deps.project_info.get('name', 'Unknown')}
- Description: {ctx.deps.project_info.get('description', 'Unknown')}
- Languages: {', '.join(ctx.deps.project_info.get('languages', []))}
- Total files: {ctx.deps.project_info.get('total_files', 0)}

**Relevant Code Chunks:**
"""
            
            for i, chunk in enumerate(ctx.deps.relevant_chunks[:5]):  # Limit to top 5
                metadata = chunk["metadata"]
                similarity = chunk["similarity"]
                base_prompt += f"""
### Chunk {i+1} (Similarity: {similarity:.2f})
**File:** {metadata['file_path']} (Lines {metadata['start_line']}-{metadata['end_line']})
**Language:** {metadata['language']}

```{metadata['language']}
{chunk['content'][:1000]}{'...' if len(chunk['content']) > 1000 else ''}
```
"""
            
            base_prompt += """

**Instructions:**
1. Analyze the provided code chunks that are most relevant to the user's query
2. Provide detailed, accurate answers based on the actual codebase
3. Reference specific files and line numbers when relevant
4. If you need more context, suggest specific files or areas to examine
5. Maintain your personality while being technically accurate
6. If the query cannot be fully answered with the provided context, clearly state this

**User Query:** {query}

Please provide a comprehensive analysis based on the codebase context provided above.
"""
            
            return base_prompt
        
        try:
            # Count tokens for usage tracking
            prompt_tokens = self._count_tokens(query + str(context.dict()))
            
            # Run analysis
            response = await self.agent.run(query, deps=context)
            
            # Count response tokens and update usage
            response_tokens = self._count_tokens(str(response))
            total_tokens = prompt_tokens + response_tokens
            
            # Estimate cost (rough estimate for OpenAI pricing)
            cost = (prompt_tokens * 0.00015 + response_tokens * 0.0006) / 1000
            
            self.indexer.update_usage_stats(total_tokens, cost)
            
            return str(response)
            
        except Exception as e:
            return f"❌ Error analyzing codebase: {str(e)}"
