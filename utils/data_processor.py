def parse_transactions(raw_lines):
    cleaned_transactions = []

    for line in raw_lines:
        parts = line.split('|')

        if len(parts) != 8:
            continue

        transaction_id = parts[0].strip()
        date = parts[1].strip()
        product_id = parts[2].strip()

        product_name = parts[3].replace(',', '').strip()

        quantity_str = parts[4].replace(',', '').strip()
        unit_price_str = parts[5].replace(',', '').strip()

        customer_id = parts[6].strip()
        region = parts[7].strip()

        try:
            quantity = int(quantity_str)
            unit_price = float(unit_price_str)
        except ValueError:
            continue

        record = {
            'TransactionID': transaction_id,
            'Date': date,
            'ProductID': product_id,
            'ProductName': product_name,
            'Quantity': quantity,
            'UnitPrice': unit_price,
            'CustomerID': customer_id,
            'Region': region
        }

        cleaned_transactions.append(record)

    return cleaned_transactions

def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    valid_transactions = []
    invalid_count = 0

    regions = set()
    amounts = []

    for tx in transactions:
        try:
            if (
                tx.get('Quantity') <= 0 or
                tx.get('UnitPrice') <= 0 or
                not tx.get('TransactionID', '').startswith('T') or
                not tx.get('ProductID', '').startswith('P') or
                not tx.get('CustomerID', '').startswith('C') or
                not tx.get('Region')
            ):
                invalid_count += 1
                continue

            amount = tx['Quantity'] * tx['UnitPrice']
            regions.add(tx['Region'])
            amounts.append(amount)

            tx['Amount'] = amount
            valid_transactions.append(tx)

        except Exception:
            invalid_count += 1

    print("Available Regions:", sorted(regions))
    if amounts:
        print("Transaction Amount Range:", min(amounts), "to", max(amounts))

    filtered_by_region = 0
    filtered_by_amount = 0

    if region:
        before = len(valid_transactions)
        valid_transactions = [t for t in valid_transactions if t['Region'] == region]
        filtered_by_region = before - len(valid_transactions)
        print("Records after region filter:", len(valid_transactions))

    if min_amount is not None:
        before = len(valid_transactions)
        valid_transactions = [t for t in valid_transactions if t['Amount'] >= min_amount]
        filtered_by_amount += before - len(valid_transactions)

    if max_amount is not None:
        before = len(valid_transactions)
        valid_transactions = [t for t in valid_transactions if t['Amount'] <= max_amount]
        filtered_by_amount += before - len(valid_transactions)

    if min_amount is not None or max_amount is not None:
        print("Records after amount filter:", len(valid_transactions))

    summary = {
        'total_input': len(transactions),
        'invalid': invalid_count,
        'filtered_by_region': filtered_by_region,
        'filtered_by_amount': filtered_by_amount,
        'final_count': len(valid_transactions)
    }

    return valid_transactions, invalid_count, summary

def calculate_total_revenue(transactions):
    total_revenue = 0.0

    for tx in transactions:
        total_revenue += tx['Quantity'] * tx['UnitPrice']

    return total_revenue

def region_wise_sales(transactions):
    region_data = {}
    total_sales = 0.0

    for tx in transactions:
        region = tx['Region']
        amount = tx['Quantity'] * tx['UnitPrice']
        total_sales += amount

        if region not in region_data:
            region_data[region] = {
                'total_sales': 0.0,
                'transaction_count': 0
            }

        region_data[region]['total_sales'] += amount
        region_data[region]['transaction_count'] += 1

    for region in region_data:
        percentage = (region_data[region]['total_sales'] / total_sales) * 100
        region_data[region]['percentage'] = round(percentage, 2)

    sorted_regions = dict(
        sorted(
            region_data.items(),
            key=lambda x: x[1]['total_sales'],
            reverse=True
        )
    )

    return sorted_regions

def top_selling_products(transactions, n=5):
    product_data = {}

    for tx in transactions:
        product = tx['ProductName']
        quantity = tx['Quantity']
        revenue = tx['Quantity'] * tx['UnitPrice']

        if product not in product_data:
            product_data[product] = {
                'total_quantity': 0,
                'total_revenue': 0.0
            }

        product_data[product]['total_quantity'] += quantity
        product_data[product]['total_revenue'] += revenue

    product_list = [
        (product,
         data['total_quantity'],
         data['total_revenue'])
        for product, data in product_data.items()
    ]

    product_list.sort(key=lambda x: x[1], reverse=True)

    return product_list[:n]
def customer_analysis(transactions):
    customer_data = {}

    for tx in transactions:
        customer = tx['CustomerID']
        amount = tx['Quantity'] * tx['UnitPrice']
        product = tx['ProductName']

        if customer not in customer_data:
            customer_data[customer] = {
                'total_spent': 0.0,
                'purchase_count': 0,
                'products_bought': set()
            }

        customer_data[customer]['total_spent'] += amount
        customer_data[customer]['purchase_count'] += 1
        customer_data[customer]['products_bought'].add(product)

    for customer in customer_data:
        total = customer_data[customer]['total_spent']
        count = customer_data[customer]['purchase_count']

        customer_data[customer]['avg_order_value'] = round(total / count, 2)
        customer_data[customer]['products_bought'] = list(
            customer_data[customer]['products_bought']
        )

    sorted_customers = dict(
        sorted(
            customer_data.items(),
            key=lambda x: x[1]['total_spent'],
            reverse=True
        )
    )

    return sorted_customers

def daily_sales_trend(transactions):
    daily_data = {}

    for tx in transactions:
        date = tx['Date']
        amount = tx['Quantity'] * tx['UnitPrice']
        customer = tx['CustomerID']

        if date not in daily_data:
            daily_data[date] = {
                'revenue': 0.0,
                'transaction_count': 0,
                'unique_customers': set()
            }

        daily_data[date]['revenue'] += amount
        daily_data[date]['transaction_count'] += 1
        daily_data[date]['unique_customers'].add(customer)

    for date in daily_data:
        daily_data[date]['unique_customers'] = len(
            daily_data[date]['unique_customers']
        )

    sorted_daily_data = dict(sorted(daily_data.items()))

    return sorted_daily_data

def find_peak_sales_day(transactions):
    daily_trends = daily_sales_trend(transactions)

    peak_date = None
    peak_revenue = 0.0
    peak_transactions = 0

    for date, data in daily_trends.items():
        if data['revenue'] > peak_revenue:
            peak_revenue = data['revenue']
            peak_transactions = data['transaction_count']
            peak_date = date

    return peak_date, peak_revenue, peak_transactions

def low_performing_products(transactions, threshold=10):
    product_data = {}

    for tx in transactions:
        product = tx['ProductName']
        quantity = tx['Quantity']
        revenue = tx['Quantity'] * tx['UnitPrice']

        if product not in product_data:
            product_data[product] = {
                'total_quantity': 0,
                'total_revenue': 0.0
            }

        product_data[product]['total_quantity'] += quantity
        product_data[product]['total_revenue'] += revenue

    low_products = []

    for product, data in product_data.items():
        if data['total_quantity'] < threshold:
            low_products.append(
                (product, data['total_quantity'], data['total_revenue'])
            )

    low_products.sort(key=lambda x: x[1])

    return low_products

from datetime import datetime


def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    def money(value):
        return f"{value:,.2f}"

    total_revenue = sum(tx['Quantity'] * tx['UnitPrice'] for tx in transactions)
    total_transactions = len(transactions)
    avg_order_value = total_revenue / total_transactions if total_transactions else 0

    dates = sorted(tx['Date'] for tx in transactions)
    date_range = (dates[0], dates[-1]) if dates else ("N/A", "N/A")

    # Region-wise summary
    region_summary = {}
    for tx in transactions:
        region = tx['Region']
        amount = tx['Quantity'] * tx['UnitPrice']
        region_summary.setdefault(region, {'sales': 0, 'count': 0})
        region_summary[region]['sales'] += amount
        region_summary[region]['count'] += 1

    for r in region_summary:
        region_summary[r]['percentage'] = (region_summary[r]['sales'] / total_revenue) * 100

    region_summary = dict(
        sorted(region_summary.items(), key=lambda x: x[1]['sales'], reverse=True)
    )

    # Top products
    product_data = {}
    for tx in transactions:
        product = tx['ProductName']
        amount = tx['Quantity'] * tx['UnitPrice']
        product_data.setdefault(product, {'qty': 0, 'revenue': 0})
        product_data[product]['qty'] += tx['Quantity']
        product_data[product]['revenue'] += amount

    top_products = sorted(
        product_data.items(),
        key=lambda x: x[1]['qty'],
        reverse=True
    )[:5]

    # Top customers
    customer_data = {}
    for tx in transactions:
        cid = tx['CustomerID']
        amount = tx['Quantity'] * tx['UnitPrice']
        customer_data.setdefault(cid, {'spent': 0, 'count': 0})
        customer_data[cid]['spent'] += amount
        customer_data[cid]['count'] += 1

    top_customers = sorted(
        customer_data.items(),
        key=lambda x: x[1]['spent'],
        reverse=True
    )[:5]

    # Daily sales trend
    daily_data = {}
    for tx in transactions:
        date = tx['Date']
        amount = tx['Quantity'] * tx['UnitPrice']
        daily_data.setdefault(date, {'revenue': 0, 'count': 0, 'customers': set()})
        daily_data[date]['revenue'] += amount
        daily_data[date]['count'] += 1
        daily_data[date]['customers'].add(tx['CustomerID'])

    daily_data = dict(sorted(daily_data.items()))

    peak_day = max(daily_data.items(), key=lambda x: x[1]['revenue'])

    # Low performing products
    low_products = [
        (p, d['qty'], d['revenue'])
        for p, d in product_data.items()
        if d['qty'] < 10
    ]

    # API enrichment summary
    enriched_success = [tx for tx in enriched_transactions if tx.get('API_Match')]
    enriched_failed = [tx['ProductName'] for tx in enriched_transactions if not tx.get('API_Match')]
    enrichment_rate = (len(enriched_success) / len(enriched_transactions)) * 100 if enriched_transactions else 0

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("SALES ANALYTICS REPORT\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Records Processed: {total_transactions}\n")
        f.write("=" * 70 + "\n\n")

        f.write("OVERALL SUMMARY\n")
        f.write(f"Total Revenue: {money(total_revenue)}\n")
        f.write(f"Total Transactions: {total_transactions}\n")
        f.write(f"Average Order Value: {money(avg_order_value)}\n")
        f.write(f"Date Range: {date_range[0]} to {date_range[1]}\n\n")

        f.write("REGION-WISE PERFORMANCE\n")
        for region, data in region_summary.items():
            f.write(
                f"{region}: Sales={money(data['sales'])}, "
                f"Transactions={data['count']}, "
                f"Percentage={data['percentage']:.2f}%\n"
            )
        f.write("\n")

        f.write("TOP 5 PRODUCTS\n")
        for i, (product, data) in enumerate(top_products, 1):
            f.write(
                f"{i}. {product} | Quantity={data['qty']} | Revenue={money(data['revenue'])}\n"
            )
        f.write("\n")

        f.write("TOP 5 CUSTOMERS\n")
        for i, (cid, data) in enumerate(top_customers, 1):
            f.write(
                f"{i}. {cid} | Spent={money(data['spent'])} | Orders={data['count']}\n"
            )
        f.write("\n")

        f.write("DAILY SALES TREND\n")
        for date, data in daily_data.items():
            f.write(
                f"{date} | Revenue={money(data['revenue'])} | "
                f"Transactions={data['count']} | "
                f"Unique Customers={len(data['customers'])}\n"
            )
        f.write("\n")

        f.write("PRODUCT PERFORMANCE ANALYSIS\n")
        f.write(
            f"Best Selling Day: {peak_day[0]} "
            f"({money(peak_day[1]['revenue'])})\n"
        )
        f.write("Low Performing Products:\n")
        for p in low_products:
            f.write(f"- {p[0]} | Qty={p[1]} | Revenue={money(p[2])}\n")
        f.write("\n")

        f.write("API ENRICHMENT SUMMARY\n")
        f.write(f"Total Enriched Successfully: {len(enriched_success)}\n")
        f.write(f"Success Rate: {enrichment_rate:.2f}%\n")
        f.write("Products Not Enriched:\n")
        for p in set(enriched_failed):
            f.write(f"- {p}\n")

    print(f"Sales report generated at {output_file}")



