import requests


def fetch_all_products():
    url = "https://dummyjson.com/products?limit=100"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        products = data.get('products', [])

        print(f"Successfully fetched {len(products)} products from API.")
        return products

    except requests.exceptions.RequestException as e:
        print("Failed to fetch products from API.")
        print("Error:", e)
        return []
    
def create_product_mapping(api_products):
    product_mapping = {}

    for product in api_products:
        product_id = product.get('id')

        if product_id is None:
            continue

        product_mapping[product_id] = {
            'title': product.get('title'),
            'category': product.get('category'),
            'brand': product.get('brand'),
            'rating': product.get('rating')
        }

    return product_mapping

def enrich_sales_data(transactions, product_mapping):
    enriched_transactions = []

    for tx in transactions:
        enriched_tx = tx.copy()

        # Default API fields
        enriched_tx['API_Category'] = None
        enriched_tx['API_Brand'] = None
        enriched_tx['API_Rating'] = None
        enriched_tx['API_Match'] = False

        try:
            product_id = tx.get('ProductID', '')

            # Extract numeric ID: P101 -> 101
            numeric_id = int(product_id.replace('P', ''))

            if numeric_id in product_mapping:
                api_info = product_mapping[numeric_id]
                enriched_tx['API_Category'] = api_info.get('category')
                enriched_tx['API_Brand'] = api_info.get('brand')
                enriched_tx['API_Rating'] = api_info.get('rating')
                enriched_tx['API_Match'] = True

        except Exception:
            # Any error keeps API_Match as False and fields as None
            pass

        enriched_transactions.append(enriched_tx)

    # Save to file as required
    save_enriched_data(enriched_transactions)

    return enriched_transactions


def save_enriched_data(enriched_transactions, filename='data/enriched_sales_data.txt'):
    header = [
        'TransactionID', 'Date', 'ProductID', 'ProductName',
        'Quantity', 'UnitPrice', 'CustomerID', 'Region',
        'API_Category', 'API_Brand', 'API_Rating', 'API_Match'
    ]

    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write('|'.join(header) + '\n')

            for tx in enriched_transactions:
                row = [
                    str(tx.get('TransactionID', '')),
                    str(tx.get('Date', '')),
                    str(tx.get('ProductID', '')),
                    str(tx.get('ProductName', '')),
                    str(tx.get('Quantity', '')),
                    str(tx.get('UnitPrice', '')),
                    str(tx.get('CustomerID', '')),
                    str(tx.get('Region', '')),
                    str(tx.get('API_Category')) if tx.get('API_Category') is not None else '',
                    str(tx.get('API_Brand')) if tx.get('API_Brand') is not None else '',
                    str(tx.get('API_Rating')) if tx.get('API_Rating') is not None else '',
                    str(tx.get('API_Match'))
                ]

                file.write('|'.join(row) + '\n')

        print(f"Enriched sales data saved to {filename}")

    except Exception as e:
        print("Failed to save enriched sales data.")
        print("Error:", e)

