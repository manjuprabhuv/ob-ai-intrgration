import os
import json
from dotenv import load_dotenv
import chromadb
from openai import OpenAI
from chromadb.utils import embedding_functions
import streamlit as st


def load_product_data(data_dir: str = "../../data-puller/data/Bendigo Bank") -> list[dict]:
    """Load JSON product data from Bendigo Bank directory.

    - Reads .json files from the specified Bendigo Bank directory
    - Ignores 'Bendigo Bank_products.json' file
    - If a file contains a list of objects, each dict is appended
    - If a file contains a single dict, it's appended
    """
    data_dir = os.path.abspath(data_dir)
    products: list[dict] = []

    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    for fname in os.listdir(data_dir):
        if not fname.lower().endswith(".json") or fname == "Bendigo Bank_products.json":
            continue
        path = os.path.join(data_dir, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            if isinstance(payload, list):
                for item in payload:
                    if isinstance(item, dict):
                        products.append(item)
            elif isinstance(payload, dict):
                products.append(payload)
            # ignore other JSON types
        except Exception:
            # skip files that can't be read/parsed
            continue

    return products

# # function to split text into chunks
# def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 20) -> list[str]:
#     """Split text into chunks of specified size with overlap."""
#     chunks = []
#     start = 0
#     text_length = len(text)

#     while start < text_length:
#         end = min(start + chunk_size, text_length)
#         chunk = text[start:end]
#         chunks.append(chunk)
#         start += chunk_size - overlap  # move start forward with overlap

#     return chunks

def chunk_product_data(product_data: dict[str, any], chunk_size: int = 1000) -> list[dict[str, any]]:
    """
    Chunks a product JSON file into meaningful segments while preserving context.
    """
    chunks = []
    data = product_data.get("data", {})
    
    # Base metadata that will be included in all chunks
    base_metadata = {
        "productId": data.get("productId", ""),
        "productName": data.get("name", ""),
        "brandName": data.get("brandName", ""),
        "productCategory": data.get("productCategory", ""),
        "lastUpdated": data.get("lastUpdated", "")
    }
    
    # Basic Information chunk
    chunks.append({
        **base_metadata,
        "chunk_type": "basic_info",
        "content": json.dumps({
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "productCategory": data.get("productCategory", ""),
            "brandName": data.get("brandName", ""),
            "applicationUri": data.get("applicationUri", "")
        }),
        "chunk_index": len(chunks)
    })
    
    # Features chunk
    if features := data.get("features", []):
        chunks.append({
            **base_metadata,
            "chunk_type": "features",
            "content": json.dumps(features),
            "chunk_index": len(chunks)
        })
    
    # Eligibility chunk
    if eligibility := data.get("eligibility", []):
        chunks.append({
            **base_metadata,
            "chunk_type": "eligibility",
            "content": json.dumps(eligibility),
            "chunk_index": len(chunks)
        })
    
    # Fees chunks
    if fees := data.get("fees", []):
        fee_chunks = [fees[i:i + 3] for i in range(0, len(fees), 3)]
        for i, fee_chunk in enumerate(fee_chunks):
            chunks.append({
                **base_metadata,
                "chunk_type": "fees",
                "content": json.dumps(fee_chunk),
                "chunk_index": len(chunks),
                "sub_chunk": i + 1,
                "total_fee_chunks": len(fee_chunks)
            })
    
    # Deposit Rates chunk
    if deposit_rates := data.get("depositRates", []):
        chunks.append({
            **base_metadata,
            "chunk_type": "deposit_rates",
            "content": json.dumps(deposit_rates),
            "chunk_index": len(chunks)
        })
    
    # Lending Rates chunk
    if lending_rates := data.get("lendingRates", []):
        chunks.append({
            **base_metadata,
            "chunk_type": "lending_rates",
            "content": json.dumps(lending_rates),
            "chunk_index": len(chunks)
        })
    
    # Additional Information chunk
    if additional_info := data.get("additionalInformation", {}):
        chunks.append({
            **base_metadata,
            "chunk_type": "additional_info",
            "content": json.dumps(additional_info),
            "chunk_index": len(chunks)
        })
    
    return chunks   

# Function to generate embeddings using OpenAI API
def get_openai_embedding(text, client):
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    embedding = response.data[0].embedding
    return embedding

def query_documents(question, n_results=2,collection=None):
    # query_embedding = get_openai_embedding(question)
    results = collection.query(query_texts=question, n_results=n_results)

    # Extract the relevant chunks
    relevant_chunks = [doc for sublist in results["documents"] for doc in sublist]
    return relevant_chunks
    # for idx, document in enumerate(results["documents"][0]):
    #     doc_id = results["ids"][0][idx]
    #     distance = results["distances"][0][idx]
    #     print(f"Found document chunk: {document} (ID: {doc_id}, Distance: {distance})")

def generate_response(question, relevant_chunks,client):
    context = "\n\n".join(relevant_chunks)
    prompt = (
        "You are an assistant for question-answering tasks about Bendigo Banks product data. Use the following pieces of "
        "retrieved context to answer the question. If you don't know the answer, say that you "
        "don't know. Use ten to twenty sentences maximum and keep the answer concise."
        "\n\nContext:\n" + context + "\n\nQuestion:\n" + question
    )

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    answer = response.choices[0].message
    return answer

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
def main():
    st.title("Banking Product RAG System using Vector DB")
    #products = load_product_data()
    #st.success(f"Loaded data for {len(products)} banks")
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=openai_api_key,
        model_name="text-embedding-3-small"
    )

    # # initialize Chroma client with persistence
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection_name = "product_descriptions"
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        embedding_function=openai_ef
    )

    client = OpenAI(api_key=openai_api_key)
 
    # chunked_products = []
    # print('chunking product data...')
    # st.success("chunking data is in progress")
    # for product in products:    
    #     chunks = chunk_product_data(product)
    #     for i, chunk in enumerate(chunks):
    #         chunked_products.append({"id": f"{product['data']['productId']}_chunk{i+1}", "text": json.dumps(chunk)})
    
    # print('generating embeddings for chunked product data...')
    # st.success("generating embeddings is in progress")
    # for chunked_product in chunked_products:
    #     # print("==== Generating embeddings... ====")
    #     # print(chunked_product["text"])
    #     # print('================================')
    #     chunked_product["embedding"] = get_openai_embedding(chunked_product["text"],client )

    # print('upserting chunked product data into ChromaDB...')
    # st.success("upserting chunked data into ChromaDB is in progress")
    # for chunked_product in chunked_products:
    #     collection.upsert(
    #         ids=[chunked_product["id"]], documents=[chunked_product["text"]], embeddings=[chunked_product["embedding"]]
    #     )
    # print('querying ChromaDB for relevant chunks...')
    
    #question = "What are Bendigo Banks's mortgage products?"
    user_query = st.text_input("Enter your query about banking products:")
    if user_query:
        relevant_chunks = query_documents(user_query, 5, collection)
        answer = generate_response(user_query, relevant_chunks,client)
        
        st.write("### Initial Response:")
        st.write(answer)
        print(answer)
        
        # Allow user to augment/refine the response
        st.write("### Refine the Response")
        refined_query = st.text_area("Add additional context or questions:", 
                                   f"Based on the above response, I would like to know more about...")
        
        if st.button("Generate Refined Response"):
            relevant_chunks = query_documents(refined_query, 5, collection)
            answer = generate_response(refined_query, relevant_chunks,client)
            st.write("### Refined Response:")
            st.write(answer)
    

if __name__ == "__main__":
    main()