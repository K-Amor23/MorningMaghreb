#!/usr/bin/env python3
"""
Research Trading Data Sources for Moroccan Stocks

This script tests various data sources to find alternatives to Yahoo Finance
for Moroccan stock market data.
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from bs4 import BeautifulSoup
import logging
import re  # Added missing import for re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingDataSourceResearch:
    """Research class for finding alternative trading data sources"""

    def __init__(self):
        self.results = {}
        self.test_tickers = ["ATW", "IAM", "BCP", "BMCE", "CIH"]

    def test_alpha_vantage(self, api_key: str = None) -> Dict:
        """Test Alpha Vantage API for international markets"""
        logger.info("Testing Alpha Vantage API...")

        if not api_key:
            logger.warning("No Alpha Vantage API key provided")
            return {"success": False, "error": "No API key"}

        base_url = "https://www.alphavantage.co/query"
        results = {}

        for ticker in self.test_tickers:
            try:
                params = {
                    "function": "TIME_SERIES_DAILY",
                    "symbol": ticker,
                    "apikey": api_key,
                }

                response = requests.get(base_url, params=params)
                data = response.json()

                if "Error Message" in data:
                    results[ticker] = {"success": False, "error": data["Error Message"]}
                elif "Note" in data:
                    results[ticker] = {
                        "success": False,
                        "error": "API rate limit exceeded",
                    }
                elif "Time Series (Daily)" in data:
                    time_series = data["Time Series (Daily)"]
                    if time_series:
                        latest_date = list(time_series.keys())[0]
                        latest_data = time_series[latest_date]

                        results[ticker] = {
                            "success": True,
                            "latest_price": float(latest_data["4. close"]),
                            "latest_date": latest_date,
                            "data_points": len(time_series),
                        }
                    else:
                        results[ticker] = {"success": False, "error": "No data found"}
                else:
                    results[ticker] = {
                        "success": False,
                        "error": "Unknown response format",
                    }

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                results[ticker] = {"success": False, "error": str(e)}

        success_count = sum(1 for r in results.values() if r["success"])
        self.results["alpha_vantage"] = {
            "results": results,
            "success_rate": success_count / len(results) if results else 0,
        }

        logger.info(f"Alpha Vantage: {success_count}/{len(results)} successful")
        return self.results["alpha_vantage"]

    def test_moroccan_financial_sites(self) -> Dict:
        """Test web scraping from Moroccan financial websites"""
        logger.info("Testing Moroccan financial websites...")

        sites = [
            {
                "name": "Casablanca Bourse",
                "url": "https://www.casablanca-bourse.com/",
                "description": "Official CSE website",
            },
            {
                "name": "Attijariwafa Bank",
                "url": "https://www.attijariwafa.com/",
                "description": "Major Moroccan bank",
            },
            {
                "name": "Maroc Telecom",
                "url": "https://www.iam.ma/",
                "description": "Major Moroccan telecom",
            },
            {
                "name": "Maghreb Securities",
                "url": "https://www.maghrebsecurities.com/",
                "description": "Regional broker",
            },
        ]

        results = {}

        for site in sites:
            try:
                logger.info(f"Testing {site['name']}: {site['url']}")

                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                }

                response = requests.get(site["url"], headers=headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")

                    # Look for stock price information
                    price_elements = soup.find_all(text=re.compile(r"\d+\.?\d*"))

                    results[site["name"]] = {
                        "success": True,
                        "accessible": True,
                        "content_length": len(response.content),
                        "potential_price_data": len(price_elements) > 0,
                        "description": site["description"],
                    }
                else:
                    results[site["name"]] = {
                        "success": False,
                        "accessible": False,
                        "status_code": response.status_code,
                        "error": f"HTTP {response.status_code}",
                    }

                time.sleep(2)  # Be respectful

            except Exception as e:
                results[site["name"]] = {"success": False, "error": str(e)}

        accessible_count = sum(
            1 for r in results.values() if r.get("accessible", False)
        )
        self.results["moroccan_sites"] = {
            "results": results,
            "accessible_rate": accessible_count / len(results) if results else 0,
        }

        logger.info(f"Moroccan sites: {accessible_count}/{len(results)} accessible")
        return self.results["moroccan_sites"]

    def test_quandl_api(self, api_key: str = None) -> Dict:
        """Test Quandl/NASDAQ Data Link API"""
        logger.info("Testing Quandl API...")

        if not api_key:
            logger.warning("No Quandl API key provided")
            return {"success": False, "error": "No API key"}

        base_url = "https://www.quandl.com/api/v3/datasets"
        results = {}

        # Test with some international datasets
        datasets = [
            "OPEC/ORB",  # Oil prices
            "FRED/GDP",  # US GDP
            "WIKI/AAPL",  # Apple stock (example)
        ]

        for dataset in datasets:
            try:
                url = f"{base_url}/{dataset}.json"
                params = {"api_key": api_key}

                response = requests.get(url, params=params)
                data = response.json()

                if "dataset" in data:
                    dataset_info = data["dataset"]
                    results[dataset] = {
                        "success": True,
                        "name": dataset_info.get("name"),
                        "data_points": len(dataset_info.get("data", [])),
                        "latest_date": (
                            dataset_info.get("data", [[]])[0][0]
                            if dataset_info.get("data")
                            else None
                        ),
                    }
                else:
                    results[dataset] = {"success": False, "error": "No dataset found"}

                time.sleep(1)

            except Exception as e:
                results[dataset] = {"success": False, "error": str(e)}

        success_count = sum(1 for r in results.values() if r["success"])
        self.results["quandl"] = {
            "results": results,
            "success_rate": success_count / len(results) if results else 0,
        }

        logger.info(f"Quandl: {success_count}/{len(results)} successful")
        return self.results["quandl"]

    def test_manual_data_sources(self) -> Dict:
        """Research manual data entry sources"""
        logger.info("Researching manual data entry sources...")

        manual_sources = [
            {
                "name": "BVC Official Website",
                "url": "https://www.casablanca-bourse.com/",
                "description": "Official exchange website with daily prices",
                "access_method": "Web scraping",
                "data_frequency": "Daily",
            },
            {
                "name": "Moroccan Financial Newspapers",
                "url": "https://www.lematin.ma/",
                "description": "Financial section with market data",
                "access_method": "Web scraping",
                "data_frequency": "Daily",
            },
            {
                "name": "Broker Websites",
                "url": "Various",
                "description": "Local broker websites with market data",
                "access_method": "Web scraping",
                "data_frequency": "Real-time",
            },
            {
                "name": "Manual Entry System",
                "url": "Internal",
                "description": "Manual data entry interface",
                "access_method": "Manual",
                "data_frequency": "As needed",
            },
        ]

        self.results["manual_sources"] = {
            "sources": manual_sources,
            "recommendation": "Implement web scraping + manual entry fallback",
        }

        logger.info(f"Manual sources: {len(manual_sources)} identified")
        return self.results["manual_sources"]

    def generate_recommendations(self) -> Dict:
        """Generate recommendations based on test results"""
        logger.info("Generating recommendations...")

        recommendations = {
            "immediate_actions": [],
            "short_term": [],
            "long_term": [],
            "fallback_strategy": [],
        }

        # Analyze Alpha Vantage results
        if "alpha_vantage" in self.results:
            av_result = self.results["alpha_vantage"]
            if av_result["success_rate"] > 0.5:
                recommendations["immediate_actions"].append(
                    {
                        "action": "Implement Alpha Vantage API",
                        "reason": f"Good success rate: {av_result['success_rate']:.1%}",
                        "priority": "High",
                    }
                )
            else:
                recommendations["short_term"].append(
                    {
                        "action": "Test Alpha Vantage with different ticker formats",
                        "reason": f"Low success rate: {av_result['success_rate']:.1%}",
                        "priority": "Medium",
                    }
                )

        # Analyze Moroccan sites results
        if "moroccan_sites" in self.results:
            ms_result = self.results["moroccan_sites"]
            if ms_result["accessible_rate"] > 0.5:
                recommendations["immediate_actions"].append(
                    {
                        "action": "Implement web scraping from Moroccan financial sites",
                        "reason": f"Good accessibility: {ms_result['accessible_rate']:.1%}",
                        "priority": "High",
                    }
                )
            else:
                recommendations["short_term"].append(
                    {
                        "action": "Research additional Moroccan financial websites",
                        "reason": f"Low accessibility: {ms_result['accessible_rate']:.1%}",
                        "priority": "Medium",
                    }
                )

        # Manual data entry fallback
        recommendations["fallback_strategy"].append(
            {
                "action": "Implement manual data entry system",
                "reason": "Reliable fallback for critical data",
                "priority": "High",
            }
        )

        # Long-term recommendations
        recommendations["long_term"].extend(
            [
                {
                    "action": "Contact BVC for official data feeds",
                    "reason": "Direct access to official market data",
                    "priority": "Medium",
                },
                {
                    "action": "Partner with local data providers",
                    "reason": "Access to professional-grade data",
                    "priority": "Low",
                },
            ]
        )

        self.results["recommendations"] = recommendations
        return recommendations

    def save_results(self, output_file: str = "trading_data_research_results.json"):
        """Save all research results to file"""
        output_path = Path(output_file)

        # Add metadata
        self.results["metadata"] = {
            "research_date": datetime.now().isoformat(),
            "test_tickers": self.test_tickers,
            "total_sources_tested": len(self.results) - 1,  # Exclude metadata
        }

        with open(output_path, "w") as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"Results saved to: {output_path}")
        return output_path

    def print_summary(self):
        """Print a summary of research results"""
        print("\n" + "=" * 60)
        print("TRADING DATA SOURCE RESEARCH SUMMARY")
        print("=" * 60)

        for source_name, result in self.results.items():
            if source_name == "metadata":
                continue

            print(f"\n📊 {source_name.upper()}:")

            if "success_rate" in result:
                print(f"   Success Rate: {result['success_rate']:.1%}")
            elif "accessible_rate" in result:
                print(f"   Accessibility: {result['accessible_rate']:.1%}")

            if "recommendations" in result:
                print(f"   Recommendation: {result['recommendations']}")

        if "recommendations" in self.results:
            print(f"\n🎯 RECOMMENDATIONS:")
            for category, actions in self.results["recommendations"].items():
                print(f"\n   {category.replace('_', ' ').title()}:")
                for action in actions:
                    print(f"   • {action['action']} ({action['priority']})")


def main():
    """Main research function"""
    print("🔍 Researching Trading Data Sources for Moroccan Stocks")
    print("=" * 60)

    research = TradingDataSourceResearch()

    # Test Alpha Vantage (requires API key)
    alpha_vantage_key = input(
        "Enter Alpha Vantage API key (or press Enter to skip): "
    ).strip()
    if alpha_vantage_key:
        research.test_alpha_vantage(alpha_vantage_key)

    # Test Moroccan financial sites
    research.test_moroccan_financial_sites()

    # Test Quandl (requires API key)
    quandl_key = input("Enter Quandl API key (or press Enter to skip): ").strip()
    if quandl_key:
        research.test_quandl_api(quandl_key)

    # Research manual sources
    research.test_manual_data_sources()

    # Generate recommendations
    research.generate_recommendations()

    # Save results
    output_file = research.save_results()

    # Print summary
    research.print_summary()

    print(f"\n✅ Research complete! Results saved to: {output_file}")


if __name__ == "__main__":
    main()
