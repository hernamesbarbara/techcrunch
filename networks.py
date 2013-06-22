import numpy as np
import pandas as pd
from collections import Counter, defaultdict

def read_data(f='./investments.csv'):
    df = pd.read_csv(f,
        names=['company','year',
               'amt','currency',
               'round','firm'])

    df.currency = df.currency.fillna('USD')
    df = df.drop(df[df.currency != 'USD'].index)

    # mask = df.firm.isin(df.firm.value_counts().head(10).index)
    # df = df[mask]
    return df

def in_common(deals, vc, other):
    return sorted([co for co in deals[vc] if co in deals[other]])

def pearson(deals, vc, other):
    common = (deals, vc, other)
    n = len(common)

    if n == 0:
        return 0

    vc_sum    = sum([ deals[vc][co] for co in common ])
    other_sum = sum([ deals[other][co] for co in common ])
    vc_sq     = sum([ pow(deals[vc][co], 2) for co in common ])
    other_sq  = sum([ pow(deals[other][co], 2) for co in common ])
    p         = sum([ deals[vc][co] * deals[other][co] for co in common ])

    num = p - (vc_sum * other_sum / n)
    den = np.sqrt((vc_sq - pow(vc_sum,2)/n) * (other_sq - pow(other_sum,2)/n))

    if den == 0:
        return 0

    r = num / den
    return r

def compute_matches(deals, vc, similarity=pearson):
    totals = defaultdict(int)
    sim_totals = defaultdict(int)

    for other in deals:
        if other == vc:
            continue
        sim = similarity(deals, vc, other)

        if sim <= 0:
            continue

        for co in deals[other]:
            if co not in deals[vc] or deals[vc][co] == 0:
                totals[co] += deals[other][co] * sim
                sim_totals[co] += sim

    rankings = [(total/sim_totals[co], co) for co,total in totals.items()]
    rankings.sort()
    rankings.reverse()
    return rankings[:25]

df = read_data()
firms = df.firm.unique().tolist()

deals_done = {}
for vc in firms:
    rows = df[df.firm == vc]
    companies = rows.company
    n_rounds = Counter(companies)
    deals_done[vc] = n_rounds

sequoia ='Sequoia Capital'
first_round = 'First Round Capital'
accel = 'Accel Partners'
village = 'Village Ventures'
ia_ventures = 'IA Ventures'
rre = 'RRE Ventures'

print pearson(deals_done, sequoia, first_round)
print compute_matches(deals_done, first_round)
