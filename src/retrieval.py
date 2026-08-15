from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from data.brand_data import brand_descriptions

def build_vector_store():
    docs = [Document(page_content=desc) for desc in brand_descriptions]
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(
        docs, 
        embeddings, 
        persist_directory="./chroma_db"
    )
    return vectorstore

def retrieve_similar(query, k=3):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    results = vectorstore.similarity_search(query, k=k)
    return [doc.page_content for doc in results]

if __name__ == "__main__":
    build_vector_store()
    print("Vector store built.\n")
    
    test_query = "serum for redness and pores"
    results = retrieve_similar(test_query)
    print(f"Query: {test_query}\n")
    print("Top matches:")
    for r in results:
        print(f"- {r}")