import pandas as pd
from tqdm import tqdm

# File paths
input_file = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\forhistory\formatted\useable\cleaned_appended_20240806_093139.csv'
output_file = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\forhistory\formatted\useable\cleaned_no_unknown_age.csv'
removed_rows_file = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\forhistory\formatted\useable\unknown_age_rows.csv'

def process_data(df):
    print("Identifying rows with unknown age...")
    unknown_age_mask = df['Age'].isna() & (df['AgeGroup'] == 'Unknown')
    unknown_age_rows = df[unknown_age_mask]
    
    print("Removing rows with unknown age from the main dataset...")
    cleaned_df = df[~unknown_age_mask]
    
    return cleaned_df, unknown_age_rows

def main():
    print("Reading CSV file...")
    df = pd.read_csv(input_file, encoding='utf-8-sig', low_memory=False)
    print(f"Read {len(df)} rows.")
    
    cleaned_df, unknown_age_rows = process_data(df)
    
    print("Saving cleaned data...")
    cleaned_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print("Saving removed rows...")
    unknown_age_rows.to_csv(removed_rows_file, index=False, encoding='utf-8-sig')
    
    print(f"\nProcessing summary:")
    print(f"Original shape: {df.shape}")
    print(f"Cleaned shape: {cleaned_df.shape}")
    print(f"Removed rows: {len(unknown_age_rows)}")
    print(f"\nCleaned data saved to: {output_file}")
    print(f"Removed rows saved to: {removed_rows_file}")

if __name__ == "__main__":
    main()