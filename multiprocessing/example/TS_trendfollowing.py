# -*- coding: utf-8 -*-
"""
TS_trendfollowing

Quantiacs Trend Following Trading System Example
Rewritten to OO to make multithreaded DoE/ML/Optimization possible

@author: durasm

"""

import numpy


# Strategy class
class TS ():

    def __init__(self, _settings={}):

        """
        [optional] parameter "_settings" is dictionary which contains settings
        that should be applied from "outside"

        Default values for settings are put here, and overwritten if settings contain same key
        Settings contain few sets of parameters:
            Markets that are traded
            Backtester parameters
            Trading System parameters
            ...
        """

        self.settings_ts={}

        # Initial settings (reduced list for the example)
        # Trading only futures Contracts
        self.settings_ts['markets']  = ['F_KC', 'F_LB','F_OJ', 'F_PA', 'F_PL', 'F_RB', 'F_RU',
        'F_S','F_SB', 'F_SF', 'F_SI', 'F_SM']

        # Backtesting parameters
        self.settings_ts['lookback']= 504
        self.settings_ts['budget']= 10**6
        self.settings_ts['slippage']= 0.05


        # Trading system parameters
        
        # This is specific to trading strategy
        # Comment this after putting in best ones below
        self.settings_ts['periodLong'] = 100
        self.settings_ts['periodShort'] = 20

        # Set optimized strategy parameters - shold be uncommented before uploading to Quantiacs
        # strategy.settings_ts['periodLong']  = [90, 80, 80, 190, 120, 50, 50, 170, 50, 60, 200, 200]
        # strategy.settings_ts['periodShort'] = [50, 40, 50, 50, 5, 40, 5, 5, 15, 10, 50, 40]


        # Apply settings from outside, put with _settings, from DoE/Optimization/ML loop
        for key in _settings.keys():
            self.settings_ts[key]=_settings[key]

        # Might be handy to have this length pre-calculated
        self.num_markets = len(self.settings_ts['markets'])


    def myTradingSystem(self, DATE, OPEN, HIGH, LOW, CLOSE, VOL, exposure, equity, settings):

        """
        Copied from Quantiacs "trend following" example
        """

        ''' This system uses trend following techniques to allocate capital into the desired equities'''

        nMarkets = CLOSE.shape[1] # We have this in self.num_markets but left here as in original TS

        periodLong = self.settings_ts['periodLong']   # We are optimizing periods, use the one prescribed from outside
        periodShort = self.settings_ts['periodShort']

        # Should be edited after optimization as periodLong and periodShort become lists with
        # best periods for each market
        #
        #smaLong=[]
        #smaRecent=[]
        #for idx in range(len(periodLong)):
        #    smaLong.append(numpy.nansum(CLOSE[-periodLong[idx]:,idx],axis=0)/periodLong[idx])
        #    smaRecent.append(numpy.nansum(CLOSE[-periodShort[idx]:,idx],axis=0)/periodShort[idx])

        smaLong = numpy.nansum(CLOSE[-periodLong:,:],axis=0)/periodLong
        smaRecent = numpy.nansum(CLOSE[-periodShort:,:],axis=0)/periodShort


        longEquity = smaRecent > smaLong
        shortEquity = ~longEquity

        pos=numpy.zeros((1,nMarkets))

        pos[0,longEquity] = 1
        pos[0,shortEquity] = -1

        weights = pos/numpy.nansum(abs(pos))

        return weights, settings


    def mySettings(self):
        """
        Return settings dictionary
        """
        return self.settings_ts



# For testing this strategy as standalone, and when testing best parameters
# resulted from optimisation
if __name__ == '__main__':

    import quantiacsToolbox

    # Instantiate trading system
    strategy=TS()

    # Run backtest
    results=quantiacsToolbox.runts(strategy)
