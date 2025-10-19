# Open Banking AI Integration

This project implements AI-powered solutions for Open Banking data, including data crawling, MCP (Model Context Protocol) server implementation, and RAG (Retrieval Augmented Generation) capabilities.

## Project Structure

```
.
├── data-puller/        # Data crawling and collection
├── mcp-server/         # Model Context Protocol server
└── rag-product/        # RAG implementation with Gemini
```

## Prerequisites

- Python 3.8+
- Virtual environment
- Google Cloud API key for Gemini
- Docker (optional)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/manjuprabhuv/ob-ai-intrgration.git
cd ob-ai-intrgration
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
# For RAG Product
cd rag-product
pip install -r requirements.txt
```

4. Set up your Gemini API key:
```bash
export GOOGLE_API_KEY=your_api_key_here
```

## Components

### Data Puller

The data puller component crawls and collects Open Banking data.

```bash
cd data-puller
python data-crawler.py
```

### MCP Server

The Model Context Protocol server provides an interface for model interactions.

```bash
cd mcp-server
python product-mcp.py
```

To Integrate with VSCode co-pilot , run mcp `product-id` mcp server .
To Integrate with gemini , Add this in settings.json and restart gemini cli.
```JSON
  "mcpServers": {
    "product-id" :{
        "command": "npx",
        "args": ["mcp-remote", "http://localhost:8000/mcp"]
    }
  }

```

Usage Demo
```
https://www.youtube.com/watch?v=awnVsvKLM6U
```



### RAG Product

The RAG implementation uses Gemini to provide intelligent responses based on banking product data.

1. Navigate to the RAG product directory:
```bash
cd rag-product
```

2. Run the Streamlit application:
```bash
streamlit run product-rag.py
```

3. Usage Demo
```
https://www.youtube.com/watch?v=hbOpLRZvk8w
```


The application will be accessible at `http://localhost:8501` by default.

## Usage

### RAG Product Features

- Query banking product information
- Get AI-generated responses using Gemini
- Refine and augment responses with additional context
- Interactive web interface using Streamlit

### Example Queries

- "What are the different types of banks available?"
- "Tell me about ANZ's banking products"
- "Compare products between CommBank and NAB"

## Troubleshooting

1. If you encounter Gemini API errors:
   - Verify your API key is set correctly
   - Ensure you're using the latest version of google-generativeai
   - Check if the model name is correct (should be 'gemini-2.5-flash-preview-09-2025')

2. For environment issues:
   - Make sure you're using the virtual environment
   - Verify all dependencies are installed
   - Check Python version compatibility


## License

This project is licensed under the MIT License - see the LICENSE file for details
