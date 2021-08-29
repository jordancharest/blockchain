import pandas as pd
import plotly.express as px

# How to use this script:
# python3 sell_strategy.py

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
        5  : 51.1,
        6  : 70.9,
        7  : 95.5,
        8  : 125.4,
        9  : 161.0,
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
valid_strategies = ["linear", "ddca"]

class Strategy:
    def __init__(self, name, start_risk, strategy_type):
        assert strategy_type in valid_strategies, "Invalid strategy"
        self.name = name
        self.start_risk = start_risk
        self.num_blocks = 10 - start_risk
        self.sell_fraction = []

        if strategy_type == "linear":
            self.sell_fraction = [1] * self.num_blocks
        elif strategy_type == "ddca":
            self.sell_fraction = range(1, self.num_blocks + 1)

        self.sell_risk_levels = range(start_risk , start_risk + self.num_blocks)
        self.total_increments = sum(self.sell_fraction)

    def __repr__(self):
        return f"""{self.name}
  First Stop Loss: {self.start_risk}
  Sell Fractions:\n{self._get_sell_fractions_str()}"""

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
                row = {'strategy' : self.name}
                row['risk'] = risk
                row['proceeds'] = (target / self.total_increments) * holdings * risks[ticker][i] * risk_multiplier[i]
                row['total'] = 0
                results.append(row)
                i += 1
                risk += 1
        return pd.DataFrame(results)




if __name__ == "__main__":
    # some pandas output options
    pd.set_option('display.precision', 2)
    pd.options.display.float_format = "${:,.0f}".format

    # build several different strategies
    conservative_linear = Strategy("Conservative Linear", 5, strategy_type="linear")
    moderate_linear = Strategy("Moderate Linear", 6, strategy_type="linear")
    aggressive_linear = Strategy("Aggressive Linear", 7, strategy_type="linear")
    yolo_linear = Strategy("YOLO Linear", 8, strategy_type="linear")

    conservative = Strategy("Conservative DDCA", 5, strategy_type="ddca")
    moderate = Strategy("Moderate DDCA", 6, strategy_type="ddca")
    aggressive = Strategy("Aggressive DDCA", 7, strategy_type="ddca")
    yolo = Strategy("YOLO DDCA", 8, strategy_type="ddca")
    strategies = [conservative_linear, moderate_linear, aggressive_linear, yolo_linear, conservative, moderate, aggressive, yolo]


    all_results = pd.DataFrame()

    # generate and print results for each strategy
    print("Summary:\n")
    for strategy in strategies:
        print(strategy)
        results = strategy.run(assets, risk_maps)
        results['total'] = results.loc[results.strategy == strategy.name, 'proceeds'].sum()

        print(results.to_string(index=False))
        print(f"\n Total: ${results.loc[results.strategy == strategy.name, 'proceeds'].sum():,.0f}\n\n")

        all_results = all_results.append(results, ignore_index=True)

    # aggregate by strategy and risk level
    # TODO: can we still aggregate but group by asset as well?
    print(f"All results:\n{all_results}")
    all_results = all_results.groupby(['strategy', 'risk', 'total'], sort=False).proceeds.sum().reset_index()
    all_results.proceeds = all_results['proceeds'].round(decimals = 2)

    # sort by total proceeds
    print(type(all_results))
    print(all_results)
    all_results = all_results.sort_values(['total', 'risk'])

    print(f"\nAggregated and Sorted:\n{all_results}")


    # plot
    fig = px.bar(all_results, x="strategy",
                              y="proceeds",
                              color="risk",
                              title="Visualizing Sell Strategies",
                              color_continuous_scale=px.colors.diverging.Temps,
                              color_continuous_midpoint=7)
    fig.show()

