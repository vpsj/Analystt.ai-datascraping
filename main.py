from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup
import requests
import time

def scrape_product_details(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        
        product_description_tag = soup.find('meta', attrs={'name': 'description'})
        product_description = product_description_tag['content'] if product_description_tag else None

        
        asin_tag = soup.find('th', string='ASIN')
        asin = asin_tag.find_next('td').text.strip() if asin_tag else None

        
        manufacturer_tag = soup.find('th', string='Manufacturer')
        manufacturer = manufacturer_tag.find_next('td').text.strip() if manufacturer_tag else None

        return product_description, asin, manufacturer
    else:
        print(f"Failed to fetch data for {url}. Status code: {response.status_code}")
        return None, None, None

def get_amazon_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.find_all('div', {'data-component-type': 's-search-result'})

        data = []
        for product in products:
            try:
                product_url = product.find('a', {'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})['href']
                product_url = urljoin('https://www.amazon.in/', product_url)  
                product_name = product.find('h2').text.strip()
                product_price = product.find('span', class_='a-price-whole').text.strip()
                product_rating = product.find('span', class_='a-icon-alt').text.strip().split()[0]
                num_reviews = product.find('span', class_='a-size-base s-underline-text').text.strip()

                
                product_description, asin, manufacturer = scrape_product_details(product_url)

                print(f"Product URL: {product_url}")
                print(f"Product Name: {product_name}")
                print(f"Product Price: {product_price}")
                print(f"Rating: {product_rating}")
                print(f"Number of Reviews: {num_reviews}")
                print(f"Description: {product_description}")
                print(f"ASIN: {asin}")
                print(f"Manufacturer: {manufacturer}")
                print()

                data.append({
                    'Product URL': product_url,
                    'Product Name': product_name,
                    'Product Price': product_price,
                    'Rating': product_rating,
                    'Number of Reviews': num_reviews,
                    'Description': product_description,
                    'ASIN': asin,
                    'Manufacturer': manufacturer
                })
            except AttributeError:
                continue

        return data
    else:
        print(f"Failed to fetch data from the URL. Status code: {response.status_code}")
        return []

if __name__ == "__main__":
    base_url = 'https://www.amazon.in/s'
    params = {
        'k': 'bags',
        'crid': '2M096C61O4MLT',
        'qid': '1653308124',
        'sprefix': 'ba%2Caps%2C283',
        'ref': 'sr_pg_1'
    }

    all_data = []
    num_pages = 20

    for page in range(1, num_pages + 1):
        params['page'] = page
        response = requests.get(base_url, params=params, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            print(f"Scraping Page {page}")
            data = get_amazon_data(response.url)
            all_data.extend(data)
        else:
            print(f"Failed to fetch data from Page {page}. Status code: {response.status_code}")

        

    df = pd.DataFrame(all_data)
    df.to_csv('amazon_products_with_details.csv', index=False)
    print("Data scraped successfully and saved to 'amazon_products_with_details.csv'.")
