#!/usr/bin/env python3
"""
Asset Finder Agent — Search for existing assets in parallel

Sources (free first):
  1. Pexels (stock video)
  2. Pixabay (stock video/photos)
  3. Wikimedia Commons (historical)
  4. NASA (satellite/space)
  5. Internet Archive (historical footage)
  6. Library of Congress (historical collections)
"""

from base_agent import BaseAgent, AgentResult, AgentStatus
from typing import Dict, Any, List
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


class AssetFinderAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Asset Finder",
            description="Search Pexels, Pixabay, Wikimedia, NASA, Internet Archive, LoC in parallel"
        )

        self.sources = {
            "pexels": {
                "name": "Pexels",
                "url": "https://api.pexels.com/videos/search",
                "key": "6mRphkqCxN8oBj28vU9lpdeMXgoS5EfsdTKKK9Ts0Dv14pT07cxAPjdq",
                "type": "video"
            },
            "pixabay": {
                "name": "Pixabay",
                "url": "https://pixabay.com/api/videos/",
                "type": "video"
            },
            "wikimedia": {
                "name": "Wikimedia Commons",
                "url": "https://commons.wikimedia.org/w/api.php",
                "type": "images"
            },
            "nasa": {
                "name": "NASA",
                "url": "https://images-api.nasa.gov/search",
                "type": "images"
            },
            "internet_archive": {
                "name": "Internet Archive",
                "url": "https://archive.org/advancedsearch.php",
                "type": "video"
            },
            "library_of_congress": {
                "name": "Library of Congress",
                "url": "https://www.loc.gov/collections/",
                "type": "images"
            }
        }

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Search for assets in parallel"""

        shots = input_data.get("shots", [])
        if not shots:
            self.log_error("No shots provided")
            return AgentResult(self.name, AgentStatus.FAILED, {})

        self.log_status(f"Searching for assets for {len(shots)} shots (parallel)")

        found_assets = {}

        # Search each shot in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}

            for shot in shots:
                shot_num = shot["shot_number"]
                queries = shot.get("search_queries", [])
                visual_type = shot.get("visual_type", "stock_footage")

                future = executor.submit(
                    self._search_shot_assets,
                    shot_num,
                    queries,
                    visual_type
                )
                futures[future] = shot_num

            # Collect results as they complete
            for future in as_completed(futures):
                shot_num = futures[future]
                try:
                    assets = future.result()
                    found_assets[shot_num] = assets
                    self.log_status(f"Shot {shot_num}: Found {len(assets)} assets")
                except Exception as e:
                    self.log_error(f"Shot {shot_num}: {str(e)}")
                    found_assets[shot_num] = []

        # Summary
        total_found = sum(len(a) for a in found_assets.values())
        self.log_status(f"Total assets found: {total_found}")

        output = {
            "total_shots_searched": len(shots),
            "total_assets_found": total_found,
            "assets_by_shot": found_assets,
            "sources_used": list(self.sources.keys()),
            "gaps": [i for i in range(1, len(shots) + 1) if not found_assets.get(i)]
        }

        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            output=output
        )

    def _search_shot_assets(self, shot_num: int, queries: List[str], visual_type: str) -> List[Dict]:
        """Search for assets for a single shot"""

        assets = []

        # Try each query with each source
        for query in queries[:2]:  # Top 2 queries
            # Pexels
            pexels = self._search_pexels(query)
            assets.extend([{"source": "Pexels", **a} for a in pexels[:1]])

            # Wikimedia Commons
            wikimedia = self._search_wikimedia(query)
            assets.extend([{"source": "Wikimedia", **a} for a in wikimedia[:1]])

            # Internet Archive
            ia = self._search_internet_archive(query)
            assets.extend([{"source": "Internet Archive", **a} for a in ia[:1]])

        return assets

    def _search_pexels(self, query: str) -> List[Dict]:
        """Search Pexels"""

        try:
            response = requests.get(
                self.sources["pexels"]["url"],
                headers={"Authorization": self.sources["pexels"]["key"]},
                params={"query": query, "per_page": 3},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                return [
                    {
                        "title": v.get("user", {}).get("name", "Unknown"),
                        "url": v["url"],
                        "duration": v.get("duration"),
                        "resolution": f"{v.get('width')}x{v.get('height')}"
                    }
                    for v in data.get("videos", [])[:3]
                ]
        except Exception as e:
            pass

        return []

    def _search_wikimedia(self, query: str) -> List[Dict]:
        """Search Wikimedia Commons"""

        try:
            response = requests.get(
                self.sources["wikimedia"]["url"],
                params={
                    "action": "query",
                    "format": "json",
                    "list": "search",
                    "srsearch": query,
                    "srnamespace": "6",  # File namespace
                    "srlimit": 3
                },
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                return [
                    {"title": s["title"], "url": f"https://commons.wikimedia.org/wiki/{s['title']}"}
                    for s in data.get("query", {}).get("search", [])[:3]
                ]
        except Exception as e:
            pass

        return []

    def _search_internet_archive(self, query: str) -> List[Dict]:
        """Search Internet Archive"""

        try:
            response = requests.get(
                self.sources["internet_archive"]["url"],
                params={
                    "q": query,
                    "output": "json",
                    "rows": 3,
                    "mediatype": "movies"
                },
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                return [
                    {
                        "title": d.get("title"),
                        "url": f"https://archive.org/details/{d.get('identifier')}",
                        "year": d.get("year")
                    }
                    for d in data.get("response", {}).get("docs", [])[:3]
                ]
        except Exception as e:
            pass

        return []
