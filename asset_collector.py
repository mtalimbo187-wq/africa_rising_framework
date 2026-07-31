#!/usr/bin/env python3
"""
Africa Rising Video Framework — Asset Collector

Finds and collects assets for video production:
- Stock footage (Pexels, Unsplash, Pixabay)
- Historical archives (Internet Archive, Google Arts)
- Satellite imagery (Google Earth, Bing Maps)
- Maps and location data
- News footage and clips
"""

import requests
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

class AssetCollector:
    def __init__(self):
        self.cache_dir = Path("/Users/rajab/africa_rising_framework/cache/assets")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # API Keys (from environment or stored)
        self.pexels_key = "6mRphkqCxN8oBj28vU9lpdeMXgoS5EfsdTKKK9Ts0Dv14pT07cxAPjdq"
        self.unsplash_key = None  # Can be added if needed

        self.sources = {
            "pexels": {
                "name": "Pexels",
                "type": "stock_footage",
                "url": "https://www.pexels.com",
                "api": "https://api.pexels.com/videos/search"
            },
            "internet_archive": {
                "name": "Internet Archive",
                "type": "archive",
                "url": "https://archive.org",
                "api": "https://archive.org/advancedsearch.php"
            },
            "google_arts": {
                "name": "Google Arts & Culture",
                "type": "archive",
                "url": "https://artsandculture.google.com"
            },
            "unsplash": {
                "name": "Unsplash",
                "type": "stock_photos",
                "url": "https://unsplash.com",
                "api": "https://api.unsplash.com/search/photos"
            },
            "pixabay": {
                "name": "Pixabay",
                "type": "stock_footage",
                "url": "https://pixabay.com"
            }
        }

    def collect_for_shot(self, query: str, visual_type: str, shot_number: int) -> Dict[str, Any]:
        """Collect assets for a single shot"""

        result = {
            "shot_number": shot_number,
            "query": query,
            "visual_type": visual_type,
            "timestamp": datetime.now().isoformat(),
            "assets_found": [],
            "recommendation": None
        }

        # Try Pexels for stock footage
        if visual_type in ["stock_footage", "stock_photos"]:
            pexels_results = self._search_pexels(query)
            result["assets_found"].extend(pexels_results)

        # Try Internet Archive for historical content
        if visual_type == "archive":
            archive_results = self._search_internet_archive(query)
            result["assets_found"].extend(archive_results)

        # Recommend best option
        if result["assets_found"]:
            result["recommendation"] = result["assets_found"][0]

        return result

    def _search_pexels(self, query: str) -> List[Dict]:
        """Search Pexels for stock footage"""
        assets = []

        try:
            response = requests.get(
                self.sources["pexels"]["api"],
                headers={"Authorization": self.pexels_key},
                params={"query": query, "per_page": 5},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                for video in data.get("videos", [])[:3]:  # Top 3 results
                    asset = {
                        "source": "Pexels",
                        "title": video.get("user", {}).get("name", "Unknown"),
                        "url": video["url"],
                        "video_files": [
                            {
                                "quality": f["quality"],
                                "url": f["link"]
                            }
                            for f in video.get("video_files", [])[:2]  # 720p + 1080p
                        ],
                        "duration": video.get("duration"),
                        "width": video.get("width"),
                        "height": video.get("height")
                    }
                    assets.append(asset)
        except Exception as e:
            print(f"⚠️ Pexels search error: {e}")

        return assets

    def _search_internet_archive(self, query: str) -> List[Dict]:
        """Search Internet Archive for historical content"""
        assets = []

        try:
            # Search for media items
            params = {
                "q": query,
                "output": "json",
                "rows": 5,
                "mediatype": "movies"
            }

            response = requests.get(
                self.sources["internet_archive"]["api"],
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                for doc in data.get("response", {}).get("docs", [])[:3]:
                    asset = {
                        "source": "Internet Archive",
                        "title": doc.get("title", "Unknown"),
                        "identifier": doc.get("identifier"),
                        "url": f"https://archive.org/details/{doc.get('identifier')}",
                        "year": doc.get("year"),
                        "description": doc.get("description", ""),
                        "collection": doc.get("collection", [])
                    }
                    assets.append(asset)
        except Exception as e:
            print(f"⚠️ Internet Archive search error: {e}")

        return assets

    def collect_batch(self, shots: List[Dict]) -> Dict[str, Any]:
        """Collect assets for all shots in a script"""

        print("\n" + "="*80)
        print("🔍 COLLECTING ASSETS")
        print("="*80 + "\n")

        results = {
            "timestamp": datetime.now().isoformat(),
            "total_shots": len(shots),
            "shots": []
        }

        for shot in shots:
            print(f"Shot {shot['shot_number']}: {shot['text'][:60]}...")
            queries = shot.get("search_queries", [])
            visuals = shot.get("visual_types", [])

            shot_assets = {
                "shot_number": shot["shot_number"],
                "assets_by_type": {}
            }

            for visual_type in visuals:
                shot_assets["assets_by_type"][visual_type] = []

                # Use first query for this visual type
                if queries:
                    query = queries[0]
                    print(f"  → {visual_type}: searching '{query}'...")

                    asset_result = self.collect_for_shot(query, visual_type, shot["shot_number"])
                    shot_assets["assets_by_type"][visual_type] = asset_result

            results["shots"].append(shot_assets)

        # Save results
        output_file = self.cache_dir / "collected_assets.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n✅ Assets collected and saved to {output_file}\n")
        return results


def main():
    """Example usage"""
    from script_analyzer import ScriptAnalyzer

    # Analyze script first
    sample_script = """
    Facebook content moderators in Africa earn just two dollars an hour.
    In the United States, the same work pays twenty dollars.
    """

    analyzer = ScriptAnalyzer()
    analysis = analyzer.analyze(sample_script)

    # Collect assets for analyzed shots
    collector = AssetCollector()
    assets = collector.collect_batch(analysis["shots"])

    print(f"Collected assets for {assets['total_shots']} shots")


if __name__ == "__main__":
    main()
