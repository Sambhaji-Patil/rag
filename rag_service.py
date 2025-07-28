import time
import uuid
import asyncio
from datetime import datetime
from typing import List, Tuple, Dict, Any

from document_processor import extract_text_from_pdf, chunk_text
from embeddings import gemini_embed_async
from vector_store import store_chunks_async, retrieve_chunks
from llm import query_gpt4_async
from cache import is_document_processed, mark_document_processed, save_timing_logs
from config import Config

class RAGService:
    """Main RAG service class"""
    
    async def process_request(self, document_url: str, questions: List[str]) -> Tuple[List[str], str]:
        """
        Process a RAG request with document URL and questions
        Returns: (answers, log_filepath)
        """
        start_time = time.time()
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        print(f"Processing request ID: {request_id}")
        
        # Initialize timing data structure
        timing_data = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "document_url": document_url,
            "num_questions": len(questions),
            "questions": questions,
            "timings": {}
        }

        # Check if document was already processed
        if is_document_processed(document_url):
            print(f"📋 Document already processed, skipping PDF processing, chunking, embedding, and storage")
            timing_data["timings"]["pdf_processing"] = 0.0
            timing_data["timings"]["chunking"] = 0.0
            timing_data["timings"]["embedding"] = 0.0
            timing_data["timings"]["vector_storage"] = 0.0
            timing_data["embedding_stats"] = {
                "total_chunks": "cached",
                "successful_embeddings": "cached", 
                "failed_embeddings": 0,
                "success_rate": "100.0% (cached)"
            }
            chunks = []  # Will skip to Q&A processing
        else:
            try:
                # 1. PDF Processing
                pdf_start = time.time()
                pages = extract_text_from_pdf(document_url)
                pdf_time = time.time() - pdf_start
                timing_data["timings"]["pdf_processing"] = pdf_time
                print(f"1. PDF Processing: {pdf_time:.2f} seconds")

                # 2. Chunking
                chunk_start = time.time()
                chunks = chunk_text(pages, Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
                chunk_time = time.time() - chunk_start
                timing_data["timings"]["chunking"] = chunk_time
                timing_data["num_chunks"] = len(chunks)
                print(f"2. Chunking: {chunk_time:.2f} seconds")

                if not chunks:
                    raise ValueError("No text chunks were generated from the document")

                # 3. Embedding (with async batch processing and caching)
                embed_start = time.time()
                embeddings = await gemini_embed_async(chunks, batch_size=Config.BATCH_SIZE)
                embed_time = time.time() - embed_start
                timing_data["timings"]["embedding"] = embed_time
                
                # Add embedding success rate to timing data
                successful_embeddings = sum(1 for emb in embeddings if emb is not None)
                failed_embeddings = len(embeddings) - successful_embeddings
                timing_data["embedding_stats"] = {
                    "total_chunks": len(chunks),
                    "successful_embeddings": successful_embeddings,
                    "failed_embeddings": failed_embeddings,
                    "success_rate": f"{(successful_embeddings/len(chunks))*100:.1f}%"
                }
                print(f"3. Embedding: {embed_time:.2f} seconds ({successful_embeddings}/{len(chunks)} chunks successful)")

                # 4. Vector Storage (async batched with parallel uploads)
                storage_start = time.time()
                await store_chunks_async(chunks, embeddings)
                storage_time = time.time() - storage_start
                timing_data["timings"]["vector_storage"] = storage_time
                print(f"4. Vector Storage: {storage_time:.2f} seconds")
                
                # Mark document as processed
                mark_document_processed(document_url, len(chunks))
                
            except Exception as e:
                print(f"Error processing document: {str(e)}")
                raise ValueError(f"Failed to process document: {str(e)}")

        # Process all questions in parallel for retrieval and answer generation
        qa_start = time.time()
        results = await asyncio.gather(*[self._process_question(q) for q in questions])
        qa_total_time = time.time() - qa_start
        
        final_answers = [result[0] for result in results]
        individual_retrieval_times = [result[1] for result in results]
        individual_answer_times = [result[2] for result in results]

        # Store timing data correctly
        timing_data["timings"]["retrieval_individual_sum"] = sum(individual_retrieval_times)
        timing_data["timings"]["answer_generation_individual_sum"] = sum(individual_answer_times)
        timing_data["timings"]["qa_actual_parallel_time"] = qa_total_time
        timing_data["timings"]["retrieval_per_question"] = individual_retrieval_times
        timing_data["timings"]["answer_generation_per_question"] = individual_answer_times

        print(f"5. Retrieval (parallel actual time): {qa_total_time:.2f} seconds")
        print(f"   - Individual times sum: {sum(individual_retrieval_times):.2f}s (if sequential)")
        print(f"6. Answer Generation (parallel actual time): included in above")
        print(f"   - Individual times sum: {sum(individual_answer_times):.2f}s (if sequential)")
        
        total_time = time.time() - start_time
        timing_data["timings"]["total_time"] = total_time
        timing_data["answers"] = final_answers
        
        print(f"TOTAL TIME: {total_time:.2f} seconds")

        # Save timing logs to file
        log_filepath = save_timing_logs(request_id, timing_data)
        
        return final_answers, log_filepath

    async def _process_question(self, question: str) -> Tuple[str, float, float]:
        """Process a single question and return answer with timing info"""
        # 5. Retrieval
        retrieval_start = time.time()
        q_embedding = await gemini_embed_async([question])
        q_embedding = q_embedding[0]
        candidate_chunks = retrieve_chunks(q_embedding)
        retrieval_time = time.time() - retrieval_start

        # 6. Answer Generation
        answer_start = time.time()
        context = "\n---\n".join(candidate_chunks)
        prompt = f"Use the following context to answer the question:\n{context}\n\nQ: {question}\nA:"
        answer = await query_gpt4_async(prompt)
        answer_time = time.time() - answer_start
        
        return answer.strip(), retrieval_time, answer_time
