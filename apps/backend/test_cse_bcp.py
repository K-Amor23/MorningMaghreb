#!/usr/bin/env python3
import asyncio
import aiohttp
import ssl
from bs4 import BeautifulSoup

async def test_cse_bcp():
    """Test CSE document host directly for BCP reports."""
    base_url = "https://www.casablanca-bourse.com"
    
    # Focus on the working instruments page where we found BCP
    working_url = f"{base_url}/fr/marche-cash/instruments-actions"
    
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
            print(f"Testing CSE instruments page: {working_url}")
            async with session.get(working_url) as resp:
                print(f"Status: {resp.status}")
                print(f"Content-Type: {resp.headers.get('content-type', 'unknown')}")
                
                if resp.status == 200:
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    print(f"\nPage title: {soup.title.string if soup.title else 'No title'}")
                    
                    # Look for BCP-specific content
                    text_content = soup.get_text()
                    print(f"\nTotal text length: {len(text_content)} characters")
                    
                    # Find all occurrences of BCP in the text
                    bcp_positions = []
                    lines = text_content.split('\n')
                    for i, line in enumerate(lines):
                        if 'BCP' in line:
                            bcp_positions.append((i, line.strip()))
                    
                    print(f"\nFound {len(bcp_positions)} lines containing 'BCP':")
                    for pos, line in bcp_positions[:10]:  # Show first 10
                        print(f"  Line {pos}: {line}")
                    
                    # Look for BCP in HTML elements
                    bcp_elements = soup.find_all(text=lambda text: text and 'BCP' in text)
                    print(f"\nFound {len(bcp_elements)} HTML elements containing 'BCP':")
                    for elem in bcp_elements[:10]:  # Show first 10
                        parent = elem.parent
                        if parent:
                            print(f"  {parent.name}: {elem.strip()}")
                    
                    # Look for any tables that might contain company data
                    tables = soup.find_all('table')
                    print(f"\nFound {len(tables)} tables")
                    for i, table in enumerate(tables[:3]):  # Show first 3
                        rows = table.find_all('tr')
                        print(f"  Table {i+1}: {len(rows)} rows")
                        if rows:
                            # Show first few rows
                            for j, row in enumerate(rows[:5]):
                                cells = row.find_all(['td', 'th'])
                                cell_texts = [cell.get_text(strip=True) for cell in cells]
                                if any('BCP' in text for text in cell_texts):
                                    print(f"    Row {j+1} (contains BCP): {cell_texts}")
                    
                    # Look for any forms or search mechanisms
                    forms = soup.find_all('form')
                    print(f"\nFound {len(forms)} forms")
                    for i, form in enumerate(forms):
                        print(f"  Form {i+1}: action='{form.get('action', '')}', method='{form.get('method', '')}'")
                        inputs = form.find_all('input')
                        for inp in inputs:
                            print(f"    Input: name='{inp.get('name', '')}', type='{inp.get('type', '')}', value='{inp.get('value', '')}'")
                    
                    # Look for any links that might lead to company details
                    all_links = soup.find_all('a', href=True)
                    print(f"\nTotal links: {len(all_links)}")
                    
                    # Look for links that might contain company information
                    company_links = soup.find_all('a', href=lambda x: x and any(term in x.lower() for term in ['emetteur', 'societe', 'company', 'detail']))
                    print(f"\nCompany-related links: {len(company_links)}")
                    for link in company_links[:10]:  # Show first 10
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        if 'BCP' in text or 'BCP' in href:
                            print(f"  BCP-related: {href} - {text}")
                        else:
                            print(f"  Other: {href} - {text}")
                        
                else:
                    print(f"Failed to fetch: {resp.status}")
                    
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_cse_bcp())
