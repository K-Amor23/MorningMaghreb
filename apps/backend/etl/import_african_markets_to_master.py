#!/usr/bin/env python3
"""
Import African Markets companies into the master `companies` table and a snapshot into `market_data`.

Usage:
  - Requires env vars:
      NEXT_PUBLIC_SUPABASE_URL
      SUPABASE_SERVICE_ROLE_KEY
  - Reads data from apps/backend/data/cse_companies_african_markets_database.json
    If the file does not exist, optionally run the scraper beforehand.
"""

from __future__ import annotations

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Supabase client not installed. Install with: pip install supabase")
    raise


DATA_FILE = Path("apps/backend/data/cse_companies_african_markets_database.json")


def _map_company_to_master(company: Dict[str, Any]) -> Dict[str, Any]:
    """Map African Markets company dict to master `companies` row."""
    return {
        'ticker': company.get('ticker', '').upper(),
        'name': company.get('name', ''),
        'sector': company.get('sector'),
        'industry': company.get('industry'),
        'market_cap': company.get('market_cap_billion', 0),
        'current_price': company.get('price'),
        'price_change': None,  # not provided directly
        'price_change_percent': company.get('change_1d_percent'),
        'pe_ratio': company.get('pe_ratio'),
        'dividend_yield': company.get('dividend_yield'),
        'shares_outstanding': company.get('shares_outstanding'),
        'size_category': company.get('size_category'),
        'sector_group': company.get('sector_group'),
        'exchange': company.get('exchange', 'Casablanca Stock Exchange (BVC)'),
        'country': company.get('country', 'Morocco'),
        'company_url': company.get('company_url'),
        'ir_url': company.get('ir_url'),
        'base_url': company.get('url'),
        'is_active': True,
        'last_updated': company.get('last_updated') or datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
    }


def _map_company_to_market_data(company: Dict[str, Any]) -> Dict[str, Any]:
    """Map to a `market_data` snapshot row."""
    return {
        'ticker': company.get('ticker', '').upper(),
        'price': company.get('price'),
        'volume': company.get('volume'),
        'change_amount': None,
        'change_percent': company.get('change_1d_percent'),
        'high_24h': None,
        'low_24h': None,
        'open_price': None,
        'previous_close': None,
        'timestamp': datetime.now().isoformat(),
        'source': company.get('data_source', 'African Markets BVC'),
    }


def _load_companies_from_file(file_path: Path) -> List[Dict[str, Any]]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        companies = data.get('companies') or data
        if isinstance(companies, dict) and 'companies' in companies:
            companies = companies['companies']
        if not isinstance(companies, list):
            raise ValueError('Unexpected companies payload structure')
        logger.info(f"Loaded {len(companies)} companies from {file_path}")
        return companies
    except Exception as e:
        logger.error(f"Failed to load companies from {file_path}: {e}")
        return []


def _init_supabase() -> Client:
    url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    if not url or not key:
        raise RuntimeError('Supabase env vars missing: require NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY')
    return create_client(url, key)


def upsert_into_master(client: Client, companies: List[Dict[str, Any]]) -> Tuple[int, int, int]:
    """Upsert into `companies` on ticker, and insert market_data snapshot. Returns (new, updated, failed)."""
    new_count = 0
    updated_count = 0
    failed_count = 0

    try:
        existing = client.table('companies').select('ticker').execute()
        existing_tickers = {row['ticker'] for row in (existing.data or [])}
    except Exception as e:
        logger.warning(f"Could not fetch existing companies: {e}")
        existing_tickers = set()

    for company in companies:
        master_row = _map_company_to_master(company)
        ticker = master_row['ticker']
        try:
            # Upsert companies by ticker (unique)
            client.table('companies').upsert(master_row, on_conflict='ticker').execute()
            if ticker in existing_tickers:
                updated_count += 1
            else:
                new_count += 1

            # Insert market_data snapshot (best-effort)
            try:
                client.table('market_data').insert(_map_company_to_market_data(company)).execute()
            except Exception as e:
                logger.debug(f"market_data insert skipped for {ticker}: {e}")

        except Exception as e:
            failed_count += 1
            logger.error(f"Upsert failed for {ticker}: {e}")

    logger.info(f"Master import complete: new={new_count}, updated={updated_count}, failed={failed_count}")
    return new_count, updated_count, failed_count


def import_african_markets_into_supabase(data_file: Path = DATA_FILE) -> Dict[str, Any]:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_file}. Run the scraper first to generate it.")

    companies = _load_companies_from_file(data_file)
    if not companies:
        return {'total_companies': 0, 'new': 0, 'updated': 0, 'failed': 0}

    client = _init_supabase()
    new_count, updated_count, failed_count = upsert_into_master(client, companies)

    return {
        'total_companies': len(companies),
        'new': new_count,
        'updated': updated_count,
        'failed': failed_count,
    }


if __name__ == "__main__":
    results = import_african_markets_into_supabase()
    print(json.dumps(results, indent=2))


