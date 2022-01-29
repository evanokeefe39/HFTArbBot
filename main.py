import audioop
from calendar import c
from typing import Tuple
import ccxt
import pprint as pp
import networkx as nx
import matplotlib.pyplot as plt

def main():
# setup
    ex1 = ccxt.binance()
    G = nx.MultiDiGraph()


    # do stuff
    markets = ex1.fetch_markets()
    #length = len(markets)
    length=50


    for i in range(length):
        symbol = markets[i]["symbol"]
        base = markets[i]["base"]
        quote = markets[i]["quote"]
        
        ticker = ex1.fetch_ticker(symbol)
        ask = ticker["ask"]
        askVolume = ticker["askVolume"]
        bid = ticker["bid"]
        bidVolume = ticker["bidVolume"]
        
        taker = markets[i]["taker"] #fee for buyers and sellers in spot market
        
        #Multiples
        if (bid is None or bid <=0):
            continue
        
        quoteToBase = (1-taker)/bid # adjust for fees
        baseToQuote = (1-taker)*ask # adjust for fees
      
        G.add_node(base)
        G.add_node(quote)
        G.add_edge(quote, base, weight=quoteToBase, action="buy", bidask=bid)
        G.add_edge(base, quote, weight=baseToQuote, action="sell", bidask=ask)
        
        # TODO: market depth limits the extent to which the path can be traversed before there is price impact.
        #       need to determine the maximum amount that could be invested into the oppurtunity
        
    generator = nx.algorithms.cycles.simple_cycles(G)

    for g in generator:
        if len(g)<=2: #don't want to buy and sell spread of 1 market
            continue
        
        (m, r, actions) = evaluate_cycle_oppurtunity(G, g)
        
        ppGain = 100*(m-1) # % gains
        formatted_ppGain = "{:.2f}".format(ppGain)
        
        g.append(g[0]) # cycle to linear path
        
        if r:
            print(f"Path {g} expected profit {formatted_ppGain}% \n-------\n{actions}")
        
    
    
def evaluate_cycle_oppurtunity(G, cycle):
    l = len(cycle)
    cumMultiple = 1
    actions = []
    for i in range(l):
        ii = (i+1)%l
        u=cycle[i]
        v=cycle[ii]
        #wrap array around to start when i exceeds len
        edgeData =G.get_edge_data(cycle[i],cycle[ii])[0]
        weight = edgeData["weight"]
        action = edgeData["action"]
        bidask = edgeData["bidask"]
        cumMultiple *= weight
        if action=="buy":
            actions.append(f"Have {u} -> buy {v} @ {bidask} [cumulative multiple: {cumMultiple}]\n")
        if action=="sell":
            actions.append(f"Have {u} -> sell {u} @ {bidask} to get {v} [cumulative multiple: {cumMultiple}]\n")
        
        #pp.pprint(edgeData)
    
    if cumMultiple>1:
        return cumMultiple, True, ''.join(actions)
    return cumMultiple, False, ""     
        
        
    
main()