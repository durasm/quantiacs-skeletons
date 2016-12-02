# -*- coding: utf-8 -*-
"""
MP_DoE

Multiprocessing DoE example for Quantiacs with trendfollowing strategy
Selecting periods with best Sharpe for each market

@author: durasm

"""
import quantiacsToolbox
from TS_trendfollowing import TS # This is strategy to optimize
from multiprocessing import Pool

import numpy as np
import time

# DOE - Loops over parameters variation without algorithm aka "brute force"
def call_backtest (params):

    i = params[0]
    j = params[1]

    strategy = TS() # Instantiate
    strategy.settings_ts['markets']  = markets   # Overrides initial in TS
    strategy.settings_ts['lookback']  = lookback # Overrides initial in TS
    strategy.settings_ts['periodLong']  = i  # Apply long period from argument to trading system
    strategy.settings_ts['periodShort'] = j  # Short period

    # Display stdout message
    print "Evaluating for long: %d and short: %d"%(i,j)

    # Backtest trading system defined in "strategy" (TS class object)
    # without showing graphics after the run
    results=quantiacsToolbox.runts(strategy,False)

    # Send backtest results back
    return (i, j, results)

# This is not essential for the optimization, but handy for evaluating sharpe
# of each "market"
def getMarketStats(returns):

    ret=np.transpose(np.array(returns))
    ret=ret[:,lookback:]
    statistics=[]
    for i in range(len(ret)):
        statistics.append(quantiacsToolbox.stats(ret[i]))
    return statistics


# Markets to optimize - global, accessible from all processes
markets = ['F_KC', 'F_LB','F_OJ', 'F_PA', 'F_PL', 'F_RB', 'F_RU', 'F_S','F_SB', 'F_SF', 'F_SI', 'F_SM']
lookback = 504

# Main
if __name__ == '__main__':

    use_num_cores = 5 # NUMBER OF PROCESSES to evaluate in parallel
    worker_pool = Pool(use_num_cores)

    # Generate parameter space:
    #    Long period  - from 50 to 200 with step 10
    #    Short period - from 5 to 50 step 5
    params_all=[]
    for long_period in range(50, 210, 10):
        for short_period in range (5, 55, 5):
            if long_period <= short_period: # Skip cases where long period is smaller/equal than short period
                continue
            params_all.append((long_period, short_period))

    # Initialize list to handle best periods
    best_sharpe = [-200]*len(markets)
    best_long = [0]*len(markets)
    best_short = [0]*len(markets)

    # Start measuring time
    time_elapsed=time.time()

    # imap_unordered - returns results as soon as clcualted, doesn't return in order in "params_all"
    # use imap - to get results in the same order as in "params_all"
    for (long_period, short_period, results) in worker_pool.imap_unordered(call_backtest, params_all):

        # Get stats for performed backtesting.
        stats = getMarketStats(results['marketEquity'])

        # Check each market and pick best strat parameters based on Sharpe ratio
        for k in range (len(stats)):
            if best_sharpe[k] < stats[k]['sharpe']:
                best_sharpe[k]=stats[k]['sharpe']
                best_long[k]=long_period
                best_short[k]=short_period
                print markets[k], " sharpe: ", best_sharpe[k]


    print "\nUsed %d parallel processes, execution time: %d s"%(use_num_cores, time.time()-time_elapsed)

    # Final result
    print "Optimized long periods:", best_long
    print "Optimized short periods:", best_short


    # Store results to file
    out_file=file('TS_trendfollowing.dat','w')
    out_file.write("strategy.settings_ts['periodLong']  = %s\n"%repr(best_long))
    out_file.write("strategy.settings_ts['periodShort'] = %s\n"%repr(best_short))
    out_file.close()
