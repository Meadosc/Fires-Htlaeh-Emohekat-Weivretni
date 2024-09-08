import gzip
import ijson


def find_eins_for_url(url):
    path = 'data/2024-09-01_anthem_index.json.gz'
    with gzip.open(path, 'rb') as f:
        objects = ijson.items(f, 'reporting_structure.item')
        for obj in objects:
            for tuple in obj['in_network_files']:
                if url in tuple['location']:
                    for rp in obj['reporting_plans']:
                        print(f"{rp['plan_id']}, {rp.get('plan_type', None)}, {rp['plan_name']}")
                    print("")
                    return True # cuts off execution to find first matching value


if __name__ == '__main__':
    urls = [
        "https://mrf.beaconhealthoptions.com/files/BEACON_CHEVRON-CORPORATION_in-network-rates.zip",
        "https://100112941.mrfcentral.com/",
        "https://mrf.beaconhealthoptions.com/files/BEACON_SAG-AFTRA-HEALTH-PLAN_in-network-rates.zip",
        "https://mrf.beaconhealthoptions.com/files/BEACON_UPS_in-network-rates.zip",
        "https://mrf.beaconhealthoptions.com/files/BEACON_SHEETMETAL-WRKRS-LOCAL28_in-network-rates.zip",
        "https://mrf.beaconhealthoptions.com/files/BEACON_PACIFIC-GAS-AND-ELECTRIC_in-network-rates.zip",
        "https://mrf.beaconhealthoptions.com/files/BEACON_ANTHEM-DBA-UNICARE-COMM_in-network-rates.zip",
        "https://mrf.beaconhealthoptions.com/files/BEACON_EMPL-HLTH-PL-SUFF-CTY_in-network-rates.zip"
    ]
    
    for url in urls:
        print(f'url: {url}')
        find_eins_for_url(url)
        print('')
