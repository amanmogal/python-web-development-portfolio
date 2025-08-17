#!/usr/bin/env python3
"""
Web Scraping and API Integration Tool
A comprehensive Python application for web scraping and API data collection
"""

import requests
import json
import csv
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
from datetime import datetime
import os
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ScrapingConfig:
    """Configuration class for web scraping parameters"""
    base_url: str
    headers: Dict[str, str]
    delay_range: tuple = (1, 3)
    max_retries: int = 3
    timeout: int = 30
    max_pages: int = 10

class WebScraper:
    """Main class for web scraping operations"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(config.headers)
        self.scraped_data = []
        self.failed_urls = []
        
    def get_random_delay(self) -> float:
        """Generate random delay between requests"""
        return random.uniform(*self.config.delay_range)
    
    def make_request(self, url: str, retries: int = 0) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        try:
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            if retries < self.config.max_retries:
                time.sleep(self.get_random_delay())
                return self.make_request(url, retries + 1)
            else:
                self.failed_urls.append(url)
                return None
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """Parse HTML content using BeautifulSoup"""
        return BeautifulSoup(html_content, 'html.parser')
    
    def extract_text_data(self, soup: BeautifulSoup, selectors: Dict[str, str]) -> Dict[str, str]:
        """Extract text data using CSS selectors"""
        data = {}
        for key, selector in selectors.items():
            element = soup.select_one(selector)
            data[key] = element.get_text(strip=True) if element else ""
        return data
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from a page"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                links.append(absolute_url)
        return links
    
    def scrape_page(self, url: str, selectors: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Scrape a single page"""
        logger.info(f"Scraping: {url}")
        
        response = self.make_request(url)
        if not response:
            return None
        
        soup = self.parse_html(response.text)
        data = self.extract_text_data(soup, selectors)
        data['url'] = url
        data['scraped_at'] = datetime.now().isoformat()
        
        # Add delay between requests
        time.sleep(self.get_random_delay())
        
        return data
    
    def scrape_multiple_pages(self, urls: List[str], selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """Scrape multiple pages"""
        scraped_data = []
        
        for i, url in enumerate(urls[:self.config.max_pages]):
            data = self.scrape_page(url, selectors)
            if data:
                scraped_data.append(data)
                logger.info(f"Successfully scraped page {i+1}/{len(urls[:self.config.max_pages])}")
        
        self.scraped_data.extend(scraped_data)
        return scraped_data
    
    def save_to_csv(self, filename: str = "scraped_data.csv") -> None:
        """Save scraped data to CSV file"""
        if not self.scraped_data:
            logger.warning("No data to save")
            return
        
        df = pd.DataFrame(self.scraped_data)
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"Data saved to {filename}")
    
    def save_to_json(self, filename: str = "scraped_data.json") -> None:
        """Save scraped data to JSON file"""
        if not self.scraped_data:
            logger.warning("No data to save")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Data saved to {filename}")

class APIClient:
    """Class for API integration and data collection"""
    
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
        
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Python-API-Client/1.0'
        })
    
    def make_api_request(self, endpoint: str, method: str = 'GET', 
                        params: Dict = None, data: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def get_paginated_data(self, endpoint: str, params: Dict = None, 
                          max_pages: int = 10) -> List[Dict]:
        """Fetch paginated data from API"""
        all_data = []
        page = 1
        
        while page <= max_pages:
            if params is None:
                params = {}
            params['page'] = page
            
            data = self.make_api_request(endpoint, params=params)
            if not data:
                break
            
            # Handle different pagination formats
            if isinstance(data, list):
                all_data.extend(data)
                if len(data) == 0:
                    break
            elif isinstance(data, dict):
                if 'data' in data:
                    all_data.extend(data['data'])
                    if not data.get('has_next', True):
                        break
                elif 'results' in data:
                    all_data.extend(data['results'])
                    if not data.get('next'):
                        break
                else:
                    all_data.append(data)
                    break
            
            page += 1
            time.sleep(1)  # Rate limiting
        
        return all_data

class DataProcessor:
    """Class for processing and analyzing scraped/API data"""
    
    def __init__(self):
        self.processed_data = []
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text data"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters (keep alphanumeric and basic punctuation)
        import re
        text = re.sub(r'[^\w\s\.\,\!\?\-\:]', '', text)
        
        return text.strip()
    
    def process_scraped_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and clean scraped data"""
        processed = []
        
        for item in data:
            processed_item = {}
            for key, value in item.items():
                if isinstance(value, str):
                    processed_item[key] = self.clean_text(value)
                else:
                    processed_item[key] = value
            processed.append(processed_item)
        
        self.processed_data = processed
        return processed
    
    def analyze_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform basic analysis on the data"""
        if not data:
            return {}
        
        df = pd.DataFrame(data)
        analysis = {
            'total_records': len(data),
            'columns': list(df.columns),
            'data_types': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict()
        }
        
        # Text analysis for string columns
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            if col in df.columns:
                analysis[f'{col}_analysis'] = {
                    'unique_values': df[col].nunique(),
                    'most_common': df[col].value_counts().head(5).to_dict(),
                    'average_length': df[col].str.len().mean() if df[col].dtype == 'object' else None
                }
        
        return analysis

def main():
    """Main function to demonstrate web scraping and API integration"""
    print("=== Web Scraping and API Integration Tool ===\n")
    
    # Example: Scraping a news website
    config = ScrapingConfig(
        base_url="https://news.ycombinator.com",
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    )
    
    scraper = WebScraper(config)
    
    # Define selectors for Hacker News
    selectors = {
        'title': '.titleline > a',
        'score': '.score',
        'author': '.hnuser',
        'comments': '.subtext > a:last-child'
    }
    
    # Scrape main page
    main_page_data = scraper.scrape_page(config.base_url, selectors)
    if main_page_data:
        print("Successfully scraped main page data")
        print(f"Title: {main_page_data.get('title', 'N/A')}")
    
    # Example: API integration (using a public API)
    print("\n=== API Integration Example ===")
    
    # Using JSONPlaceholder API for demonstration
    api_client = APIClient("https://jsonplaceholder.typicode.com")
    
    # Fetch posts
    posts = api_client.get_paginated_data("posts", max_pages=2)
    print(f"Fetched {len(posts)} posts from API")
    
    if posts:
        print(f"First post title: {posts[0].get('title', 'N/A')}")
    
    # Process data
    processor = DataProcessor()
    
    # Combine scraped and API data
    all_data = []
    if main_page_data:
        all_data.append(main_page_data)
    all_data.extend(posts)
    
    # Process and analyze
    processed_data = processor.process_scraped_data(all_data)
    analysis = processor.analyze_data(processed_data)
    
    print(f"\nData Analysis Results:")
    print(f"Total records: {analysis.get('total_records', 0)}")
    print(f"Columns: {analysis.get('columns', [])}")
    
    # Save results
    scraper.scraped_data = processed_data
    scraper.save_to_csv("combined_data.csv")
    scraper.save_to_json("combined_data.json")
    
    print("\n=== Processing Complete ===")
    print("Check 'combined_data.csv' and 'combined_data.json' for results")

if __name__ == "__main__":
    main()