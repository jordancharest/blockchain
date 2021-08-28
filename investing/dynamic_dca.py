import pandas as pd
import plotly.express as px

# How to use this script:
# python3 dynamic_dca.py

bitcoin = "BTC"
ethereum = "ETH"
chainlink = "LINK"

###############################################################################
# Edit these values to fit your personal situation
# These values should be the maximum amount of each asset that you would sell,
# not necessarily how much you own
assets = {
    bitcoin : 0.1,
    ethereum : 5,
    chainlink : 500,
}


# Edit these values to reflect the present day
prices = {
    bitcoin  : 49306,
    ethereum  : 3269,
    chainlink : 26.0, 
}

# multiply risk by 10 so we can match keys
# these must all contain the same keys
risk_maps = {
    bitcoin : {
        5  : 47676,
        6  : 62318,
        7  : 79383,
        8  : 98839,
        9  : 120659,
    },
    ethereum : {
        5  : 3502,
        6  : 5383,
        7  : 7818,
        8  : 10863,
        9  : 14580,
    },
    chainlink : {
        5  : 35.8,
        6  : 51.1,
        7  : 70.9,
        8  : 95.5,
        9  : 125.4,
    }
}

# This is a hand-wavy multiplier that attempts to account for:
# 1) The price at each risk level will move up by the time we reach it 
# TODO: adjust for the current price!!!! price won't rise as much to the 0.9 risk level
# when it's currently at 0.8 vs 0.5
# 2) Since we set stop losses instead of market dumping the instant the risk levels are hit,
# most of our sells will be somewhere in the middle of the bands
# Modify based on how bullish you are / how much fantasizing you want to do
# Higher multipliers will favor more aggressive strategies
risk_multiplier = {
    5 : 1.0,
    6 : 1.05,
    7 : 1.1,
    8 : 1.15,
    9 : 1.2,
}

###############################################################################

class Strategy:
    def __init__(self, name, start_risk):
        self.name = name
        self.start_risk = start_risk
        self.num_blocks = int(10 - start_risk)
        self.sell_fraction = range(1, self.num_blocks + 1)
        self.sell_risk_levels = [i for i in range(start_risk , start_risk + self.num_blocks)]
        self.total_increments = sum(self.sell_fraction)

    def __repr__(self):
        return f"""{self.name}
  First Stop Loss: {self.start_risk}
  Sell Fractions:\n{self._get_sell_fractions_str()}
  Sell Risk Levels: {self.sell_risk_levels}\n"""
    
    def _get_sell_fractions_str(self):
        # generate a string representing how much of each asset will be sold in each risk band
        blocks = ""
        tail_risk = self.start_risk        
        head_risk = tail_risk + 1
        total_increments = sum(self.sell_fraction)
        for i in range(self.num_blocks):
            blocks += f"    [{tail_risk:^2} - {head_risk:>2}] : {self.sell_fraction[i]} / {self.total_increments}\n"
            tail_risk += 1
            head_risk += 1
        return blocks

    def run(self, assets, risks):
        # calculate how much you will earn if you sell the designated sell fraction
        # at the entry to each risk band
        results = []
        for ticker, holdings in assets.items():
            risk = self.start_risk
            i = self.start_risk
            for target in self.sell_fraction:
                row = {"Strategy" : self.name}
                row["Risk"] = risk
                row["Proceeds"] = (target / self.total_increments) * holdings * risks[ticker][i] * risk_multiplier[i]
                results.append(row)
                i += 1
                risk += 1
        return results




if __name__ == "__main__":
    # some pandas output options
    pd.set_option('display.precision', 2)
    pd.options.display.float_format = "${:,.0f}".format

    # build several different strategies
    conservative = Strategy("Conservative", 5)
    moderate = Strategy("Moderate", 6)
    aggressive = Strategy("Aggressive", 7)
    yolo = Strategy("YOLO", 8)
    strategies = [conservative, moderate, aggressive, yolo]


    all_results = pd.DataFrame()

    # generate and print results for each strategy
    print("Summary:\n")
    for strategy in strategies:
        print(strategy)
        strategy_results = strategy.run(assets, risk_maps)
        df_results = pd.DataFrame(strategy_results)
        all_results = all_results.append(df_results, ignore_index=True)
        print(df_results.to_string(index=False))

        print(f"\n Total: ${df_results.loc[df_results['Strategy'] == strategy.name, 'Proceeds'].sum():,.0f}\n\n")

    # aggregate by strategy and risk level
    # TODO: can we still aggregate but group by asset as well?
    print(f"All results:\n{all_results}")
    all_results['Proceeds'] = all_results['Proceeds'].round(decimals = 2)
    all_results = all_results.groupby(['Strategy', 'Risk'], sort=False)['Proceeds'].sum().reset_index()
    print(f"\nAggregated\n{all_results}")


    #plot
    fig = px.bar(all_results, x="Strategy",
                              y="Proceeds",
                              color="Risk",
                              title="Visaulizing Dynamic DCA",
                              color_continuous_scale=px.colors.diverging.Temps,
                              color_continuous_midpoint=7)
    fig.show()

