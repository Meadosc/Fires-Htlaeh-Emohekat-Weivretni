from datetime import timedelta
import gzip
import json
import itertools
import time

import ijson


def main():
    path = 'data/2024-09-01_anthem_index.json.gz'
    start = time.time()
    with gzip.open(path, 'rb') as f:
        objects = ijson.items(f, 'reporting_structure.item')
        urls = filter_urls(objects)
    write_output(urls)
    print_time_elapsed(start)
    

def filter_urls(objects, limit=None):
    urls = []
    for obj in itertools.islice(objects, limit):
        for tuple in obj['in_network_files']:
            url = tuple['location']
            if common_ny_patterns(url):
                urls = append_unique_url(url, urls)
            elif vision_and_dental(url):
                urls = append_unique_url(url, urls)
            elif outliers(url):
                urls = append_unique_url(url, urls)
    return urls


def common_ny_patterns(url):
    clean_url = url.split('?&', 1)[0]
    if '254_39B0' in clean_url or '.s3.amazonaws.com/anthem/NY' in clean_url:
        return True
    return False


def vision_and_dental(url):
    if 'vision' in url:
        return True
    elif '_anthem-dental_in-network-rates' in url: # exclude ME (Maine) and NH (New Hampshire) dental
        return True
    return False


def outliers(url):
    outlier_substrings_in_ny = [
        'BEACON_CHEVRON-CORPORATION_in-network-rates',
        'BEACON_SAG-AFTRA-HEALTH-PLAN_in-network-rates',
        'BEACON_UPS_in-network-rates',
        'BEACON_SHEETMETAL-WRKRS-LOCAL28_in-network-rates',
        'BEACON_EMPL-HLTH-PL-SUFF-CTY_in-network-rates',
    ]
    for substring in outlier_substrings_in_ny:
        if substring in url:
            return True
    return False


def write_output(urls):
    with open('data/output.json', 'w', encoding='utf-8') as f:
        data = {'urls': urls}
        json.dump(data, f, indent=4)
    

def append_unique_url(url, urls):
    if url not in urls:
        urls.append(url)
    return urls


def print_time_elapsed(start):
    print(f"Time: {str(timedelta(seconds=time.time() - start))}")


if __name__ == '__main__':
    main()
