from utils.file_handler import read_sales_data
from utils.data_processor import (
    parse_transactions,
    validate_and_filter,
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products,
    generate_sales_report
)
from utils.api_handler import (
    fetch_all_products,
    create_product_mapping,
    enrich_sales_data
)


def main():
    print("=" * 70)
    print("SALES ANALYTICS SYSTEM")
    print("=" * 70)

    try:
        # 1. Read sales data
        print("[1/10] Reading sales data...")
        raw_lines = read_sales_data("data/sales_data.txt")
        print(f"• Successfully read {len(raw_lines)} transactions")

        # 2. Parse and clean
        print("[2/10] Parsing and cleaning data...")
        transactions = parse_transactions(raw_lines)
        print(f"• Parsed {len(transactions)} records")

        # 3. Display filter options
        print("[3/10] Filter Options Available:")
        _, _, preview_summary = validate_and_filter(transactions)
        regions = ["North", "South", "East", "West"]
        print("Regions:", ", ".join(regions))
        print("Amount Range: Refer above")

        apply_filter = input("Do you want to filter data? (y/n): ").strip().lower()

        region = None
        min_amount = None
        max_amount = None

        if apply_filter == "y":
            region = input("Enter region (or press Enter to skip): ").strip() or None

            min_val = input("Enter minimum transaction amount (or press Enter to skip): ").strip()
            max_val = input("Enter maximum transaction amount (or press Enter to skip): ").strip()

            min_amount = float(min_val) if min_val else None
            max_amount = float(max_val) if max_val else None

        # 4. Validate transactions
        print("[4/10] Validating transactions...")
        valid_transactions, invalid_count, summary = validate_and_filter(
            transactions,
            region=region,
            min_amount=min_amount,
            max_amount=max_amount
        )
        print(f"• Valid: {summary['final_count']} | Invalid: {invalid_count}")

        # 5. Analysis
        print("[5/10] Analyzing sales data...")
        calculate_total_revenue(valid_transactions)
        region_wise_sales(valid_transactions)
        top_selling_products(valid_transactions)
        customer_analysis(valid_transactions)
        daily_sales_trend(valid_transactions)
        find_peak_sales_day(valid_transactions)
        low_performing_products(valid_transactions)
        print("• Analysis complete")

        # 6. Fetch API products
        print("[6/10] Fetching product data from API...")
        api_products = fetch_all_products()
        print(f"• Fetched {len(api_products)} products")

        # 7. Enrich data
        print("[7/10] Enriching sales data...")
        product_mapping = create_product_mapping(api_products)
        enriched_transactions = enrich_sales_data(valid_transactions, product_mapping)

        enriched_success = sum(1 for tx in enriched_transactions if tx.get("API_Match"))
        success_rate = (enriched_success / len(enriched_transactions)) * 100 if enriched_transactions else 0
        print(f"• Enriched {enriched_success}/{len(enriched_transactions)} transactions ({success_rate:.2f}%)")

        # 8. Save enriched data
        print("[8/10] Saving enriched data...")
        print("• Saved to: data/enriched_sales_data.txt")

        # 9. Generate report
        print("[9/10] Generating report...")
        generate_sales_report(valid_transactions, enriched_transactions)
        print("• Report saved to: output/sales_report.txt")

        # 10. Complete
        print("[10/10] Process Complete!")
        print("=" * 70)

    except Exception as e:
        print("An error occurred during execution.")
        print("Error details:", e)
        print("The program exited safely without crashing.")


if __name__ == "__main__":
    main()
