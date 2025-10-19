from fastmcp import FastMCP
import os
import json

mcp = FastMCP("Product MCP Server")

@mcp.tool(
    description="Retrieve product information for a given product ID of a bank.",
    name="get_product_info",
)
def get_product_info(product_id: str, bank_name: str) -> dict:
    """
    Retrieve product information for a given product ID of a bank.
    
    Parameters:
        product_id: The unique identifier of the product.
        BankName: The name of the bank to which the product belongs.
    """
    bank_folder = f"./data-puller/data/{bank_name}"
    product_file_path = os.path.join(bank_folder, f"{product_id}.json")
    
    if not os.path.exists(product_file_path):
        return {"error": f"Product file for {product_id} in {bank_name} not found."}
    
    with open(product_file_path, 'r') as infile:
        product_data = json.load(infile)
    
    return product_data 

if __name__ == "__main__":
    """
    Entry point for the MCP Product Server.
    
    When this script is run directly, it starts the FastMCP server which will:
    - Listen for incoming requests from MCP clients.
    - Execute the defined tools based on client requests.
    - Return results back to the clients.
    """
    mcp.run(transport="http", host="localhost", port=8000)