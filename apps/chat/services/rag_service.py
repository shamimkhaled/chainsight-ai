import openai
from django.conf import settings
import logging
from typing import List, Dict, Any
import tiktoken

logger = logging.getLogger(__name__)


class RAGChatService:
    """
    Retrieval-Augmented Generation (RAG) service for contract chat
    """
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.embedding_model = 'text-embedding-ada-002'
        
    def query_contracts(
        self,
        query: str,
        contract_ids: List[str],
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Query contracts using RAG
        
        Args:
            query: User's question
            contract_ids: List of contract IDs to search
            chat_history: Previous messages for context
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            # Step 1: Retrieve relevant context from vector database
            relevant_chunks = self._retrieve_relevant_chunks(query, contract_ids)
            
            # Step 2: Build context from retrieved chunks
            context = self._build_context(relevant_chunks)
            
            # Step 3: Generate answer using GPT-4
            answer, tokens_used = self._generate_answer(
                query, context, chat_history
            )
            
            # Step 4: Extract sources
            sources = self._extract_sources(relevant_chunks)
            
            return {
                'answer': answer,
                'sources': sources,
                'context_used': context,
                'tokens_used': tokens_used,
                'relevant_chunks_count': len(relevant_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error in RAG query: {str(e)}")
            raise
    
    def _retrieve_relevant_chunks(
        self,
        query: str,
        contract_ids: List[str],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks using vector similarity
        
        In production, this would:
        1. Generate embedding for query
        2. Search Pinecone vector database
        3. Filter by contract_ids
        4. Return top_k most similar chunks
        """
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # TODO: Query Pinecone vector database
            # For now, return mock relevant chunks
            relevant_chunks = []
            
            from apps.contracts.models import Contract
            
            # Get contracts
            contracts = Contract.objects.filter(id__in=contract_ids)
            
            for contract in contracts:
                # Get clauses related to query (simplified)
                clauses = contract.clauses.all()[:top_k]
                
                for clause in clauses:
                    relevant_chunks.append({
                        'contract_id': str(contract.id),
                        'contract_filename': contract.original_filename,
                        'clause_id': str(clause.id),
                        'clause_type': clause.clause_type,
                        'clause_title': clause.title,
                        'content': clause.content,
                        'page_number': clause.page_number,
                        'similarity_score': 0.85  # Mock score
                    })
            
            return relevant_chunks[:top_k]
            
        except Exception as e:
            logger.error(f"Error retrieving chunks: {str(e)}")
            return []
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI
        """
        try:
            response = openai.Embedding.create(
                model=self.embedding_model,
                input=text
            )
            return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return []
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Build context string from retrieved chunks
        """
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}] Contract: {chunk['contract_filename']}\n"
                f"Clause Type: {chunk['clause_type']}\n"
                f"Page: {chunk.get('page_number', 'N/A')}\n"
                f"Content: {chunk['content']}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def _generate_answer(
        self,
        query: str,
        context: str,
        chat_history: List[Dict[str, str]] = None
    ) -> tuple[str, int]:
        """
        Generate answer using GPT-4 with context
        
        Returns:
            Tuple of (answer, tokens_used)
        """
        try:
            # Build messages
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a legal contract analysis expert. "
                        "Answer questions about contracts based on the provided context. "
                        "Always cite your sources by referencing [Source N]. "
                        "If the answer is not in the context, say so clearly. "
                        "Be precise, professional, and helpful."
                    )
                }
            ]
            
            # Add chat history if provided
            if chat_history:
                messages.extend(chat_history[-5:])  # Last 5 messages
            
            # Add current query with context
            messages.append({
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            })
            
            # Call GPT-4
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for factual answers
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return answer, tokens_used
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return "I apologize, but I encountered an error processing your question.", 0
    
    def _extract_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract source references from chunks
        """
        sources = []
        
        for chunk in chunks:
            sources.append({
                'contract_id': chunk['contract_id'],
                'contract_filename': chunk['contract_filename'],
                'clause_id': chunk.get('clause_id'),
                'clause_type': chunk.get('clause_type'),
                'clause_title': chunk.get('clause_title'),
                'page_number': chunk.get('page_number'),
                'similarity_score': chunk.get('similarity_score')
            })
        
        return sources
    
    def create_embeddings_for_contract(self, contract_id: str):
        """
        Create vector embeddings for a contract's content
        
        This would be called after contract analysis is complete.
        Chunks the contract text and stores embeddings in Pinecone.
        """
        try:
            from apps.contracts.models import Contract
            
            contract = Contract.objects.get(id=contract_id)
            
            # Get all clauses
            clauses = contract.clauses.all()
            
            embeddings_created = []
            
            for clause in clauses:
                # Generate embedding for clause content
                embedding = self._generate_embedding(clause.content)
                
                if embedding:
                    # TODO: Store in Pinecone
                    vector_id = f"{contract_id}_{clause.id}"
                    
                    # Store reference in database
                    from apps.chat.models import ContractEmbedding
                    
                    embedding_obj = ContractEmbedding.objects.create(
                        contract=contract,
                        chunk_text=clause.content,
                        chunk_index=clause.clause_number,
                        vector_id=vector_id,
                        clause_type=clause.clause_type,
                        page_number=clause.page_number,
                        embedding_model=self.embedding_model
                    )
                    
                    embeddings_created.append(embedding_obj)
            
            logger.info(
                f"Created {len(embeddings_created)} embeddings for contract {contract_id}"
            )
            
            return embeddings_created
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            return []

