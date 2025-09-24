import requests
import json
import csv
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

def extract_id_from_url(url):
    return url.split('/')[-1]

def clean_field(value):
    if isinstance(value, str):
        # Remove newlines and commas
        return value.replace('\n', ' ').replace(',', '，')
    return value

def fetch_drug_data(url):
    try:
        session = requests.Session()
        
        # Visit main site for cookies
        main_url = "https://www.cde.org.cn/"
        session.get(main_url, headers=headers)
        
        # Extract the ID from the URL
        id_code = extract_id_from_url(url)
        
        # Make the API request
        api_url = "https://www.cde.org.cn/hymlj/getInfoById"
        data = {"idCode": id_code}
        api_headers = headers.copy()
        api_headers["Content-Type"] = "application/x-www-form-urlencoded"
        api_headers["Referer"] = url
        
        time.sleep(0.5)
        
        response = session.post(api_url, data=data, headers=api_headers)
        
        if response.status_code == 200:
            result = response.json()
            if result['code'] == 200:
                data = result['data']
                
                # Clean all string fields
                for key, value in data.items():
                    data[key] = clean_field(value)
                
                # Add the original URL
                data['source_url'] = url
                return data
        
        return None
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None

def main():
    global headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    # Read the CSV with drug URLs
    df = pd.read_csv('drug_data.csv')
    urls = df['药物链接'].tolist()
    
    # Process first URL to get all possible fields
    print("Processing first URL to determine all fields...")
    first_result = fetch_drug_data(urls[0])
    if not first_result:
        print("Failed to process first URL. Exiting.")
        return
    
    # Get all possible fields
    all_fields = list(first_result.keys())
    
    # Create output file
    output_file = 'drug_details.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=all_fields)
        writer.writeheader()
        writer.writerow(first_result)
    
    # Process remaining URLs in batches
    remaining_urls = urls[1:]
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=64) as executor:
        batch_size = 200
        for i in range(0, len(remaining_urls), batch_size):
            batch_urls = remaining_urls[i:i+batch_size]
            results = list(executor.map(fetch_drug_data, batch_urls))
            
            valid_results = [r for r in results if r is not None]
            
            if valid_results:
                with open(output_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=all_fields, extrasaction='ignore')
                    writer.writerows(valid_results)
            
            print(f"Processed batch {i//batch_size + 1}/{(len(remaining_urls) + batch_size - 1)//batch_size}")
            time.sleep(2)

if __name__ == "__main__":
    main()
    print("Data extraction complete!")