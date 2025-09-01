import os
import aiohttp
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

async def fetch_page(session: aiohttp.ClientSession, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    while True:
        try:
            logger.info(f"Fetching page from {url} with params {params}")
            async with session.get(url, params=params) as response:
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', '5'))
                    logger.warning(f"Rate limited. Waiting {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    continue
                logger.debug(f"Response status: {response.status}")
                response.raise_for_status()
                data = await response.json()
                logger.info(f"Successfully fetched page {params.get('page')} with {len(data.get('products', []))} products")
                return data
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching page: {e}")
            await asyncio.sleep(1)
            continue

async def fetch_all_products(
    base_url: Optional[str] = None,
    page_size: Optional[int] = 100
) -> List[Dict[str, Any]]:
    """
    Fetches all products from the API with pagination and retry handling.
    Args:
        base_url: Optional API URL, defaults to environment variable API_BASE_URL
        page_size: Number of products per page
    """
    if base_url is None:
        base_url = os.getenv('API_BASE_URL', 'http://mock_api:5000/api/products')
    """
    Fetches all products from the API with pagination and retry handling.
    """
    all_products = []
    
    async with aiohttp.ClientSession() as session:
        page = 1
        while True:
            params: Dict[str, Any] = {
                'page': page,
                'per_page': page_size
            }
            
            data = await fetch_page(session, base_url, params)
            products = data.get('items', [])
            
            if not products:
                break
            
            logger.info(f"Fetched page {data.get('page')} of {data.get('total') // data.get('size', 10) + 1} with {len(products)} items")
                
            # Add metadata
            for product in products:
                product['source'] = 'api'
                product['ingested_at'] = datetime.now().isoformat()
                
            all_products.extend(products)
            page += 1
            
    return all_products
