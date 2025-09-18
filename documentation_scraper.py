"""Web scraper for Jira help documentation."""

import requests
import os
import json
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from config import config

# Optional imports with fallback
try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False
    print("⚠️  BeautifulSoup not available - documentation scraping will be limited")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️  SentenceTransformers not available - vector search will be disabled")

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️  ChromaDB not available - vector database will be disabled")

@dataclass
class DocumentationPage:
    """Represents a documentation page."""
    url: str
    title: str
    content: str
    sections: List[Dict[str, str]]

class DocumentationScraper:
    """Scraper for Jira help documentation."""
    
    def __init__(self):
        self.base_url = config.JIRA_DOCS_URL
        self.cache_dir = config.CACHE_PATH
        self.model = None
        self.chroma_client = None
        self.collection = None
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize model if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"⚠️  Could not load sentence transformer model: {e}")
        
        # Initialize vector database
        self._init_vector_db()
    
    def _init_vector_db(self):
        """Initialize ChromaDB for vector storage."""
        if not CHROMADB_AVAILABLE:
            print("⚠️  ChromaDB not available - vector database disabled")
            return
            
        try:
            self.chroma_client = chromadb.PersistentClient(path=config.VECTOR_DB_PATH)
            self.collection = self.chroma_client.get_or_create_collection(
                name="jira_docs",
                metadata={"description": "Jira Software Cloud documentation"}
            )
        except Exception as e:
            print(f"Warning: Could not initialize vector database: {e}")
            self.chroma_client = None
            self.collection = None
    
    def _get_cache_path(self, url: str) -> str:
        """Get cache file path for a URL."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{url_hash}.json")
    
    def _load_from_cache(self, url: str) -> Optional[Dict[str, Any]]:
        """Load page content from cache."""
        if not config.CACHE_DOCS:
            return None
        
        cache_path = self._get_cache_path(url)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache for {url}: {e}")
        return None
    
    def _save_to_cache(self, url: str, data: Dict[str, Any]):
        """Save page content to cache."""
        if not config.CACHE_DOCS:
            return
        
        cache_path = self._get_cache_path(url)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache for {url}: {e}")
    
    def _extract_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract structured content from BeautifulSoup object."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get page title
        title = ""
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text().strip()
        
        # Get main content
        content = ""
        sections = []
        
        # Try to find main content areas
        main_content = soup.find("main") or soup.find("article") or soup.find("div", class_="content")
        
        if main_content:
            # Extract sections
            headings = main_content.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            current_section = {"title": "", "content": "", "level": 0}
            
            for element in main_content.find_all():
                if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    # Save previous section if it has content
                    if current_section["content"].strip():
                        sections.append(current_section.copy())
                    
                    # Start new section
                    current_section = {
                        "title": element.get_text().strip(),
                        "content": "",
                        "level": int(element.name[1])
                    }
                else:
                    # Add content to current section
                    text = element.get_text().strip()
                    if text:
                        current_section["content"] += text + " "
            
            # Add final section
            if current_section["content"].strip():
                sections.append(current_section)
            
            # Combine all content
            content = " ".join([section["content"] for section in sections])
        
        return {
            "title": title,
            "content": content.strip(),
            "sections": sections
        }
    
    def scrape_page(self, url: str) -> Optional[DocumentationPage]:
        """Scrape a single documentation page."""
        if not BEAUTIFULSOUP_AVAILABLE:
            print("⚠️  BeautifulSoup not available - cannot scrape documentation")
            return None
            
        # Check cache first
        cached_data = self._load_from_cache(url)
        if cached_data:
            return DocumentationPage(
                url=url,
                title=cached_data["title"],
                content=cached_data["content"],
                sections=cached_data["sections"]
            )
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            extracted = self._extract_content(soup)
            
            # Save to cache
            self._save_to_cache(url, extracted)
            
            return DocumentationPage(
                url=url,
                title=extracted["title"],
                content=extracted["content"],
                sections=extracted["sections"]
            )
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def discover_documentation_pages(self) -> List[str]:
        """Discover documentation pages from the main resources page."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(self.base_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            # Find all links that point to Jira documentation
            for link in soup.find_all("a", href=True):
                href = link["href"]
                
                # Convert relative URLs to absolute
                if href.startswith("/"):
                    href = "https://support.atlassian.com" + href
                elif href.startswith("http"):
                    # Only include Atlassian support links
                    if "support.atlassian.com" in href and "jira-software-cloud" in href:
                        links.append(href)
            
            return list(set(links))  # Remove duplicates
            
        except Exception as e:
            print(f"Error discovering documentation pages: {e}")
            return []
    
    def scrape_all_documentation(self) -> List[DocumentationPage]:
        """Scrape all available documentation pages."""
        pages = []
        urls = self.discover_documentation_pages()
        
        print(f"Found {len(urls)} documentation pages to scrape")
        
        for i, url in enumerate(urls):
            print(f"Scraping {i+1}/{len(urls)}: {url}")
            page = self.scrape_page(url)
            if page:
                pages.append(page)
        
        return pages
    
    def add_to_vector_db(self, page: DocumentationPage):
        """Add a documentation page to the vector database."""
        if not self.collection:
            return
        
        try:
            # Split content into chunks
            chunks = self._chunk_text(page.content, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
            
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    # Generate embedding
                    embedding = self.model.encode(chunk).tolist()
                    
                    # Create document ID
                    doc_id = f"{hashlib.md5(page.url.encode()).hexdigest()}_{i}"
                    
                    # Add to collection
                    self.collection.add(
                        documents=[chunk],
                        embeddings=[embedding],
                        metadatas=[{
                            "url": page.url,
                            "title": page.title,
                            "chunk_index": i,
                            "total_chunks": len(chunks)
                        }],
                        ids=[doc_id]
                    )
            
        except Exception as e:
            print(f"Error adding page to vector database: {e}")
    
    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def search_documentation(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search documentation using vector similarity."""
        if not self.collection:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode(query).tolist()
            
            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            
            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if results["distances"] else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching documentation: {e}")
            return []
    
    def populate_vector_db(self):
        """Populate the vector database with all documentation."""
        print("Discovering and scraping documentation...")
        pages = self.scrape_all_documentation()
        
        print(f"Adding {len(pages)} pages to vector database...")
        for page in pages:
            self.add_to_vector_db(page)
        
        print("Vector database populated successfully!")

class DocumentationManager:
    """Manager class for handling documentation operations."""
    
    def __init__(self):
        self.scraper = DocumentationScraper()
    
    def search(self, query: str) -> Dict[str, Any]:
        """Search documentation and return formatted results."""
        results = self.scraper.search_documentation(query)
        
        if results:
            return {
                "source": "documentation",
                "results": results,
                "message": f"Found {len(results)} relevant documentation sections"
            }
        else:
            return {
                "source": "documentation_error",
                "error": "No relevant documentation found",
                "message": "No documentation matches your query"
            }
    
    def get_epic_documentation(self) -> Dict[str, Any]:
        """Get documentation specifically about epics."""
        query = "epic create manage track issues"
        return self.search(query)
    
    def get_sprint_documentation(self) -> Dict[str, Any]:
        """Get documentation specifically about sprints."""
        query = "sprint create manage track agile scrum"
        return self.search(query)
    
    def initialize_documentation(self):
        """Initialize documentation by populating the vector database."""
        try:
            self.scraper.populate_vector_db()
            return True
        except Exception as e:
            print(f"Error initializing documentation: {e}")
            return False
