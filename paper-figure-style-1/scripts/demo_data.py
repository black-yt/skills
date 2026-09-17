"""Fictional, deterministic example data. Never an empirical benchmark.

All intervals in the demos are illustrative bounds, not estimated confidence
intervals. Replace both estimates and bounds with the user's real measurements.
"""
from math import exp
from charts import COLORS

FAMILIES = ("Planning", "Search", "Retrieval", "Compact")
FAMILY_COLORS = dict(zip(FAMILIES,COLORS[:4]))
FAMILY_SHAPES = dict(zip(FAMILIES,("circle","square","diamond","triangle")))

# name, family, success percent, demonstration half-range, USD, minutes, tokens(k)
_ROWS = [
    ("Atlas Pro", "Planning", 68.2, 2.1, 7.8, 17, 86),
    ("Atlas Base", "Planning", 64.5, 2.8, 5.4, 20, 77),
    ("Cedar Pro", "Search", 62.8, 1.8, 3.4, 10, 16),
    ("Cedar Core", "Search", 54.6, 3.2, 4.2, 18, 29),
    ("Quartz Max", "Compact", 41.0, 3.0, 3.1, 40, 145),
    ("Iris Plus", "Retrieval", 37.2, 2.6, 2.2, 22, 171),
    ("Cedar Lite", "Search", 35.0, 2.4, 3.6, 23, 44),
    ("Iris Base", "Retrieval", 30.4, 3.0, 1.6, 34, 98),
    ("Iris Edge", "Retrieval", 28.6, 2.5, 1.0, 38, 67),
    ("Quartz Core", "Compact", 27.1, 2.7, 2.7, 21, 33),
    ("Atlas Lite", "Planning", 25.8, 2.9, 4.6, 27, 137),
    ("Quartz Mini", "Compact", 21.4, 2.3, 1.3, 19, 46),
    ("Cedar Mini", "Search", 18.8, 2.4, .6, 29, 60),
    ("Atlas Mini", "Planning", 6.2, 1.5, .72, 8, 25),
    ("Quartz Nano", "Compact", 5.0, 1.1, .82, 32, 115),
]
METHODS = [dict(id=i+1,name=n,family=g,score=s,low=s-e,high=s+e,
                cost=c,time=t,tokens=k,color=FAMILY_COLORS[g],shape=FAMILY_SHAPES[g])
           for i,(n,g,s,e,c,t,k) in enumerate(_ROWS)]


def budget_curve(method, *, steps=60):
    """Synthetic cumulative staircase ending at the corresponding demo score."""
    if steps<2:
        raise ValueError("steps must be at least 2")
    times=[60*i/steps for i in range(steps+1)]
    delay=3+(method["id"]%4)
    rate=6+method["id"]*1.3
    def shape(t):
        return (1-exp(-max(0,t-delay)/rate))**1.8
    y=[round(method["score"]*shape(t)/shape(60),1) for t in times]
    span=(method["high"]-method["low"])/2
    delta=[span*(v/method["score"])**.5 for v in y]
    low=[max(0,v-d) for v,d in zip(y,delta)]
    high=[v+d for v,d in zip(y,delta)]
    return times,y,low,high
