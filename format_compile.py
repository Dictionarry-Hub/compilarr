from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Union
import argparse
import json
import yaml


class TargetApp(Enum):
    RADARR = auto()
    SONARR = auto()


@dataclass
class Specification:
    name: str
    implementation: str
    negate: bool = False
    required: bool = False
    fields: List[Dict[str, str]] = None

    def __post_init__(self):
        if self.fields is None:
            self.fields = []


@dataclass
class CustomFormat:
    name: str
    description: str
    tags: List[str]
    conditions: List[Dict]
    tests: List[Dict]


@dataclass
class ConvertedFormat:
    name: str
    specifications: List[Specification]


class ValueResolver:
    RADARR_INDEXER_FLAGS = {
        'freeleech': 1,
        'halfleech': 2,
        'double_upload': 4,
        'internal': 32,
        'scene': 128,
        'freeleech_75': 256,
        'freeleech_25': 512,
        'nuked': 2048,
        'ptp_golden': 8,
        'ptp_approved': 16
    }

    SONARR_INDEXER_FLAGS = {
        'freeleech': 1,
        'halfleech': 2,
        'double_upload': 4,
        'internal': 8,
        'scene': 16,
        'freeleech_75': 32,
        'freeleech_25': 64,
        'nuked': 128
    }

    RADARR_SOURCES = {
        'cam': 1,
        'telesync': 2,
        'telecine': 3,
        'workprint': 4,
        'dvd': 5,
        'tv': 6,
        'web_dl': 7,
        'webrip': 8,
        'bluray': 9
    }

    SONARR_SOURCES = {
        'television': 1,
        'televisionraw': 2,
        'web_dl': 3,
        'webrip': 4,
        'dvd': 5,
        'bluray': 6,
        'blurayraw': 7
    }

    RESOLUTIONS = {
        '360p': 360,
        '480p': 480,
        '540p': 540,
        '576p': 576,
        '720p': 720,
        '1080p': 1080,
        '2160p': 2160
    }

    @classmethod
    def get_indexer_flag(cls, flag: str, target_app: TargetApp) -> int:
        flags = (cls.RADARR_INDEXER_FLAGS if target_app == TargetApp.RADARR
                 else cls.SONARR_INDEXER_FLAGS)
        return flags.get(flag.lower(), 0)

    @classmethod
    def get_source(cls, source: str, target_app: TargetApp) -> int:
        sources = (cls.RADARR_SOURCES
                   if target_app == TargetApp.RADARR else cls.SONARR_SOURCES)
        return sources.get(source, 0)

    @classmethod
    def get_resolution(cls, resolution: str) -> int:
        return cls.RESOLUTIONS.get(resolution, 0)


class FormatConverter:

    def __init__(self, patterns: Dict[str, str]):
        self.patterns = patterns

    def _create_specification(
            self, condition: Dict,
            target_app: TargetApp) -> Optional[Specification]:
        condition_type = condition['type']

        if condition_type in ['release_title', 'release_group']:
            pattern_name = condition['pattern']
            pattern = self.patterns.get(pattern_name)
            if not pattern:
                return None

            implementation = ('ReleaseTitleSpecification'
                              if condition_type == 'release_title' else
                              'ReleaseGroupSpecification')
            fields = [{'name': 'value', 'value': pattern}]

        elif condition_type == 'source':
            implementation = 'SourceSpecification'
            value = ValueResolver.get_source(condition['source'], target_app)
            fields = [{'name': 'value', 'value': value}]

        elif condition_type == 'resolution':
            implementation = 'ResolutionSpecification'
            value = ValueResolver.get_resolution(condition['resolution'])
            fields = [{'name': 'value', 'value': value}]

        elif condition_type == 'indexer_flag':
            implementation = 'IndexerFlagSpecification'
            value = ValueResolver.get_indexer_flag(condition.get('flag', ''),
                                                   target_app)
            fields = [{'name': 'value', 'value': value}]

        else:
            return None

        return Specification(name=condition.get('name', ''),
                             implementation=implementation,
                             negate=condition.get('negate', False),
                             required=condition.get('required', False),
                             fields=fields)

    def convert_format(self, custom_format: CustomFormat,
                       target_app: TargetApp) -> ConvertedFormat:
        specifications = []

        for condition in custom_format.conditions:
            spec = self._create_specification(condition, target_app)
            if spec:
                specifications.append(spec)

        return ConvertedFormat(name=custom_format.name,
                               specifications=specifications)


class FormatProcessor:

    def __init__(self, input_dir: Path, output_dir: Path, patterns_dir: Path):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.patterns = self._load_patterns(patterns_dir)
        self.converter = FormatConverter(self.patterns)

    @staticmethod
    def _load_patterns(patterns_dir: Path) -> Dict[str, str]:
        patterns = {}
        for file_path in patterns_dir.glob('*.yml'):
            with file_path.open('r') as f:
                pattern_data = yaml.safe_load(f)
                patterns[pattern_data['name']] = pattern_data['pattern']
        return patterns

    def _load_custom_format(self, format_name: str) -> Optional[CustomFormat]:
        format_path = self.input_dir / f"{format_name}.yml"
        if not format_path.exists():
            print(f"Error: Custom format file not found: {format_path}")
            return None

        with format_path.open('r') as f:
            data = yaml.safe_load(f)
            return CustomFormat(**data)

    def process_format(self,
                       format_name: str,
                       target_app: TargetApp,
                       return_data: bool = False) -> Optional[ConvertedFormat]:
        custom_format = self._load_custom_format(format_name)
        if not custom_format:
            return None

        print(f"\nProcessing: {format_name}")
        converted_format = self.converter.convert_format(
            custom_format, target_app)

        if return_data:
            return converted_format

        output_data = [{
            'name':
            converted_format.name,
            'specifications':
            [vars(spec) for spec in converted_format.specifications]
        }]

        output_path = self.output_dir / f"{format_name}.json"
        with output_path.open('w') as f:
            json.dump(output_data, f, indent=2)

        print(f"Output generated: {output_path}")
        return converted_format

    def process_all_formats(self,
                            target_app: TargetApp,
                            single_file: bool = False) -> None:
        successful = 0
        failed = 0
        all_formats = []

        for format_path in self.input_dir.glob('*.yml'):
            format_name = format_path.stem
            converted_format = self.process_format(format_name,
                                                   target_app,
                                                   return_data=single_file)

            if converted_format:
                if single_file:
                    all_formats.append({
                        'name':
                        converted_format.name,
                        'specifications': [
                            vars(spec)
                            for spec in converted_format.specifications
                        ]
                    })
                successful += 1
            else:
                failed += 1

        if single_file and all_formats:
            output_path = self.output_dir / f"{target_app.name.lower()}_custom_formats.json"
            with output_path.open('w') as f:
                json.dump(all_formats, f, indent=2)
            print(f"\nCombined output generated: {output_path}")

        print(f"\nProcessing complete!")
        print(f"Successfully processed: {successful} format(s)")
        if failed > 0:
            print(f"Failed to process: {failed} format(s)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=
        'Convert custom format files between Profilarr and Radarr/Sonarr formats'
    )
    parser.add_argument(
        'format_name',
        nargs='?',
        help=
        'Name of the custom format file (without .yml extension). If omitted, processes all formats.'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-r',
                       '--radarr',
                       action='store_true',
                       help='Convert for Radarr')
    group.add_argument('-s',
                       '--sonarr',
                       action='store_true',
                       help='Convert for Sonarr')
    parser.add_argument(
        '--input-dir',
        type=Path,
        default=Path('custom_formats'),
        help=
        'Directory containing input custom format files (default: custom_formats)'
    )
    parser.add_argument('--output-dir',
                        type=Path,
                        default=Path('output'),
                        help='Directory for output files (default: output)')
    parser.add_argument(
        '--patterns-dir',
        type=Path,
        default=Path('regex_patterns'),
        help=
        'Directory containing regex pattern files (default: regex_patterns)')
    parser.add_argument(
        '--single-file',
        action='store_true',
        help=
        'Output all formats to a single JSON file instead of separate files')
    return parser.parse_args()


def main():
    args = parse_args()
    target_app = TargetApp.RADARR if args.radarr else TargetApp.SONARR

    args.output_dir.mkdir(exist_ok=True)

    processor = FormatProcessor(args.input_dir, args.output_dir,
                                args.patterns_dir)

    if args.format_name:
        processor.process_format(args.format_name, target_app,
                                 args.single_file)
    else:
        processor.process_all_formats(target_app, args.single_file)


if __name__ == '__main__':
    main()
