# -*- coding: utf-8 -*-
"""
TS_template

OO to enable multithreaded DoE/ML/Optimization

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

        # Initial settings
        # Trading only futures Contracts
        self.settings_ts['markets']  = ['F_AD', 'F_BO', 'F_BP', 'F_C', 'F_CC', 'F_CD',
            'F_CL', 'F_CT', 'F_DX', 'F_EC', 'F_ED', 'F_ES', 'F_FC','F_FV', 'F_GC',
            'F_HG', 'F_HO', 'F_JY', 'F_KC', 'F_LB', 'F_LC', 'F_LN', 'F_MD', 'F_MP',
            'F_NG', 'F_NQ', 'F_NR', 'F_O', 'F_OJ', 'F_PA', 'F_PL', 'F_RB', 'F_RU',
            'F_S','F_SB', 'F_SF', 'F_SI', 'F_SM', 'F_TU', 'F_TY', 'F_US','F_W', 'F_XX',
            'F_YM']

        # Backtesting parameters
        self.settings_ts['lookback']= 504
        self.settings_ts['budget']= 10**6
        self.settings_ts['slippage']= 0.05


        # Trading system parameters
        # This section is specific to trading strategy
        # Put default values here
        self.settings_ts['periodLong'] = 100
        self.settings_ts['periodShort'] = 20

        # Apply settings from outside, put with _settings, from DoE/Optimization/ML loop
        for key in _settings.keys():
            self.settings_ts[key]=_settings[key]

        # Might be handy to have this length pre-calculated
        self.num_markets = len(self.settings_ts['markets'])


    def myTradingSystem(self, DATE, OPEN, HIGH, LOW, CLOSE, VOL, exposure, equity, settings):

        """
        Trading system code goes here
        """

        # Use parameters from "global" storage
        periodLong = self.settings_ts['periodLong']
        periodShort = self.settings_ts['periodShort']

        # Do strategy calculation
        smaLong = numpy.nansum(CLOSE[-periodLong:,:],axis=0)/periodLong
        smaRecent = numpy.nansum(CLOSE[-periodShort:,:],axis=0)/periodShort

        longEquity = smaRecent > smaLong
        shortEquity = ~longEquity

        pos=numpy.zeros((1,self.num_markets))

        pos[0,longEquity] = 1
        pos[0,shortEquity] = -1

        weights = pos/numpy.nansum(abs(pos))


        # Return results
        return weights, settings


    # This method returns "settings" dictionary and is called by quantiacsToolbox
    def mySettings(self):
        """
        Return settings dictionary
        """

        return self.settings_ts



# This is executed when uploaded to Quantiacs
if __name__ == '__main__':

    import quantiacsToolbox

    # Instantiate trading system
    strategy=TS()

    # Set optimized strategy parameters here - should be edited after optimization
    # with results stored in file
    strategy.settings_ts['periodLong'] =[12,23,34,55,66]
    strategy.settings_ts['periodShort']=[12,23,34,55,66]

    # Run backtest
    results=quantiacsToolbox.runts(strategy)


