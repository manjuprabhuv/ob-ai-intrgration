import json
import os
import requests
from concurrent.futures import ThreadPoolExecutor

def fetch_bank_data(holder):
    """Fetches and saves data for a single bank."""
    bank_name = holder.get('bankName')
    url = holder.get('url')

    if not bank_name or not url:
        print(f"Skipping entry due to missing BankName or URL: {holder}")
        return None

    product_headers = {
        'Accept': 'application/json',
        'x-v': '3'
    }
    product_details_headers = {
        'Accept': 'application/json',
        'x-v': '4'
    }

    # Create a folder for the bank if it doesn't exist
    bank_folder = f"data/{bank_name}"
    if not os.path.exists(bank_folder):
        os.makedirs(bank_folder)
        print(f"Created folder: {bank_folder}")

    try:
        response = requests.get(f"{url}/banking/products?page=1&page-size=1000", headers=product_headers)
        if response.status_code != 200:
            print(f"Request for {bank_name} failed with status code {response.status_code}")
            return bank_name

        response_data = response.json()

        # Save the full product list
        products_list_path = os.path.join(bank_folder, f"{bank_name}_products.json")
        with open(products_list_path, 'w') as outfile:
            json.dump(response_data, outfile, indent=4)
        print(f"Successfully saved product list for {bank_name} to {products_list_path}")

        # Iterate over products and fetch individual product details
        products = response_data.get("data", {}).get("products", [])
        for product in products:
            product_id = product.get("productId")
            if not product_id:
                print(f"Skipping product in {bank_name} due to missing productId.")
                continue

            try:
                product_response = requests.get(f"{url}/banking/products/{product_id}", headers=product_details_headers)
                if product_response.status_code != 200:
                    print(f"Request {url}/banking/products/{product_id} for product {product_id} in {bank_name} failed with status code {product_response.status_code}")
                    continue

                product_data = product_response.json()

                # Save the product data in a file named after the product ID
                file_path = os.path.join(bank_folder, f"{product_id}.json")
                with open(file_path, 'w') as outfile:
                    json.dump(product_data, outfile, indent=4)
                print(f"Successfully saved product {product_id} for {bank_name} to {file_path}")

            except requests.exceptions.RequestException as e:
                print(f"Error fetching product {product_id} for {bank_name}: {e}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for product {product_id} for {bank_name}: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {bank_name} from {url}: {e}")
        return bank_name
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response for {bank_name} from {url}: {e}")
        return bank_name
    except Exception as e:
        print(f"An unexpected error occurred for {bank_name}: {e}")
        return bank_name

    return None

def crawl_data():
    with open('data-holder.json', 'r') as f:
        data_holders = json.load(f)

    failed_banks = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(fetch_bank_data, data_holders)
        for result in results:
            if result:
                failed_banks.append(result)

    if failed_banks:
        print("\n--- Failed Banks ---")
        for bank in failed_banks:
            print(bank)

if __name__ == '__main__':
    crawl_data()