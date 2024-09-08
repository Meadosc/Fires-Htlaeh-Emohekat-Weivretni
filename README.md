# S.H. Takehome Interview
Fires Htlaeh Emohekat Weivretni

## Setup Instructions
This repo was developed on Python 3.9.2. It has a single external dependency (ijson). To setup and run the code, follow the instructions below:

On your system, install python 3.9+. Other versions of Python 3 will likely work, but if you encounter any unexpected errors then switch to Python 3.9.2.

Then, in a terminal:
```
git pull <repo>
```

At this point, you need to download the [source data](https://antm-pt-prod-dataz-nogbd-nophi-us-east1.s3.amazonaws.com/anthem/2024-09-01_anthem_index.json.gz).

Once the source data is downloaded, move it into the `src/data/` directory. Do not decompress the data; the code is expecting gz data.

Then:
```
cd <repo>
source .venv/bin/activate
pip install -r requirements.txt
cd src/
python -b main.py
```

The code should run for ~2.5 minutes, and then write a file with the urls in `src/data/output.json`.



## Discussion

### Overview

My solution reads a compressed file through a stream. This limits the amount of in-memory data to a manageable amount and avoids storing the entirety of the decompressed data. 

I ignore most fields in the index and focus on the `In Network Files` in the `Reporting Structure Object`. 

I iterate through all the urls and pattern match meaningful substrings to find the URLs corresponding to Anthem's PPO in NY. I look for `.s3.amazonaws.com/anthem/NY`, which matches to URLs stored on s3 correspoding to New York, and I look for `254_39B0`, which seems to be an internal code for New York used by several Anthem provider domains. 

I also look for `vision` and `_anthem-dental_in-network-rates`, which find Anthem's national vision and dental plans, respectively (there are two other possible dental plans that will be discussed below). 

Finally, I handle outliers, which were manually investigated to find reasonable matches for New York.

I will discuss this process in more detail below.

### Reading Compressed Data

The first hurdle to investigating the data is accessing it in memory. I use the built in library `gzip` and external library `ijson` to accomplish this. It allows me to process small chunks of data without having to access the whole, and using the `gzip` library allows me to skip decompressing the data before processing. This is useful if I want to read directly from the source or if I want to avoid storing a larger dataset, though I'm not sure if it is more or less performant than decompressing entirely and then reading. In a robust production process, this would be investigated and the most performant option would be used.

I also assume that the data will only be iterated  through once. If the data were to be iterated through multiple times, a single decompression step before processing would likely be optimal.

### The Index

The index file contains data that is not used during processing, or was only used to investigate the nature of certain urls or url patterns. on the top level, only the 'reporitng_structure' array was interesting, with the other fields containing metadata that is not useful for this project. 

The Reporting Structure Objects, which are in the `reporting_structure` array, have three fields: `reporting_plans`, `in_network_files`, and `allowed_amount_file`. Of those three, only `in_network_files` is used, as it contains the desired urls, whereas `reporting_plans` contains useful data for verifying assumptions and investigating url patterns, and `allowed_amount_file` contains data that is not needed for this project.

Within the `in_network_files`, I found the `description` field to be mostly useless. It's pattern changed depending on the file, and any interesting data tended to tell me that the urls belonged to a company that had been acquired by Anthem, such as Highmark. The `location` field is where the machine readable urls are found.

### The URLs

This is the interesting part. During my analysis of the urls, I noticed that the bulk of the data followed two patterns:
```
"https://antm-pt-prod-dataz-nogbd-nophi-us-east1.s3.amazonaws.com/anthem/NY_HYLZMED0000.json.gz"
"https://anthembcbsin.mrf.bcbs.com/2024-09_254_39B0_in-network-rates_1_of_10.json.gz..." # presigned url omitted for readability
```
The first url, hosted on s3, has a clear marker for New York; NY is in the string, and upon investigation of related EINs it seemed to clearly belong to a New York provider.

The second url pattern was less obvious, but after searching through several EINs I found that `254_39B0` appears to be a code for New York. New York is an odd outlier, as well, because other states still have their two letter abbreviation in the url string. Exceptions are flags for further investigation, but in order to stay within time constraints I chose to accept this as an answer, and filtered for the code. Given more time, I'd like to investigate why New York is treated differently.

I then had to deal with outliers. There are 4 urls that are used for vision and dental.
```
"https://antm-pt-prod-dataz-nogbd-nophi-us-east1.s3.amazonaws.com/anthem/2024-09-01_anthem-vision_in-network-rates.json.gz"
"https://antm-pt-prod-dataz-nogbd-nophi-us-east1.s3.amazonaws.com/anthem/2024-09-01_anthem-dental_in-network-rates.json.gz"
"https://antm-pt-prod-dataz-nogbd-nophi-us-east1.s3.amazonaws.com/anthem/2024-09-01_anthem-dental_me_in-network-rates.json.gz"
"https://antm-pt-prod-dataz-nogbd-nophi-us-east1.s3.amazonaws.com/anthem/2024-09-01_anthem-dental_nh_in-network-rates.json.gz"
```
There appears to be a single nationwide vision plan, and three dental plans. The dental plans appear to be for the nation, and then a single file for Maine and a single file for New Hampshire, which is deduced from their two state abbreviation being in the url. I did some searching for why those two stated may be exceptions for the nationwide dental plan, but I couldn't find anything decisive. It seems reasonable to assume New York is under the general dental plan, but I'm less than perfectly confident in this interpretation and would prefer to research more, but I chose to move on to stay within the allotted time.

Finally, there are some strange outliers that I investigated manually. Here are some abbreviated examples:
```
"https://mrf.beaconhealthoptions.com/files/BEACON_CHEVRON-CORPORATION_in-network-rates.zip",
"https://100112941.mrfcentral.com/",
"https://mrf.beaconhealthoptions.com/files/BEACON_SAG-AFTRA-HEALTH-PLAN_in-network-rates.zip",
"https://mrf.beaconhealthoptions.com/files/BEACON_UPS_in-network-rates.zip",
"https://mrf.beaconhealthoptions.com/files/BEACON_SHEETMETAL-WRKRS-LOCAL28_in-network-rates.zip",
"https://mrf.beaconhealthoptions.com/files/BEACON_PACIFIC-GAS-AND-ELECTRIC_in-network-rates.zip",
"https://mrf.beaconhealthoptions.com/files/BEACON_ANTHEM-DBA-UNICARE-COMM_in-network-rates.zip",
"https://mrf.beaconhealthoptions.com/files/BEACON_EMPL-HLTH-PL-SUFF-CTY_in-network-rates.zip"
```
It appears that mrfcentral is a url for Boyd Gaming, which operates out of Nevada, and the other urls are for Beacon, which was acquired by Anthem. Each Beacon url names the organization it is serving, so I investigated each organization and decided if it likely operated in New York or not. I must admit, I'm not sure if this was a reasonable methodology or not, as exceptions seem to be common when looking at healthcare providers. I can safely say that Chevron, UPS, and the good folk of Suffolk County probably operate in New York, but I excluded PG&E and the Commonwealth of Massachussetts, which seems reasonable, but perhaps they have remote employees in NY? Perhaps that doesn't matter? We're reaching the limit of my knowledge on healthcare and the needs of the theoretical customer. I assume this is an area I would need to ramp up on. And of course, given the time constraints, I needed to make a judgement call on the data given the information I had on hand.


## Final Thoughts

I have reasonable confidence in the url parsing done here, but to build confidence I'd like more domain knowledge and further investigation into example results to confirm that the files represent what I believe they do. 

I took several shortcuts and made several assumptions in order to finish the project in a timely manner, and even then I took close to 2 hours. I had to explore several techniques that I have not implemented before, such locally streaming through large files (most providers I've worked with break large files into smaller chunks), and I am unfamiliar with healthcare data. I hope that these one time learning experiences that slowed me down don't negatively reflect on my performance.

This code is not production ready. There is no error handling, no way to recover if a single piece of data is malformed, and no type checking, cleaning, or sanity checks. It also specifically designed for New York, and would need to be rebuilt from almost the ground up to accommodate any other state. The next steps for this code would be to generalize it to any state and add handling for errors and bad data. It would also be nice to have some indication of the code's progress through the file, but that might take many forms depending on the platform it runs on.

I wrote several iterations of code while exploring the data before I finalized and cleaned it up. I left two files in the repo. They are not used in the final program, but they show part of how I programmatically investigated the data and I thought they were worth leaving. They are not written as well or as clean as main.py.
```
src/find_ein.py
src/unique_urls.py
```
