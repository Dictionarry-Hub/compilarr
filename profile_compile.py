import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Optional


class QualityMappings:
    RADARR = {
        "Unknown": {
            "id": 0,
            "name": "Unknown",
            "source": "unknown",
            "resolution": 0
        },
        "SDTV": {
            "id": 1,
            "name": "SDTV",
            "source": "tv",
            "resolution": 480
        },
        "DVD": {
            "id": 2,
            "name": "DVD",
            "source": "dvd",
            "resolution": 480
        },
        "WEBDL-1080p": {
            "id": 3,
            "name": "WEBDL-1080p",
            "source": "webdl",
            "resolution": 1080
        },
        "HDTV-720p": {
            "id": 4,
            "name": "HDTV-720p",
            "source": "tv",
            "resolution": 720
        },
        "WEBDL-720p": {
            "id": 5,
            "name": "WEBDL-720p",
            "source": "webdl",
            "resolution": 720
        },
        "Bluray-720p": {
            "id": 6,
            "name": "Bluray-720p",
            "source": "bluray",
            "resolution": 720
        },
        "Bluray-1080p": {
            "id": 7,
            "name": "Bluray-1080p",
            "source": "bluray",
            "resolution": 1080
        },
        "WEBDL-480p": {
            "id": 8,
            "name": "WEBDL-480p",
            "source": "webdl",
            "resolution": 480
        },
        "HDTV-1080p": {
            "id": 9,
            "name": "HDTV-1080p",
            "source": "tv",
            "resolution": 1080
        },
        "Raw-HD": {
            "id": 10,
            "name": "Raw-HD",
            "source": "tv",
            "resolution": 1080
        },
        "WEBRip-480p": {
            "id": 12,
            "name": "WEBRip-480p",
            "source": "webrip",
            "resolution": 480
        },
        "WEBRip-720p": {
            "id": 14,
            "name": "WEBRip-720p",
            "source": "webrip",
            "resolution": 720
        },
        "WEBRip-1080p": {
            "id": 15,
            "name": "WEBRip-1080p",
            "source": "webrip",
            "resolution": 1080
        },
        "HDTV-2160p": {
            "id": 16,
            "name": "HDTV-2160p",
            "source": "tv",
            "resolution": 2160
        },
        "WEBRip-2160p": {
            "id": 17,
            "name": "WEBRip-2160p",
            "source": "webrip",
            "resolution": 2160
        },
        "WEBDL-2160p": {
            "id": 18,
            "name": "WEBDL-2160p",
            "source": "webdl",
            "resolution": 2160
        },
        "Bluray-2160p": {
            "id": 19,
            "name": "Bluray-2160p",
            "source": "bluray",
            "resolution": 2160
        },
        "Bluray-480p": {
            "id": 20,
            "name": "Bluray-480p",
            "source": "bluray",
            "resolution": 480
        },
        "Bluray-576p": {
            "id": 21,
            "name": "Bluray-576p",
            "source": "bluray",
            "resolution": 576
        },
        "BR-DISK": {
            "id": 22,
            "name": "BR-DISK",
            "source": "bluray",
            "resolution": 1080
        },
        "DVD-R": {
            "id": 23,
            "name": "DVD-R",
            "source": "dvd",
            "resolution": 480
        },
        "WORKPRINT": {
            "id": 24,
            "name": "WORKPRINT",
            "source": "workprint",
            "resolution": 0
        },
        "CAM": {
            "id": 25,
            "name": "CAM",
            "source": "cam",
            "resolution": 0
        },
        "TELESYNC": {
            "id": 26,
            "name": "TELESYNC",
            "source": "telesync",
            "resolution": 0
        },
        "TELECINE": {
            "id": 27,
            "name": "TELECINE",
            "source": "telecine",
            "resolution": 0
        },
        "DVDSCR": {
            "id": 28,
            "name": "DVDSCR",
            "source": "dvd",
            "resolution": 480
        },
        "REGIONAL": {
            "id": 29,
            "name": "REGIONAL",
            "source": "dvd",
            "resolution": 480
        },
        "Remux-1080p": {
            "id": 30,
            "name": "Remux-1080p",
            "source": "bluray",
            "resolution": 1080
        },
        "Remux-2160p": {
            "id": 31,
            "name": "Remux-2160p",
            "source": "bluray",
            "resolution": 2160
        }
    }

    SONARR = {
        "Unknown": {
            "id": 0,
            "name": "Unknown",
            "source": "unknown",
            "resolution": 0
        },
        "SDTV": {
            "id": 1,
            "name": "SDTV",
            "source": "television",
            "resolution": 480
        },
        "DVD": {
            "id": 2,
            "name": "DVD",
            "source": "dvd",
            "resolution": 480
        },
        "WEBDL-1080p": {
            "id": 3,
            "name": "WEBDL-1080p",
            "source": "web",
            "resolution": 1080
        },
        "HDTV-720p": {
            "id": 4,
            "name": "HDTV-720p",
            "source": "television",
            "resolution": 720
        },
        "WEBDL-720p": {
            "id": 5,
            "name": "WEBDL-720p",
            "source": "web",
            "resolution": 720
        },
        "Bluray-720p": {
            "id": 6,
            "name": "Bluray-720p",
            "source": "bluray",
            "resolution": 720
        },
        "Bluray-1080p": {
            "id": 7,
            "name": "Bluray-1080p",
            "source": "bluray",
            "resolution": 1080
        },
        "WEBDL-480p": {
            "id": 8,
            "name": "WEBDL-480p",
            "source": "web",
            "resolution": 480
        },
        "HDTV-1080p": {
            "id": 9,
            "name": "HDTV-1080p",
            "source": "television",
            "resolution": 1080
        },
        "Raw-HD": {
            "id": 10,
            "name": "Raw-HD",
            "source": "televisionRaw",
            "resolution": 1080
        },
        "WEBRip-480p": {
            "id": 12,
            "name": "WEBRip-480p",
            "source": "webRip",
            "resolution": 480
        },
        "Bluray-480p": {
            "id": 13,
            "name": "Bluray-480p",
            "source": "bluray",
            "resolution": 480
        },
        "WEBRip-720p": {
            "id": 14,
            "name": "WEBRip-720p",
            "source": "webRip",
            "resolution": 720
        },
        "WEBRip-1080p": {
            "id": 15,
            "name": "WEBRip-1080p",
            "source": "webRip",
            "resolution": 1080
        },
        "HDTV-2160p": {
            "id": 16,
            "name": "HDTV-2160p",
            "source": "television",
            "resolution": 2160
        },
        "WEBRip-2160p": {
            "id": 17,
            "name": "WEBRip-2160p",
            "source": "webRip",
            "resolution": 2160
        },
        "WEBDL-2160p": {
            "id": 18,
            "name": "WEBDL-2160p",
            "source": "web",
            "resolution": 2160
        },
        "Bluray-2160p": {
            "id": 19,
            "name": "Bluray-2160p",
            "source": "bluray",
            "resolution": 2160
        },
        "Bluray-1080p Remux": {
            "id": 20,
            "name": "Bluray-1080p Remux",
            "source": "blurayRaw",
            "resolution": 1080
        },
        "Bluray-2160p Remux": {
            "id": 21,
            "name": "Bluray-2160p Remux",
            "source": "blurayRaw",
            "resolution": 2160
        },
        "Bluray-576p": {
            "id": 22,
            "name": "Bluray-576p",
            "source": "bluray",
            "resolution": 576
        }
    }


class LanguageMappings:
    """Basic language mappings with only 'any' defined"""
    COMMON = {
        'any': {
            'id': -1,
            'name': 'Any'
        }
        # Other languages to be added later
    }


class ProfileConverter:

    def __init__(self, target_app: str):
        self.target_app = target_app
        self.quality_mappings = QualityMappings.RADARR if target_app == "Radarr" else QualityMappings.SONARR

    def _convert_group_id(self, group_id: int) -> int:
        """Convert negative group IDs to 1000+ numbers"""
        if group_id < 0:
            return 1000 + abs(group_id)
        return group_id

    def _create_all_qualities(self,
                              allowed_qualities: List[str]) -> List[Dict]:
        """Create a list of all possible qualities, marking specified ones as allowed"""
        qualities = []

        # Sort qualities so allowed ones come after non-allowed ones
        for quality_name, quality_data in sorted(
                self.quality_mappings.items()):
            qualities.append({
                "quality": quality_data.copy(),
                "items": [],
                "allowed": quality_name in allowed_qualities
            })

        return qualities

    def convert_quality_group(self, group: Dict) -> Dict:
        """Convert a quality group from Profilarr format to target app format"""
        # Get original group ID and convert if negative
        original_id = group.get("id", 0)
        converted_id = self._convert_group_id(original_id)

        # Get list of quality names that should be allowed
        allowed_qualities = [
            q.get("name") for q in group.get("qualities", [])
            if q.get("name") in self.quality_mappings
        ]

        converted_group = {
            "name": group["name"],
            "items": self._create_all_qualities(allowed_qualities),
            "allowed": True,
            "id": converted_id
        }

        return converted_group

    def convert_profile(self, profile: Dict) -> Dict:
        converted_profile = {
            "name": profile["name"],
            "upgradeAllowed": profile.get("upgradesAllowed", True),
            "items": [],
            "formatItems": [],  # This will be filled from custom_formats
            "minFormatScore": profile.get("minCustomFormatScore", 0),
            "cutoffFormatScore": profile.get("upgradeUntilScore", 0),
            "minUpgradeFormatScore": max(1,
                                         profile.get("minScoreIncrement", 1)),
            "language": LanguageMappings.COMMON['any']
        }

        # Keep track of qualities we've already processed
        used_qualities = set()

        # First, process all groups
        for group in profile.get("qualities", []):
            converted_group = {
                "name": group["name"],
                "items": [],
                "allowed": True,
                "id": self._convert_group_id(group.get("id", 0))
            }

            # Add only qualities specified for this group
            for quality in group.get("qualities", []):
                quality_name = quality.get("name")
                if quality_name in self.quality_mappings:
                    converted_group["items"].append({
                        "quality":
                        self.quality_mappings[quality_name],
                        "items": [],
                        "allowed":
                        True
                    })
                    used_qualities.add(quality_name)

            if converted_group["items"]:
                converted_profile["items"].append(converted_group)

        # Process standalone qualities
        for quality in profile.get("qualities", []):
            quality_name = quality.get("name")
            if quality_name in self.quality_mappings and quality_name not in used_qualities:
                converted_profile["items"].append({
                    "quality":
                    self.quality_mappings[quality_name],
                    "items": [],
                    "allowed":
                    True
                })
                used_qualities.add(quality_name)

        # Add remaining qualities as individual disabled items
        for quality_name, quality_data in self.quality_mappings.items():
            if quality_name not in used_qualities:
                converted_profile["items"].append({
                    "quality": quality_data,
                    "items": [],
                    "allowed": False
                })

        # Handle cutoff...
        if "upgrade_until" in profile and "id" in profile["upgrade_until"]:
            cutoff_id = self._convert_group_id(profile["upgrade_until"]["id"])
            converted_profile["cutoff"] = cutoff_id
        elif converted_profile["items"]:
            converted_profile["cutoff"] = max(
                item.get("id", 0) for item in converted_profile["items"]
                if "id" in item  # Only consider items that have IDs (groups)
            )

        # Process custom formats
        for cf in profile.get("custom_formats", []):
            format_item = {
                "format":
                len(converted_profile["formatItems"]) + 1,  # Sequential ID
                "name": cf["name"],
                "score": cf["score"]
            }
            converted_profile["formatItems"].append(format_item)

        # Reverse the items list
        converted_profile["items"].reverse()

        return converted_profile


def process_profile(input_path: Path, output_path: Path, target_app: str):
    """Process a single profile file"""
    # Read input profile
    with input_path.open('r') as f:
        profile_data = yaml.safe_load(f)

    # Convert profile
    converter = ProfileConverter(target_app)
    converted_profile = converter.convert_profile(profile_data)

    # Write output
    with output_path.open('w') as f:
        json.dump([converted_profile], f, indent=2)

    print(f"Converted profile saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert Profilarr profiles to Radarr/Sonarr format')
    parser.add_argument('input', type=Path, help='Input profile YAML file')
    parser.add_argument('output', type=Path, help='Output JSON file')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-r',
                       '--radarr',
                       action='store_true',
                       help='Convert for Radarr')
    group.add_argument('-s',
                       '--sonarr',
                       action='store_true',
                       help='Convert for Sonarr')

    args = parser.parse_args()

    # Get target app from args
    target_app = "Radarr" if args.radarr else "Sonarr"

    # Create output directory if it doesn't exist
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Process the profile - using target_app instead of args.target
    process_profile(args.input, args.output, target_app)


if __name__ == '__main__':
    main()
