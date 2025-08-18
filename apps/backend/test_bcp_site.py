#!/usr/bin/env python3
import asyncio
import aiohttp
import ssl
from bs4 import BeautifulSoup

async def test_bcp_site():
    """Test BCP site manually to see what's actually there."""
    url = "https://www.bcp.ma/fr/investisseurs/informations-financieres"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.113 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr,en;q=0.9",
    }
    
    # Create SSL context that skips verification
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        try:
            async with session.get(url) as resp:
                print(f"Status: {resp.status}")
                print(f"Content-Type: {resp.headers.get('content-type', 'unknown')}")
                
                if resp.status == 200:
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for PDF links
                    pdf_links = soup.find_all('a', href=lambda x: x and x.lower().endswith('.pdf'))
                    print(f"\nFound {len(pdf_links)} PDF links:")
                    for link in pdf_links[:10]:  # Show first 10
                        print(f"  {link.get('href')} - {link.get_text(strip=True)}")
                    
                    # Look for any links
                    all_links = soup.find_all('a', href=True)
                    print(f"\nTotal links: {len(all_links)}")
                    
                    # Look for specific text patterns
                    text_content = soup.get_text()
                    if 'rapport' in text_content.lower():
                        print("Found 'rapport' in text")
                    if 'financier' in text_content.lower():
                        print("Found 'financier' in text")
                    if 'publication' in text_content.lower():
                        print("Found 'publication' in text")
                        
                else:
                    print(f"Failed to fetch: {resp.status}")
                    
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_bcp_site())
