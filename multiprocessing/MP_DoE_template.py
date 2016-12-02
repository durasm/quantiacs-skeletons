# -*- coding: utf-8 -*-
"""
MP_DoE_template

Multiprocessing DoE template for Quantiacs toolbox

@author: durasm

"""


# This is strategy to optimize - change as needed
# must be written as class to handle parameters separately between paeallel processes
from TS_trendfollowing import TS

 # Using standard python multiprocessing module
from multiprocessing import Pool

import quantiacsToolbox


# Function for the "worker" - exedutes as separate process
# it should backtest one set of parameters received in "params" as tuple
def call_backtest (params):

    # Split params tuple to separate variables
    i = params[0]
    j = params[1]

    strategy = TS() # Instantiate trading dsystem

    # Apply srtategy paramters and needed overrides to default TS settings
    strategy.settings_ts['markets']  = markets   # Overrides initial in TS - optional
    strategy.settings_ts['lookback']  = lookback # Overrides initial in TS - optional

    strategy.settings_ts['periodLong']  = i  # Apply one parameter of the trading system
    strategy.settings_ts['periodShort'] = j  # Apply second parameter ....

    # Display stdout message
    # Messages written out get messed up due to concurrent execution
    print "Evaluating for long: %d and short: %d"%(i,j)

    # Backtest trading system with parameters
    # without showing graphics after the run
    results=quantiacsToolbox.runts(strategy,False)

    # Send backtest results back - must be combined in a single object - tuple in this case
    # Returning back also input parameters to link with "results" of backtesting
    # as imap_unoredered was used for multiprocessing and order of returned results is not
    # the same as order of parameters
    return (i, j, results)



# Global variables accessible from all processes

# Just an example here. Not needed if all default settings in TS are OK.
markets = ['F_KC', 'F_LB','F_OJ', 'F_PA', 'F_PL', 'F_RB', 'F_RU',
    'F_S','F_SB', 'F_SF', 'F_SI', 'F_SM']
lookback = 504



# Main
# The script execution starts here!
if __name__ == '__main__':

    use_num_cores = 5 # NUMBER OF PROCESSES to evaluate in parallel - edit based on resources (e.g. num_cpu_cores)
    worker_pool = Pool(use_num_cores) # Initialize Pool for handling parallel processes

    # Generate trading system parameter space
    # Generate tuples with all combinations of trading strategy parameters to test
    params_all=[]
    for long_period in range(50, 210, 10):
        for short_period in range (5, 50, 5):
            params_all.append((long_period, short_period))


    # Init some variables needed for result processing
    best_long=0
    best_short=0
    best_sharpe=-20


    # Start parallel processing
    # Call "call_backtest" function with one tuple of parameters from "params_all" in one process and do that
    # unitl all tuples from "params_all" are calculated. for loop run is executed each time new result is received.
    #
    # imap_unordered - process results as soon as clcualted, doesn't return in order as in "params_all"
    # imap - process results in the same order as in "params_all"
    for (long_period, short_period, results) in worker_pool.imap_unordered(call_backtest, params_all):

        # Check results here and do the needed selection, filtering, results checking, etc...
        if best_sharpe < results['stats']['sharpe']:
            best_long=long_period
            best_short=short_period
            best_sharpe=results['stats']['sharpe']
            print "Sharpe: ", results['stats']['sharpe'], " for long period: ", long_period, " short period: ", short_period


    # Display final result
    print "Optimized long periods:", best_long
    print "Optimized short periods:", best_short


    # Store results to file !! Important !!
    # If displayed only on screen results usually get lost.
    out_file=file('TS_results.dat','w')
    out_file.write("strategy.settings_ts['periodLong']  = %s\n"%repr(best_long))
    out_file.write("strategy.settings_ts['periodShort'] = %s\n"%repr(best_short))
    out_file.close()
