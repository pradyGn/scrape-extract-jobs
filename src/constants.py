import sys
sys.path.append('./')

import torch


############################
##### SCRAPER CONSTANTS ####
############################


SCRAPER_INFO_FILE_PATH = "./data/input/maalaang.csv"
SCRAPER_SAVE_FOLDER_PATH = f"./data/scraped/"
SCRAPER_BROWSER = "chromium"


##############################
##### EXTRACTOR CONSTANTS ####
##############################

# MODEL
# TUNED_MODEL = "./models/maalaang/Llama-3.2-1B_DoRA_True_html-extractor_v1-2-maalaang/checkpoint-1950"
TUNED_MODEL = "Jiraya/crispjobs-com-HTJ-1B-adapters"
HF_MODEL = "meta-llama/Llama-3.2-1B"
DEVICE_MAP = "auto"
LOW_CPU_MEM_USAGE = True
RETURN_DICT = True
TORCH_DTYPE = torch.float16
MAX_NEW_TOKENS = 2_500
TEMPERATURE = 0.5
EXTRACTOR_BUFFER = 1_000

# TOKENIZER
TRUST_REMOTE_CODE = True
PADDING_SIDE = 'left'


EXTRACTOR_CHECK = {
    "apple":"/en-us/details/",
    "amazon":"/en/jobs/2949643/",
    "adobe":"https://careers.adobe.com/us/en/job/",
    "airbnb":"https://careers.airbnb.com/positions/",
    "google":"jobs/results/",
    "meta":"/jobs/",
    "notion":"https://job-boards.greenhouse.io/notion/jobs/",
    "lyft":"https://app.careerpuck.com/job-board/lyft/job/"
}


EXTACTED_FOLDER_PATH = "./data/extracted/"
OLD_EXTRACT_DF_PATH = "./data/frontend_exposed_data/2024-11-10/27andyp_job_data.csv"
EXTRACTOR_PROMPT = """### Instruction:
I am providing you with an HTML. I want you to extract Job Title, Job Location, Job ID and Job Link in a JSON format. I want you to respond only with a JSON, no descriptive text. There are exactly 10 Job Title, Job Location, Job ID and Job Link that you have to extract from the provided HTML.

Again, only respond with a JSON and no desciptive text. If you do not spot job links in the HTML provided then just return an empty JSON.
Here is the HTML I want to extract Job Title, Job Location, Job ID and Job Link from,

{}
"""



########################
#### POST CONSTANTS ####
########################


POST_START_TXT = "### Response:\n"
POST_END_TXT = "<|end_of_text|>"

LINK_PREPEND = {
    'amazon':'https://www.amazon.jobs/',
    'apple':'https://jobs.apple.com/',
    'google':'https://www.google.com/about/careers/applications/',
    'meta':"https://www.metacareers.com/"
}

FRONTEND_DATA_PATH = "./data/extracted_data/"

MASTER_DF_FILE_NAME = "extract.parquet"
OLD_JOB_DATABASE_FILE_NAME = "job_database.parquet"

UNITED_STATES_LIST = ["united", "states", "america", "usa", "us"]
COUNTRY_SET = {'afghanistan',
 'albania',
 'algeria',
 'andorra',
 'angola',
 'antigua and barbuda',
 'argentina',
 'armenia',
 'australia',
 'austria',
 'azerbaijan',
 'bahrain',
 'bangladesh',
 'barbados',
 'belarus',
 'belgium',
 'belize',
 'benin',
 'bhutan',
 'bolivia',
 'bosnia and herzegovina',
 'botswana',
 'brazil',
 'brunei',
 'bulgaria',
 'burkina faso',
 'burundi',
 'cabo verde',
 'cambodia',
 'cameroon',
 'canada',
 'central african republic',
 'chad',
 'chile',
 'china',
 'colombia',
 'comoros',
 'congo, democratic republic of the',
 'congo, republic of the',
 'costa rica',
 'croatia',
 'cuba',
 'cyprus',
 'czech republic',
 'côte d’ivoire',
 'denmark',
 'djibouti',
 'dominica',
 'dominican republic',
 'east timor (timor-leste)',
 'ecuador',
 'egypt',
 'el salvador',
 'equatorial guinea',
 'eritrea',
 'estonia',
 'eswatini',
 'ethiopia',
 'fiji',
 'finland',
 'france',
 'gabon',
 'georgia',
 'germany',
 'ghana',
 'greece',
 'grenada',
 'guatemala',
 'guinea',
 'guinea-bissau',
 'guyana',
 'haiti',
 'honduras',
 'hungary',
 'iceland',
 'india',
 'indonesia',
 'iran',
 'iraq',
 'ireland',
 'israel',
 'italy',
 'jamaica',
 'japan',
 'jordan',
 'kazakhstan',
 'kenya',
 'kiribati',
 'korea, north',
 'korea, south',
 'kosovo',
 'kuwait',
 'kyrgyzstan',
 'laos',
 'latvia',
 'lebanon',
 'lesotho',
 'liberia',
 'libya',
 'liechtenstein',
 'lithuania',
 'luxembourg',
 'madagascar',
 'malawi',
 'malaysia',
 'maldives',
 'mali',
 'malta',
 'marshall islands',
 'mauritania',
 'mauritius',
 'mexico',
 'micronesia, federated states of',
 'moldova',
 'monaco',
 'mongolia',
 'montenegro',
 'morocco',
 'mozambique',
 'myanmar (burma)',
 'namibia',
 'nauru',
 'nepal',
 'netherlands',
 'new zealand',
 'nicaragua',
 'niger',
 'nigeria',
 'north macedonia',
 'norway',
 'oman',
 'pakistan',
 'palau',
 'panama',
 'papua new guinea',
 'paraguay',
 'peru',
 'philippines',
 'poland',
 'portugal',
 'qatar',
 'romania',
 'russia',
 'rwanda',
 'saint kitts and nevis',
 'saint lucia',
 'saint vincent and the grenadines',
 'samoa',
 'san marino',
 'sao tome and principe',
 'saudi arabia',
 'senegal',
 'serbia',
 'seychelles',
 'sierra leone',
 'singapore',
 'slovakia',
 'slovenia',
 'solomon islands',
 'somalia',
 'south africa',
 'spain',
 'sri lanka',
 'sudan',
 'sudan, south',
 'suriname',
 'sweden',
 'switzerland',
 'syria',
 'taiwan',
 'tajikistan',
 'tanzania',
 'thailand',
 'the bahamas',
 'the gambia',
 'togo',
 'tonga',
 'trinidad and tobago',
 'tunisia',
 'turkey',
 'turkmenistan',
 'tuvalu',
 'uganda',
 'ukraine',
 'united arab emirates',
 'united kingdom',
 'uruguay',
 'uzbekistan',
 'vanuatu',
 'vatican city',
 'venezuela',
 'vietnam',
 'yemen',
 'zambia',
 'zimbabwe'}