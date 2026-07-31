#!/usr/bin/env python3
"""
License Tracking & Attribution System

Track all asset licenses and generate proper attribution/credits.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
from enum import Enum


class LicenseType(str, Enum):
    CC0 = "CC0"
    CC_BY = "CC-BY-4.0"
    CC_BY_SA = "CC-BY-SA-4.0"
    CC_BY_NC = "CC-BY-NC-4.0"
    PROPRIETARY = "proprietary"
    ROYALTY_FREE = "royalty-free"
    PUBLIC_DOMAIN = "public-domain"


class UsageType(str, Enum):
    EDUCATIONAL = "educational"
    COMMERCIAL = "commercial"
    NONPROFIT = "nonprofit"
    DERIVATIVE = "derivative"


class LicenseManager:
    """Track licenses and generate attribution"""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.assets = {}  # asset_id -> asset_info
        self.license_db = self.output_dir / "licenses.json"
        self._load_existing()

    def _load_existing(self):
        """Load existing license database"""
        if self.license_db.exists():
            with open(self.license_db) as f:
                self.assets = json.load(f)

    def track_asset(
        self,
        asset_id: str,
        source: str,
        url: str,
        license_type: LicenseType,
        credited_to: Optional[str] = None,
        attribution_required: bool = False,
        file_path: Optional[str] = None
    ) -> Dict:
        """Track an asset and its license"""

        asset_info = {
            "asset_id": asset_id,
            "source": source,
            "url": url,
            "license": license_type.value,
            "credited_to": credited_to,
            "attribution_required": attribution_required,
            "file_path": file_path,
            "tracked_at": datetime.now().isoformat(),
            "compliance_status": self._check_compliance(license_type)
        }

        self.assets[asset_id] = asset_info
        self._save_db()
        return asset_info

    def _check_compliance(self, license_type: LicenseType) -> str:
        """Check license compliance status"""
        compliance_map = {
            LicenseType.CC0: "full_freedom",
            LicenseType.CC_BY: "requires_attribution",
            LicenseType.CC_BY_SA: "requires_attribution_and_sharealike",
            LicenseType.CC_BY_NC: "noncommercial_only",
            LicenseType.PROPRIETARY: "check_eula",
            LicenseType.ROYALTY_FREE: "no_attribution_needed",
            LicenseType.PUBLIC_DOMAIN: "full_freedom"
        }
        return compliance_map[license_type]

    def validate_for_usage(self, asset_id: str, usage_type: UsageType) -> Tuple[bool, str]:
        """Validate if asset can be used for given purpose"""
        if asset_id not in self.assets:
            return False, f"Asset not tracked: {asset_id}"

        asset = self.assets[asset_id]
        license_type = LicenseType(asset["license"])

        # Check usage restrictions
        if license_type == LicenseType.CC_BY_NC and usage_type == UsageType.COMMERCIAL:
            return False, f"License {license_type.value} prohibits commercial use"

        if license_type == LicenseType.PROPRIETARY:
            return False, f"Proprietary license requires explicit EULA check"

        return True, "Usage allowed"

    def generate_credits_file(self, project_name: str) -> str:
        """Generate credits/attribution file for video description"""
        credits = []
        credits.append(f"## Credits & Attributions\n{project_name}\n")
        credits.append(f"Generated: {datetime.now().strftime('%Y-%m-%d')}\n")

        for asset_id, asset in self.assets.items():
            if asset["attribution_required"]:
                source = asset["source"]
                credited_to = asset["credited_to"] or "Unknown"
                license_type = asset["license"]
                url = asset["url"]

                credit_line = f"- {credited_to}: {source} ({license_type})\n  URL: {url}\n"
                credits.append(credit_line)

        credits.append("\n## License Summary\n")
        license_counts = {}
        for asset in self.assets.values():
            license = asset["license"]
            license_counts[license] = license_counts.get(license, 0) + 1

        for license, count in license_counts.items():
            credits.append(f"- {license}: {count} assets\n")

        return "".join(credits)

    def generate_credits_for_description(self, max_chars: int = 5000) -> str:
        """Generate compact credits for YouTube description (char limit)"""
        credits = []

        by_source = {}
        for asset in self.assets.values():
            if asset["attribution_required"]:
                source = asset["source"]
                credited_to = asset["credited_to"] or "Unknown"
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(credited_to)

        for source, creators in by_source.items():
            creators_str = ", ".join(set(creators))
            line = f"Video: {source} ({creators_str})\n"
            if len("".join(credits)) + len(line) < max_chars:
                credits.append(line)

        return "".join(credits)

    def export_license_report(self, output_file: Optional[str] = None) -> str:
        """Export full license report for legal review"""
        if not output_file:
            output_file = self.output_dir / "LICENSE_REPORT.json"

        report = {
            "project": "Africa Rising",
            "generated": datetime.now().isoformat(),
            "total_assets": len(self.assets),
            "assets": self.assets,
            "summary": {
                "attribution_required": sum(1 for a in self.assets.values() if a["attribution_required"]),
                "royalty_free": sum(1 for a in self.assets.values() if a["license"] == "royalty-free"),
                "cc0": sum(1 for a in self.assets.values() if a["license"] == "CC0"),
                "public_domain": sum(1 for a in self.assets.values() if a["license"] == "public-domain"),
            }
        }

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        return str(output_file)

    def _save_db(self):
        """Persist license database"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.license_db, "w") as f:
            json.dump(self.assets, f, indent=2)

    def list_assets_needing_attribution(self) -> List[Dict]:
        """List all assets that require attribution"""
        return [
            asset for asset in self.assets.values()
            if asset["attribution_required"]
        ]

    def check_license_conflicts(self) -> List[str]:
        """Check for conflicting licenses (e.g., CC-BY-SA requires derivatives also be SA)"""
        issues = []
        sa_assets = [a for a in self.assets.values() if "SA" in a["license"]]

        if sa_assets:
            non_sa_assets = [a for a in self.assets.values() if "SA" not in a["license"]]
            if non_sa_assets:
                issues.append(
                    f"Warning: {len(sa_assets)} CC-BY-SA assets combined with "
                    f"{len(non_sa_assets)} non-SA assets. Output must be CC-BY-SA."
                )

        return issues
