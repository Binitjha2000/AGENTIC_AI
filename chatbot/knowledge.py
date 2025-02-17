import os
import logging
from typing import List, Dict
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

class KnowledgeBase:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.db = self._init_vector_store()
        self.logger = logging.getLogger(__name__)

    def _init_vector_store(self):
        """Initialize vector store with enhanced metadata"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=300,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        loaders = {
            '.pdf': PyPDFLoader,
            '.txt': TextLoader,
            '.docx': Docx2txtLoader
        }

        try:
            loader = DirectoryLoader(
                './knowledge_docs',
                glob="**/*.*",
                loader_cls=lambda path: loaders.get(os.path.splitext(path)[1], TextLoader)(path),
                show_progress=True
            )
            docs = loader.load()
            splits = text_splitter.split_documents(docs)
            
            # Add page numbers to metadata
            for doc in splits:
                doc.metadata.setdefault('page', 'N/A')
                
            return FAISS.from_documents(splits, self.embeddings)
            
        except Exception as e:
            self.logger.error(f"Vector store init failed: {str(e)}")
            return FAISS.from_texts(["Error loading documents"], self.embeddings)

    def search(self, query: str, k=5) -> List[Dict]:
        """Return structured search results with metadata"""
        try:
            docs = self.db.similarity_search(query, k=k)
            return [{
                "source": os.path.basename(d.metadata['source']),
                "content": d.page_content[:700].strip(),
                "page": d.metadata.get('page', 'N/A'),
                "score": float(d.metadata.get('score', 0))
            } for d in docs]
            
        except Exception as e:
            self.logger.error(f"Search error: {str(e)}")
            return []
        

        #     def search(self, query: str, k=5) -> List[Dict]:
        # """Return structured search results with metadata"""
        # try:
        #     docs = self.db.similarity_search(query, k=k)
        #     results = [{
        #         "source": os.path.basename(d.metadata['source']),
        #         "content": d.page_content[:700].strip(),  # Keep content snippet for logging
        #         "page": d.metadata.get('page', 'N/A'),
        #         "score": float(d.metadata.get('score', 0))
        #     } for d in docs]
        #     self.logger.info(f"Search results for query '{query}':\n{results}") # Added logging here
        #     return results

        # except Exception as e:
        #     self.logger.error(f"Search error: {str(e)}")
        #     return []