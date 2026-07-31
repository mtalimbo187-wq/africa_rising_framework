"""Pexels API integration for stock footage and images"""

import os
import requests
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class PexelsClient:
    """Pexels API client for discovering stock media"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PEXELS_API_KEY")
        self.base_url = "https://api.pexels.com/v1"
        self.headers = {"Authorization": self.api_key}

    def search_videos(
        self,
        query: str,
        per_page: int = 5,
        min_duration: int = 5,
        max_duration: int = 60,
    ) -> Dict[str, Any]:
        """Search for stock videos"""
        logger.info(f"Searching videos: {query}")

        params = {
            "query": query,
            "per_page": per_page,
            "min_duration": min_duration,
            "max_duration": max_duration,
        }

        try:
            response = requests.get(
                f"{self.base_url}/videos/search",
                headers=self.headers,
                params=params,
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            videos = []

            for video in data.get("videos", []):
                video_files = video.get("video_files", [])
                if video_files:
                    # Get highest quality available
                    best_file = max(
                        video_files,
                        key=lambda f: f.get("width", 0) * f.get("height", 0),
                    )

                    videos.append(
                        {
                            "id": video.get("id"),
                            "title": video.get("url", "").split("/")[-1],
                            "url": best_file.get("link"),
                            "duration": video.get("duration"),
                            "width": best_file.get("width"),
                            "height": best_file.get("height"),
                            "quality": "HD"
                            if best_file.get("width", 0) >= 1920
                            else "SD",
                            "source": "Pexels",
                        }
                    )

            return {
                "status": "success",
                "query": query,
                "total": len(videos),
                "videos": videos,
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Pexels search error: {e}")
            # Fallback: return mock results
            return {
                "status": "mock",
                "query": query,
                "total": 1,
                "videos": [
                    {
                        "id": f"pexels_{hash(query) % 10000}",
                        "title": f"{query} - Mock",
                        "url": f"https://videos.pexels.com/video-{hash(query) % 10000}/",
                        "duration": 30,
                        "width": 1920,
                        "height": 1080,
                        "quality": "HD",
                        "source": "Pexels Mock",
                    }
                ],
            }

    def search_photos(
        self,
        query: str,
        per_page: int = 10,
        size: str = "large",
    ) -> Dict[str, Any]:
        """Search for stock photos"""
        logger.info(f"Searching photos: {query}")

        params = {
            "query": query,
            "per_page": per_page,
            "size": size,
        }

        try:
            response = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params=params,
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            photos = []

            for photo in data.get("photos", []):
                photos.append(
                    {
                        "id": photo.get("id"),
                        "title": photo.get("alt", "Stock Photo"),
                        "url": photo.get("src", {}).get(size, photo.get("src", {}).get("original")),
                        "width": photo.get("width"),
                        "height": photo.get("height"),
                        "source": "Pexels",
                    }
                )

            return {
                "status": "success",
                "query": query,
                "total": len(photos),
                "photos": photos,
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Pexels photo search error: {e}")
            # Fallback: return mock results
            return {
                "status": "mock",
                "query": query,
                "total": 1,
                "photos": [
                    {
                        "id": f"pexels_photo_{hash(query) % 10000}",
                        "title": f"{query} - Mock Photo",
                        "url": f"https://images.pexels.com/photo-{hash(query) % 10000}/",
                        "width": 5000,
                        "height": 3333,
                        "source": "Pexels Mock",
                    }
                ],
            }
