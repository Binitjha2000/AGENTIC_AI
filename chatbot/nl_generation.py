from transformers import pipeline, AutoTokenizer
import logging
import re
from typing import List, Dict

class ResponseGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model_name = "google/flan-t5-large"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-large",
            device=-1,  # CPU
            truncation=True,
            do_sample=True,  # Required for temperature
            max_new_tokens=800,
            temperature=0.4,
            model_kwargs={
            "cache_dir": "./model_cache",
        }
        )
        
    def _chunk_text(self, text: str, max_tokens: int = 400) -> List[str]:
        """Split text into model-safe chunks"""
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        return [self.tokenizer.decode(tokens[i:i+max_tokens]) 
                for i in range(0, len(tokens), max_tokens)]
# {context[:4000]}
    def enhance_rag_response(self, query: str, rag_results: List[Dict]) -> str:
        try:
            # Filter and format context
            context = "\n".join(
                f"[Document {i+1}]: {self._clean_content(res['content'])}"
                for i, res in enumerate(self._filter_results(rag_results, query))
            )
        
            prompt = f"""Generate precise response using these documents:

            USER QUERY: {query}

            RELEVANT DOCUMENTS:
            {context}

            RESPONSE REQUIREMENTS:
            1. Strictly use information from provided documents
            2. Acknowledge when info is unavailable
            3. Format with headers, bullets, and code blocks
            4. Reference sources like [1], [2]
            5. Never invent technical details

            TECHNICAL RESPONSE:"""
        
            response = self.generator(
                prompt,
                max_new_tokens=800,
                temperature=0.4,  # Reduced for less randomness
                do_sample=True,
                num_beams=4,
                repetition_penalty=1.2,  # Reduce repetition
                no_repeat_ngram_size=3
            )[0]['generated_text']
        
            return self._format_response(response)

        except Exception as e:
            self.logger.error(f"Generation error: {str(e)}")
            return "I need to verify the documentation. Could you please rephrase your question?"

    def _clean_content(self, text: str) -> str:
        """Remove code comments and special characters - NO TRUNCATION NOW"""
        return re.sub(r'\/\/.*?\n', '', text).strip()

    def _filter_results(self, results: List[Dict], query: str) -> List[Dict]:
        """Filter RAG results by query relevance"""
        keywords = set(query.lower().split())
        return sorted(
            results,
            key=lambda x: sum(1 for kw in keywords if kw in x['content'].lower()),
            reverse=True
        )[:2]  # Use top 2 most relevant

    def _format_response(self, text: str) -> str:
        """Clean and structure generated text"""
        # Remove special tokens
        text = re.sub(r'<\/?s>', '', text)
    
        # Improve markdown formatting
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'(##+)(\w)', r'\1 \2', text)
        text = re.sub(r'```(.*?)```', r'\n```\n\1\n```\n', text, flags=re.DOTALL)
    
        # Remove redundant newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
    
        return text.strip()[:2000]

    def humanize(self, technical_text: str) -> str:
        chunks = self._chunk_text(technical_text)
        response = []
        for chunk in chunks:
            result = self.generator(
                f"Simplify this technical message: {chunk}",
                max_new_tokens=150
            )
            response.append(result[0]['generated_text'])
        return self._format_response(" ".join(response))