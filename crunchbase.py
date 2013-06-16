import requests
import csv
import pandas as pd
from collections import Mapping
from itertools import chain
import ujson as json

API_KEY = json.loads(open('./crunchbase_secrets.json').read())['api_key']

def query_api(url):
    api_key = "?api_key={0}".format(API_KEY)
    url = url+api_key
    try:
        return requests.get(url).json()
    except Exception, e:
        print "Something bad happened: %s" % str(e)
        return {}

same = lambda x:x  # identity function
add = lambda a,b:a+b
_tuple = lambda x:(x,)  # python actually has coercion, avoid it like so

def flattenDict(dictionary, keyReducer=add, keyLift=_tuple, init=()):

    def _flattenIter(pairs, _keyAccum=init):
        atoms = ((k,v) for k,v in pairs if not isinstance(v, Mapping))
        submaps = ((k,v) for k,v in pairs if isinstance(v, Mapping))
        def compress(k):
            return keyReducer(_keyAccum, keyLift(k))
        return chain(
            (
                (compress(k),v) for k,v in atoms
            ),

            *[_flattenIter(submap.items(), compress(k))
                for k,submap in submaps ]
        )
    return dict(_flattenIter(dictionary.items()))

def get_company(company):
    base_url = "http://api.crunchbase.com/v/1/company/{company}.js"
    return query_api(base_url.format(company=company))

def get_investor(vc):
    base_url = "http://api.crunchbase.com/v/1/financial-organization/{vc}.js"
    return query_api(base_url.format(vc=vc))

def parse_investor(vc):
    fields = ['name', 'homepage_url', 'founded_year', 'offices', 'investments']
    data = {k: v for k,v in vc.iteritems() if k in fields}
    return data

def flatten_investments(investor):
    investments = investor.get('investments', [])

    flat_investments = []

    for investment in investments:
        investment = { "_".join(k): v
                        for k,v in flattenDict(investment).iteritems() }
        flat_investments.append(investment)

    investor['investments'] = flat_investments
    return investor

def make_dataframe(investor):
    if len(investor['investments']):
        df = pd.DataFrame(investor['investments'])
    else:
        expected = [u'funding_round_company_image_attribution',
                    u'funding_round_company_image_available_sizes',
                    u'funding_round_company_name',
                    u'funding_round_company_permalink',
                    u'funding_round_funded_day',
                    u'funding_round_funded_month',
                    u'funding_round_funded_year',
                    u'funding_round_raised_amount',
                    u'funding_round_raised_currency_code',
                    u'funding_round_round_code',
                    u'funding_round_source_description',
                    u'funding_round_source_url']

        df = pd.DataFrame({col: [] for col in expected})

    df['investor'] = investor['name']
    return df

def extract_details(investor):
    offices = investor.get('offices', [])

    if len(offices):
        hq = offices[0]
    else:
        hq = {}

    city  = hq.get('city', '')
    state = hq.get('state_code', '')

    name = investor.get('name', '')
    founded = investor.get('founded_year', '')

    return [name, founded, city, state]

with open('./list_of_venture_capital_firms.txt') as f:
    vcs = [ line for line in f.read().split('\n')]

total = len(vcs)
not_found = []
for i, investor in enumerate(vcs):
    print investor
    print '\tget_investor'

    if investor in ('Y Combinator', 'Techstars'):
        vc = get_company(investor)
    else:
        vc = get_investor(investor)

    if len(vc.keys()) == 0 or 'error' in vc.keys():
        print "NOT FOUND"
        not_found.append(investor)
        continue

    print '\tparse_investor'
    vc = parse_investor(vc)

    print '\tflatten_investments'
    vc = flatten_investments(vc)

    print '\tmake_dataframe'
    df = make_dataframe(vc)

    if len(df):
        print '\nwriting dataframe to file'
        keep_cols = [ u'funding_round_company_name',
                      u'funding_round_funded_year',
                      u'funding_round_raised_amount',
                      u'funding_round_raised_currency_code',
                      u'funding_round_round_code',
                      u'investor' ]

        df.to_csv("investments.csv",
            index=False,
            header=False,
            encoding='utf-8',
            cols=keep_cols,
            mode='ab')

    vc_dets = extract_details(vc)
    f = open('investors.csv', 'ab')
    w = csv.writer(f)
    w.writerow(vc_dets)
    f.close()

    vc_dets = extract_details(vc)

    print 'Percent Complete: {:.2%}'.format(float(i)/total)
    print '*' * 79
    print

with open('not_found.csv', 'wb') as f:
    f.write('\n'.join(not_found))

print 'N Firms Not Found: %d' % len(not_found)
