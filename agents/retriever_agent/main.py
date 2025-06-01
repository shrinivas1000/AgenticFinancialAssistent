from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Retriever Agent Service", description="Document retrieval and search service")

class Document(BaseModel):
    ticker: str
    title: str
    summary: str

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3
    min_score: float = 0.3
    filter_ticker: Optional[str] = None

class AddDocumentsRequest(BaseModel):
    documents: List[Document]

class RetrieverAgent:
    def __init__(self):
        self.model = SentenceTransformer('all-mpnet-base-v2')
        self.index = None
        self.documents = []
    
    def add_documents(self, docs):
       
        existing_titles = {doc.get('title', '') for doc in self.documents}
        
        new_docs = []
        for doc in docs:
            if doc.get('title', '') not in existing_titles:
                new_docs.append(doc)
        
        if not new_docs:
            return 
        
        self.documents.extend(new_docs)
        texts = [f"Company: {doc['ticker']} | News: {doc['title']} | Details: {doc['summary']}" for doc in new_docs]
        embeddings = self.model.encode(texts)
        
        if self.index is None:
            self.index = faiss.IndexFlatIP(embeddings.shape[1])
        
        self.index.add(embeddings.astype('float32'))

    
    def search(self, query, top_k=3, min_score=0.3, filter_ticker=None):
        if self.index is None:
            return []
        
        query_embedding = self.model.encode([query])
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for i, score in zip(indices[0], scores[0]):
            if i < len(self.documents) and score >= min_score:
                doc = self.documents[i].copy()
                doc['score'] = float(score)
                results.append(doc)
        
        if filter_ticker:
            results = [r for r in results if r['ticker'] == filter_ticker]
        
        return results
    
    def get_all_documents(self):
        return self.documents
    
    def clear_documents(self):
        self.documents = []
        self.index = None

retriever = RetrieverAgent()

@app.get("/")
def root():
    return {"message": "Retriever Agent Service is running"}

@app.post("/search")
def search_documents(request: SearchRequest):
    try:
        results = retriever.search(
            query=request.query,
            top_k=request.top_k,
            min_score=request.min_score,
            filter_ticker=request.filter_ticker
        )
        return {
            "query": request.query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents")
def add_documents(request: AddDocumentsRequest):
    try:
        docs = [doc.dict() for doc in request.documents]
        retriever.add_documents(docs)
        return {
            "message": f"Added {len(docs)} documents",
            "total_documents": len(retriever.documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
def get_all_documents():
    try:
        docs = retriever.get_all_documents()
        return {
            "documents": docs,
            "count": len(docs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents")
def clear_all_documents():
    try:
        retriever.clear_documents()
        return {"message": "All documents cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "total_documents": len(retriever.documents),
        "index_ready": retriever.index is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)