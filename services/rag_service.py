import os
import json
import chromadb
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RAGService:
    def __init__(self):
        """Initialize RAG service with ChromaDB and OpenAI client."""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.chroma = chromadb.Client()
        self.collection_name = "plant_knowledge_base"
        self.collection = None
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Initialize or get existing ChromaDB collection."""
        try:
            # Check if collection exists
            existing_collections = [c.name for c in self.chroma.list_collections()]
            
            if self.collection_name in existing_collections:
                print(f"✅ Using existing collection: {self.collection_name}")
                self.collection = self.chroma.get_collection(self.collection_name)
            else:
                print("🆕 Creating new collection and embedding data...")
                self.collection = self.chroma.create_collection(self.collection_name)
                self._populate_collection()
                
        except Exception as e:
            print(f"Error initializing collection: {str(e)}")
            raise
    
    def _load_rag_data(self) -> List[Dict[str, Any]]:
        """Load RAG data from JSON file."""
        try:
            with open('data/RAG_v1.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading RAG data: {str(e)}")
            return []
    
    def _populate_collection(self):
        """Populate the collection with plant data from JSON."""
        data = self._load_rag_data()
        
        if not data:
            print("No data found to populate collection")
            return
        
        print(f"Embedding {len(data)} plant records...")
        
        for item in data:
            try:
                # Create comprehensive text for embedding
                text_to_embed = self._create_embedding_text(item)
                
                # Generate embedding using OpenAI
                embedding = self.client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text_to_embed
                ).data[0].embedding
                
                # Add to collection
                self.collection.add(
                    ids=[item["id"]],
                    embeddings=[embedding],
                    metadatas=[{
                        "name": item["name"],
                        "type": "crop",
                        "description": item["description"][:200] + "..." if len(item["description"]) > 200 else item["description"]
                    }],
                    documents=[text_to_embed]
                )
                
            except Exception as e:
                print(f"Error processing item {item.get('id', 'unknown')}: {str(e)}")
                continue
        
        print("✅ Data embedded and added to vector database.")
    
    def _create_embedding_text(self, item: Dict[str, Any]) -> str:
        """Create comprehensive text for embedding from plant data."""
        text_parts = [
            f"Plant: {item['name']}",
            f"Description: {item['description']}"
        ]
        
        # Add planting instructions
        if item.get('how_to_plant'):
            text_parts.append(f"Planting instructions: {' '.join(item['how_to_plant'])}")
        
        # Add common diseases
        if item.get('common_diseases'):
            text_parts.append(f"Common diseases: {', '.join(item['common_diseases'])}")
        
        # Add causes
        if item.get('causes'):
            text_parts.append(f"Causes: {' '.join(item['causes'])}")
        
        # Add treatments
        if item.get('treatments'):
            text_parts.append(f"Treatments: {' '.join(item['treatments'])}")
        
        # Add benefits
        if item.get('benefits'):
            text_parts.append(f"Benefits: {' '.join(item['benefits'])}")
        
        return " ".join(text_parts)
    
    def search_relevant_context(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search for relevant plant information using semantic similarity.
        
        Args:
            query: The search query
            n_results: Number of results to return
            
        Returns:
            List of relevant plant information
        """
        try:
            if not self.collection:
                print("Collection not initialized")
                return []
            
            # Generate embedding for the query
            query_embedding = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            ).data[0].embedding
            
            # Search the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results["metadatas"] and results["metadatas"][0]:
                for i, metadata in enumerate(results["metadatas"][0]):
                    formatted_results.append({
                        "name": metadata.get("name", "Unknown"),
                        "description": metadata.get("description", ""),
                        "document": results["documents"][0][i] if results["documents"] and results["documents"][0] else "",
                        "distance": results["distances"][0][i] if results["distances"] and results["distances"][0] else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching context: {str(e)}")
            return []
    
    def get_context_for_diagnosis(self, plant_name: Optional[str] = None, symptoms: Optional[str] = None) -> str:
        """
        Get relevant context for plant diagnosis.
        
        Args:
            plant_name: Optional plant name to search for
            symptoms: Optional symptoms description
            
        Returns:
            Formatted context string
        """
        query_parts = []
        if plant_name:
            query_parts.append(plant_name)
        if symptoms:
            query_parts.append(symptoms)
        
        if not query_parts:
            return ""
        
        query = " ".join(query_parts)
        results = self.search_relevant_context(query, n_results=2)
        
        if not results:
            return ""
        
        context_parts = ["Relevant plant information from local database:"]
        for result in results:
            context_parts.append(f"\n- {result['name']}: {result['description']}")
            if result['document']:
                # Extract key information from the document
                doc_parts = result['document'].split('. ')
                key_info = '. '.join(doc_parts[:3])  # Take first 3 sentences
                context_parts.append(f"  Key details: {key_info}")
        
        return "\n".join(context_parts)
    
    def get_context_for_chat(self, user_message: str) -> str:
        """
        Get relevant context for chat conversations.
        
        Args:
            user_message: User's message
            
        Returns:
            Formatted context string
        """
        results = self.search_relevant_context(user_message, n_results=2)
        
        if not results:
            return ""
        
        context_parts = ["Relevant information from local plant database:"]
        for result in results:
            context_parts.append(f"\n- {result['name']}: {result['description']}")
        
        return "\n".join(context_parts)
    
    def get_plant_specific_info(self, plant_name: str) -> Optional[Dict[str, Any]]:
        """
        Get specific information about a plant by name.
        
        Args:
            plant_name: Name of the plant
            
        Returns:
            Plant information dictionary or None
        """
        try:
            # Search for exact plant name
            results = self.search_relevant_context(plant_name, n_results=5)
            
            # Find exact match
            for result in results:
                if result['name'].lower() == plant_name.lower():
                    # Load full data from JSON
                    data = self._load_rag_data()
                    for item in data:
                        if item['name'].lower() == plant_name.lower():
                            return item
            
            return None
            
        except Exception as e:
            print(f"Error getting plant info: {str(e)}")
            return None
