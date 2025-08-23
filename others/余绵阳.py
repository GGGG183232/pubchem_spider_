import pandas as pd
import requests
import os
from concurrent.futures import ThreadPoolExecutor
import time
import aiohttp
import asyncio


# Async download function for maximum speed
async def download_pdf_async(session, row, output_dir):
    sms_content = row.get('smsContent')
    filename = row.get('smsAttname', f"{sms_content}.pdf")

    if not sms_content or sms_content == '暂无':
        return False

    file_path = os.path.join(output_dir, filename)
    if os.path.exists(file_path):
        return True

    url = f"https://www.cde.org.cn/hymlj/download/sms/{sms_content}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Referer": f"https://www.cde.org.cn/hymlj/detailPage/{row.get('idCode')}"
    }

    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                content = await response.read()
                if len(content) > 1000:
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    return True
            return False
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False


# Main async function
async def main():
    output_dir = "说明书"
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv('drug_details.csv')
    valid_rows = df[df['smsContent'].notna() & (df['smsContent'] != '暂无')].to_dict('records')

    # Configure connection pool with higher limits
    conn = aiohttp.TCPConnector(limit=50)  # Adjust based on your connection capabilities
    async with aiohttp.ClientSession(connector=conn) as session:
        # Download in batches of 50
        batch_size = 50
        for i in range(0, len(valid_rows), batch_size):
            batch = valid_rows[i:i + batch_size]
            tasks = [download_pdf_async(session, row, output_dir) for row in batch]
            results = await asyncio.gather(*tasks)
            print(f"Completed batch {i // batch_size + 1}/{(len(valid_rows) + batch_size - 1) // batch_size}")


# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())