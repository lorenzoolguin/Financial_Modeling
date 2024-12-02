import os

import pandas as pd
import numpy as np


class FinancialStatementModel:

    def __init__(self, hist_income, hist_bs, hist_cf, growth_rates):
        self.hist_income = hist_income
        self.growth_rates = growth_rates
        self.future_income = pd.DataFrame()
        self.future_income["Year"] = growth_rates["Year"]
        self.hist_bs = hist_bs
        self.future_bs = pd.DataFrame()
        self.future_bs["Year"] = growth_rates["Year"]
        self.hist_cf = hist_cf
        self.future_cf = pd.DataFrame()
        self.future_cf["Year"] = growth_rates["Year"]

    def historical_income_calcs(self):
        self.hist_income["Gross_Profit"] = (
            self.hist_income["Revenue"] + self.hist_income["Cost of sales (enter as -)"]
        )
        self.hist_income["Operating_Profit_EBIT"] = (
            self.hist_income["Gross_Profit"]
            + self.hist_income["Research & development (enter as -)"]
            + self.hist_income["Selling, general & administrative (enter as -)"]
        )
        self.hist_income["Pretax_Profit"] = (
            self.hist_income["Operating_Profit_EBIT"]
            + self.hist_income["Interest expense (enter as -)"]
            + self.hist_income["Interest income"]
            + self.hist_income["Other expense, net (enter as -)"]
        )
        self.hist_income["Net_Income"] = (
            self.hist_income["Pretax_Profit"]
            + self.hist_income["Taxes (enter expense as -)"]
        )
        self.hist_income["EBITDA"] = (
            self.hist_income["Operating_Profit_EBIT"]
            + self.hist_income["Depreciation & amortization"]
        )
        self.hist_income["Adj_EBITDA"] = (
            self.hist_income["EBITDA"] + self.hist_income["Stock based compensation"]
        )

    def revenue_forecast(self):

        new_revs = [
            self.hist_income[
                self.hist_income["Year"] == self.hist_income["Year"].max()
            ]["Revenue"].values[0]
        ]
        for rate in self.growth_rates["Revenue growth"].values:
            new_year_rev = round((1 + rate) * new_revs[-1])
            new_revs.append(new_year_rev)
        self.future_income["fut_Rev"] = new_revs[1:]

    def gross_profit_forecast(self):

        new_gross_profit = [
            self.hist_income[
                self.hist_income["Year"] == self.hist_income["Year"].max()
            ]["Gross_Profit"].values[0]
        ]

        for index, rate in enumerate(self.growth_rates["Gross profit margin"].values):
            new_year_gross_profit = round(
                (rate) * self.future_income["fut_Rev"].values[index]
            )
            new_gross_profit.append(new_year_gross_profit)
        self.future_income["fut_Gross_profit"] = new_gross_profit[1:]

    def sga_forecast(self):
        new_sga = [
            self.hist_income[
                self.hist_income["Year"] == self.hist_income["Year"].max()
            ]["Selling, general & administrative (enter as -)"].values[0]
        ]

        for index, rate in enumerate(self.growth_rates["SG&A % of sales"].values):
            new_year_sga = -1 * round(
                rate * self.future_income["fut_Rev"].values[index]
            )
            new_sga.append(new_year_sga)
        self.future_income["fut_SGA"] = new_sga[1:]

    def r_and_d_forecast(self):
        new_RandD = [
            self.hist_income[
                self.hist_income["Year"] == self.hist_income["Year"].max()
            ]["Research & development (enter as -)"].values[0]
        ]

        for index, rate in enumerate(self.growth_rates["R&D % of sales"].values):
            new_year_RandD = -1 * round(
                rate * self.future_income["fut_Rev"].values[index]
            )
            new_RandD.append(new_year_RandD)
        self.future_income["fut_RandD"] = new_RandD[1:]

    def operating_profit_forecast(self):
        self.future_income["fut_Operating_Profit_EBIT"] = self.future_income["fut_Gross_profit"] + \
            self.future_income["fut_SGA"] + self.future_income["fut_RandD"]
        
    def cost_of_sales_forecast(self):
        # This has to come after gross profit forecast. It relies on those numbers.
        self.future_income['fut_Cost_of_Sales'] = -1 * (self.future_income['fut_Rev'] - self.future_income['fut_Gross_profit'])

    # this capex forecast grows capex in-line with revenue for X years then keeps capex straight-line after
    def capex_forecast(self, years_until_SL):
        new_capex = [self.hist_cf[self.hist_cf["Year"] == self.hist_cf["Year"].max()]['Capital expenditures'].values[0]]
       
        for rate in self.growth_rates["Revenue growth"].values:
            new_year_capex = round((1 + rate) * new_capex[-1])
            new_capex.append(new_year_capex)

        for ind, ele in enumerate(new_capex):
            if ind >= years_until_SL+1:
                new_capex[ind] = new_capex[years_until_SL]
        
                
        self.future_cf['future_capex'] = new_capex[1:]

