import json
import google.generativeai as genai
import os
from typing import Dict, List
import streamlit as st

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
print(GOOGLE_API_KEY)
genai.configure(api_key=GOOGLE_API_KEY)

# Select Gemini model
model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')

def load_product_data(data_dir: str = "../data-puller/data/Bendigo Bank") -> List[Dict]:
    """Load JSON product data from Bendigo Bank directory.

    - Reads .json files from the specified Bendigo Bank directory
    - Ignores 'Bendigo Bank_products.json' file
    - If a file contains a list of objects, each dict is appended
    - If a file contains a single dict, it's appended
    """
    data_dir = os.path.abspath(data_dir)
    products: List[Dict] = []

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

def query_products(query: str, context: List[Dict]) -> str:
    """Query Gemini with product data context."""
    # Prepare context for Gemini
    context_str = json.dumps(context, indent=2)
    
    prompt = f"""Given the following banking product data:
    {context_str}
    
    User query: {query}
    
    Please provide a detailed response based on this data."""
    
    # Generate response using Gemini
    response = model.generate_content(prompt)
    return response.text

def main():
    st.title("Banking Product RAG System")
    
    # Load product data
    try:
        products = load_product_data()
        st.success(f"Loaded data for {len(products)} banks")
    except Exception as e:
        st.error(f"Error loading product data: {str(e)}")
        return
    
    # User input
    user_query = st.text_input("Enter your query about banking products:")
    
    if user_query:
        # Get initial response from Gemini
        response = query_products(user_query, products)
        st.write("### Initial Response:")
        st.write(response)
        
        # Allow user to augment/refine the response
        st.write("### Refine the Response")
        refined_query = st.text_area("Add additional context or questions:", 
                                   f"Based on the above response, I would like to know more about...")
        
        if st.button("Generate Refined Response"):
            refined_response = query_products(refined_query, products)
            st.write("### Refined Response:")
            st.write(refined_response)

if __name__ == "__main__":
    main()
