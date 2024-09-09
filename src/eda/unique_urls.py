from datetime import timedelta
import gzip
import ijson
import json
import time


def main():
    start = time.time()
    path = 'data/2024-09-01_anthem_index.json.gz'
    with gzip.open(path, 'rb') as f:
        objects = ijson.items(f, 'reporting_structure.item')
        urls_mrf = []
        urls_dental_vision = []
        urls_s3 = []
        urls_misc = []
        for obj in objects:
            for tuple in obj['in_network_files']:
                # process different url patterns
                url = tuple['location']

                if '.mrf.bcbs.com/' in url:
                    url = url.split('in-network-rates', 1)[0]
                    if url not in urls_mrf:
                        urls_mrf.append(url)
                elif '.s3.amazonaws.com/anthem/' in url:
                    if 'dental' in url or 'vision' in url:
                        if url not in urls_dental_vision:
                            urls_dental_vision.append(url)
                    else:
                        s = '.com/anthem/'
                        idx = url.find(s)
                        url = url[:idx+len(s)+2]
                        if url not in urls_s3:
                            urls_s3.append(url)
                else:
                    if url not in urls_misc:
                        urls_misc.append(url)


    url_lists = {
        'mrf_bcbs': urls_mrf,
        'dental_vision': urls_dental_vision,
        's3': urls_s3,
        'misc': urls_misc,
    }
    for k,v in url_lists.items():
        with open(f'data/unique_urls/{k}.json', 'w', encoding='utf-8') as f:
            data = {'urls': v}
            json.dump(data, f, indent=4)
    
    print(f"Time: {str(timedelta(seconds=time.time() - start))}")


if __name__ == '__main__':
    main()
