"""Run the complete Regex Data Cleaning & Log Analyzer project."""
from src.data_generator import generate_sample_data
from src.data_cleaner import clean_customer_data
from src.log_parser import parse_log_file

def main():
    print("=" * 60)
    print("REGEX DATA CLEANING & LOG ANALYZER")
    print("=" * 60)
    print("\n[1/3] Generating sample input files...")
    generate_sample_data()
    print("\n[2/3] Cleaning customer data...")
    customers = clean_customer_data()
    print("\n[3/3] Parsing application logs...")
    logs = parse_log_file()
    print("\n" + "=" * 60)
    print("PROJECT EXECUTION COMPLETED")
    print(f"Customer records: {len(customers)}")
    print(f"Parsed log records: {len(logs)}")
    print("Check the data/processed/ folder for output CSV files.")
    print("=" * 60)

if __name__ == "__main__":
    main()
