import os
import json
import yaml
import argparse


# Define the data structures
class ProfilarrFormat:

    def __init__(self, name, description, tags, conditions, tests):
        self.name = name
        self.description = description
        self.tags = tags
        self.conditions = conditions
        self.tests = tests


class RadarrFormat:

    def __init__(self, name, specifications):
        self.name = name
        self.specifications = specifications


# Parse the input format
def parse_profilarr_format(data):
    return ProfilarrFormat(data['name'], data['description'], data['tags'],
                           data['conditions'], data['tests'])


# Resolve patterns
def resolve_patterns(conditions, patterns):
    resolved_conditions = []
    for condition in conditions:
        pattern_name = condition['pattern']
        pattern = patterns.get(pattern_name)
        if pattern:
            resolved_condition = condition.copy()
            resolved_condition['pattern'] = pattern
            resolved_conditions.append(resolved_condition)
    return resolved_conditions


# Convert the data
def convert_to_radarr_format(profilarr_data, patterns, target_app):
    specifications = []
    for condition in profilarr_data.conditions:
        if condition['type'] == 'release_title':
            implementation = 'ReleaseTitleSpecification'
            pattern_name = condition['pattern']
            pattern = patterns.get(pattern_name)
            if pattern:
                fields = [{'name': 'value', 'value': pattern}]
            else:
                continue  # Skip if pattern not found
        elif condition['type'] == 'release_group':
            implementation = 'ReleaseGroupSpecification'
            pattern_name = condition['pattern']
            pattern = patterns.get(pattern_name)
            if pattern:
                fields = [{'name': 'value', 'value': pattern}]
            else:
                continue  # Skip if pattern not found
        elif condition['type'] == 'source':
            implementation = 'SourceSpecification'
            value = resolve_source_value(condition['source'], target_app)
            fields = [{'name': 'value', 'value': value}]
        elif condition['type'] == 'resolution':
            implementation = 'ResolutionSpecification'
            value = resolve_resolution_value(condition['resolution'],
                                             target_app)
            fields = [{'name': 'value', 'value': value}]
        elif condition['type'] == 'indexer_flag':
            implementation = 'IndexerFlagSpecification'
            # Check for 'flag' key instead of 'value'
            value = resolve_indexer_flag_value(condition.get('flag', ''),
                                               target_app)
            fields = [{'name': 'value', 'value': value}]
        else:
            continue  # Skip unsupported types

        specification = {
            'name': condition.get('name', ''),  # Use get() with default value
            'implementation': implementation,
            'negate': condition.get('negate',
                                    False),  # Use get() with default value
            'required': condition.get('required',
                                      False),  # Use get() with default value
            'fields': fields
        }
        specifications.append(specification)

    return RadarrFormat(profilarr_data.name, specifications)


def resolve_indexer_flag_value(flag, target_app):
    if target_app == 'radarr':
        radarr_flags = {
            'freeleech': 1,
            'halfleech': 2,
            'double_upload': 4,
            'internal': 32,
            'scene': 128,
            'freeleech_75': 256,
            'freeleech_25': 512,
            'nuked': 2048,
            'ptp_golden': 8,  # Added PTP Golden flag
            'ptp_approved': 16  # Added PTP Approved flag
        }
        return radarr_flags.get(
            flag.lower(),
            0)  # Convert to lowercase and return 0 for unknown flags
    elif target_app == 'sonarr':
        sonarr_flags = {
            'freeleech': 1,
            'halfleech': 2,
            'double_upload': 4,
            'internal': 8,
            'scene': 16,
            'freeleech_75': 32,
            'freeleech_25': 64,
            'nuked': 128
            # Note: PTP flags are Radarr-only
        }
        return sonarr_flags.get(
            flag.lower(),
            0)  # Convert to lowercase and return 0 for unknown flags


def resolve_source_value(source, target_app):
    if target_app == 'radarr':
        radarr_sources = {
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
        return radarr_sources.get(source, 0)  # Return 0 for unknown sources
    elif target_app == 'sonarr':
        sonarr_sources = {
            'television': 1,
            'televisionraw': 2,
            'web_dl': 3,
            'webrip': 4,
            'dvd': 5,
            'bluray': 6,
            'blurayraw': 7
        }
        return sonarr_sources.get(source, 0)  # Return 0 for unknown sources


def resolve_resolution_value(resolution, target_app):
    resolutions = {
        '360p': 360,
        '480p': 480,
        '540p': 540,
        '576p': 576,
        '720p': 720,
        '1080p': 1080,
        '2160p': 2160
    }
    return resolutions.get(resolution, 0)  # Return 0 for unknown resolutions


# Generate the output
def generate_radarr_output(radarr_data):
    output = [{
        'name': radarr_data.name,
        'specifications': radarr_data.specifications
    }]
    return json.dumps(output, indent=2)


def process_single_format(format_name,
                          input_dir,
                          output_dir,
                          patterns_dir,
                          target_app,
                          return_data=False):
    custom_format_file = os.path.join(input_dir, f"{format_name}.yml")

    if not os.path.exists(custom_format_file):
        print(f"Error: Custom format file not found: {custom_format_file}")
        return False if not return_data else None

    print(f"\nProcessing: {format_name}")
    print(f"Custom format file: {custom_format_file}")

    # Read custom format data from input file
    with open(custom_format_file, 'r') as file:
        custom_format_data = yaml.safe_load(file)

    # Parse custom format data
    profilarr_data = parse_profilarr_format(custom_format_data)

    # Convert to target format
    converted_data = convert_to_radarr_format(profilarr_data, patterns,
                                              target_app)

    if return_data:
        return converted_data

    # Generate output JSON
    output_json = generate_radarr_output(converted_data)

    # Write output to file
    output_file = os.path.join(output_dir, f"{profilarr_data.name}.json")
    with open(output_file, 'w') as file:
        file.write(output_json)

    print(f"Output generated: {output_file}")
    return True


def main():
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
        default='custom_formats',
        help=
        'Directory containing input custom format files (default: custom_formats)'
    )
    parser.add_argument('--output-dir',
                        default='output',
                        help='Directory for output files (default: output)')
    parser.add_argument(
        '--patterns-dir',
        default='regex_patterns',
        help=
        'Directory containing regex pattern files (default: regex_patterns)')
    parser.add_argument(
        '--single-file',
        action='store_true',
        help=
        'Output all formats to a single JSON file instead of separate files')

    args = parser.parse_args()

    # Determine target application
    target_app = 'radarr' if args.radarr else 'sonarr'

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Read regex patterns from files
    global patterns
    patterns = {}
    for filename in os.listdir(args.patterns_dir):
        if filename.endswith('.yml'):
            with open(os.path.join(args.patterns_dir, filename), 'r') as file:
                pattern_data = yaml.safe_load(file)
                patterns[pattern_data['name']] = pattern_data['pattern']

    if args.format_name:
        # Process single format
        if args.single_file:
            converted_data = process_single_format(args.format_name,
                                                   args.input_dir,
                                                   args.output_dir,
                                                   args.patterns_dir,
                                                   target_app,
                                                   return_data=True)
            if converted_data:
                output = [{
                    'name': converted_data.name,
                    'specifications': converted_data.specifications
                }]
                output_file = os.path.join(
                    args.output_dir, f"{target_app}_custom_formats.json")
                with open(output_file, 'w') as file:
                    json.dump(output, file, indent=2)
                print(f"\nOutput generated: {output_file}")
        else:
            process_single_format(args.format_name, args.input_dir,
                                  args.output_dir, args.patterns_dir,
                                  target_app)
    else:
        # Process all formats
        print(f"Processing all custom formats in {args.input_dir}")
        successful = 0
        failed = 0
        all_formats = []

        for filename in os.listdir(args.input_dir):
            if filename.endswith('.yml'):
                format_name = os.path.splitext(filename)[0]
                if args.single_file:
                    converted_data = process_single_format(format_name,
                                                           args.input_dir,
                                                           args.output_dir,
                                                           args.patterns_dir,
                                                           target_app,
                                                           return_data=True)
                    if converted_data:
                        all_formats.append({
                            'name':
                            converted_data.name,
                            'specifications':
                            converted_data.specifications
                        })
                        successful += 1
                    else:
                        failed += 1
                else:
                    if process_single_format(format_name, args.input_dir,
                                             args.output_dir,
                                             args.patterns_dir, target_app):
                        successful += 1
                    else:
                        failed += 1

        if args.single_file and all_formats:
            output_file = os.path.join(args.output_dir,
                                       f"{target_app}_custom_formats.json")
            with open(output_file, 'w') as file:
                json.dump(all_formats, file, indent=2)
            print(f"\nCombined output generated: {output_file}")

        print(f"\nProcessing complete!")
        print(f"Successfully processed: {successful} format(s)")
        if failed > 0:
            print(f"Failed to process: {failed} format(s)")


if __name__ == '__main__':
    main()
