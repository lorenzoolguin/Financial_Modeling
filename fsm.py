import os

import pandas as pd
import numpy as np


class FinancialStatementModel:

    def __init__(self, hist_income, hist_bs, hist_cf, other, growth_rates):
        self.hist_income = hist_income
        self.growth_rates = growth_rates
        self.other = other
        self.future_income = pd.DataFrame()
        self.future_income["year"] = growth_rates["Year"]
        self.future_income["fut_interest_income"] = 0
        self.future_income["fut_interest_expense"] = 0

        self.hist_bs = hist_bs
        self.future_bs = pd.DataFrame()
        self.future_bs["year"] = growth_rates["Year"]
        self.hist_cf = hist_cf
        self.future_cf = pd.DataFrame()
        self.future_cf["year"] = growth_rates["Year"]

    def historical_income_calcs(self):
        self.hist_income["Gross_Profit"] = (
            self.hist_income["revenue"] + self.hist_income["cost_of_sales_neg"]
        )
        self.hist_income["Operating_Profit_EBIT"] = (
            self.hist_income["Gross_Profit"]
            + self.hist_income["r_and_d_neg"]
            + self.hist_income["sga_neg"]
        )
        self.hist_income["Pretax_Profit"] = (
            self.hist_income["Operating_Profit_EBIT"]
            + self.hist_income["interest_expense_neg"]
            + self.hist_income["interest_income"]
            + self.hist_income["other_expense_net"]
        )
        self.hist_income["Net_Income"] = (
            self.hist_income["Pretax_Profit"] + self.hist_income["taxes_neg"]
        )
        self.hist_income["EBITDA"] = (
            self.hist_income["Operating_Profit_EBIT"] + self.hist_income["deprec_amor"]
        )
        self.hist_income["Adj_EBITDA"] = (
            self.hist_income["EBITDA"] + self.hist_income["stock_based_comp"]
        )

    def revenue_forecast(self):

        new_revs = [
            self.hist_income[
                self.hist_income["year"] == self.hist_income["year"].max()
            ]["revenue"].values[0]
        ]
        for rate in self.growth_rates["Revenue growth"].values:
            new_year_rev = round((1 + rate) * new_revs[-1])
            new_revs.append(new_year_rev)
        self.future_income["fut_Rev"] = new_revs[1:]

    def gross_profit_forecast(self):

        new_gross_profit = [
            self.hist_income[
                self.hist_income["year"] == self.hist_income["year"].max()
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
                self.hist_income["year"] == self.hist_income["year"].max()
            ]["sga_neg"].values[0]
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
                self.hist_income["year"] == self.hist_income["year"].max()
            ]["r_and_d_neg"].values[0]
        ]

        for index, rate in enumerate(self.growth_rates["R&D % of sales"].values):
            new_year_RandD = -1 * round(
                rate * self.future_income["fut_Rev"].values[index]
            )
            new_RandD.append(new_year_RandD)
        self.future_income["fut_RandD"] = new_RandD[1:]

    def operating_profit_forecast(self):
        self.future_income["fut_Operating_Profit_EBIT"] = (
            self.future_income["fut_Gross_profit"]
            + self.future_income["fut_SGA"]
            + self.future_income["fut_RandD"]
        )

    def cost_of_sales_forecast(self):
        # This has to come after gross profit forecast. It relies on those numbers.
        self.future_income["fut_Cost_of_Sales"] = -1 * (
            self.future_income["fut_Rev"] - self.future_income["fut_Gross_profit"]
        )

    # this capex forecast grows capex in-line with revenue for X years then keeps capex straight-line after
    def capex_forecast(self, years_until_SL):
        new_capex = [
            self.hist_cf[self.hist_cf["year"] == self.hist_cf["year"].max()][
                "capex"
            ].values[0]
        ]

        for rate in self.growth_rates["Revenue growth"].values:
            new_year_capex = round((1 + rate) * new_capex[-1])
            new_capex.append(new_year_capex)

        for ind, ele in enumerate(new_capex):
            if ind >= years_until_SL + 1:
                new_capex[ind] = new_capex[years_until_SL]

        self.future_cf["future_capex"] = new_capex[1:]

    def ppe_forecast(self, step_percentage):
        new_ppe = [
            self.hist_bs[self.hist_bs["year"] == self.hist_bs["year"].max()][
                "ppe"
            ].values[0]
        ]

        da_related_ppe_ratio_to_capex = round(
            self.other["da_related_to_ppe"].values[-1]
            / (-1 * self.hist_cf["capex"].values[-1]),
            4,
        )
        fut_da_related_ppe_ratio = [da_related_ppe_ratio_to_capex]
        for x in range(self.future_income.shape[0]):
            new_ratio = fut_da_related_ppe_ratio[-1] + step_percentage
            fut_da_related_ppe_ratio.append(new_ratio)

        # print(fut_da_related_ppe_ratio)

        new_da_related_to_ppe = []
        for x in range(self.future_income.shape[0]):
            new_value = (
                fut_da_related_ppe_ratio[x + 1]
                * -1
                * self.future_cf["future_capex"].values[x]
            )
            new_da_related_to_ppe.append(new_value)
        self.future_cf["d_and_a_ppe"] = new_da_related_to_ppe

        # print(new_da_related_to_ppe)

        for x in range(self.future_income.shape[0]):
            new_ppe.append(
                new_ppe[x]
                + (-1 * self.future_cf["future_capex"].values[x])
                - new_da_related_to_ppe[x]
            )

        # print(new_ppe)

        self.future_bs["future_ppe"] = new_ppe[1:]

    def deprec_and_amort_forecast(self):
        d_and_a_not_related_ppe = []
        d_and_a_not_ratio_to_rev = []
        for x in range(self.hist_income.shape[0]):
            d_and_a_not_ratio_to_rev.append(
                (
                    self.hist_cf["deprec_amor"].values[x]
                    - self.other["da_related_to_ppe"].values[x]
                )
                / self.hist_income["revenue"].values[x]
            )
        # print(d_and_a_not_ratio_to_rev)
        d_and_a_not_ratio_to_rev_avg = sum(d_and_a_not_ratio_to_rev) / len(
            d_and_a_not_ratio_to_rev
        )

        for x in range(self.future_income.shape[0]):
            d_and_a_not_related_ppe.append(
                d_and_a_not_ratio_to_rev_avg * self.future_income["fut_Rev"].values[x]
            )
        self.future_cf["fut_d_and_a_not_related"] = d_and_a_not_related_ppe
        # print(d_and_a_not_related_ppe)

        future_total_d_and_a = []
        for x in range(self.future_income.shape[0]):
            future_total_d_and_a.append(
                d_and_a_not_related_ppe[x] + self.future_cf["d_and_a_ppe"].values[x]
            )

        # print(future_total_d_and_a)

        self.future_cf["fut_deprec_amor"] = future_total_d_and_a
        self.future_income["fut_deprec_amor"] = future_total_d_and_a

    def other_non_current_assets_forecast(self):
        new_other_nca = [
            self.hist_bs[self.hist_bs["year"] == self.hist_bs["year"].max()][
                "other_non_current_assets"
            ].values[0]
        ]
        # print(new_other_nca)

        for x in range(self.future_bs.shape[0]):
            new_other_nca.append(
                new_other_nca[-1] * (1 + self.growth_rates["Revenue growth"].values[x])
            )

        self.future_bs["fut_other_non_current_assets"] = new_other_nca[1:]

        additions = []
        for x in range(self.future_bs.shape[0]):
            additions.append(
                -1
                * (
                    new_other_nca[x + 1]
                    - new_other_nca[x]
                    + self.future_cf["fut_d_and_a_not_related"].values[x]
                )
            )

        self.future_cf["fut_additions"] = additions
        self.future_cf["fut_other_non_current_assets"] = additions

    def other_expense_forecast(self):
        other_expense_value = self.hist_income[
            self.hist_income["year"] == self.hist_income["year"].max()
        ]["other_expense_net"].values[0]

        new_other_exp = [
            other_expense_value for _ in range(self.future_income.shape[0] + 1)
        ]

        self.future_income["fut_other_expense_net"] = new_other_exp[1:]

    def stock_based_comp_forecast(self):
        new_sbc = [
            self.hist_cf[self.hist_cf["year"] == self.hist_cf["year"].max()][
                "stock_based_comp"
            ].values[0]
        ]
        # print(new_other_nca)

        for x in range(self.future_cf.shape[0]):
            new_sbc.append(
                new_sbc[-1] * (1 + self.growth_rates["Revenue growth"].values[x])
            )

        self.future_cf["fut_stock_based_comp"] = new_sbc[1:]
        self.future_income["fut_stock_based_comp"] = new_sbc[1:]

    def ar_forecast(self):
        new_ar = [
            self.hist_bs[self.hist_bs["year"] == self.hist_bs["year"].max()][
                "accounts_receivable"
            ].values[0]
        ]
        # print(new_ar)

        for x in range(self.future_bs.shape[0]):
            new_ar.append(
                new_ar[-1] * (1 + self.growth_rates["Revenue growth"].values[x])
            )

        self.future_bs["fut_accounts_receivable"] = new_ar[1:]

    def inventory_forecast(self):
        # grows inventories in line with cogs growth
        # print(new_inv)
        cogs_val = [
            self.hist_income[
                self.hist_income["year"] == self.hist_income["year"].max()
            ]["cost_of_sales_neg"].values[0]
        ]
        for x in range(self.future_bs.shape[0]):
            cogs_val.append(self.future_income["fut_Cost_of_Sales"].values[x])

        cogs_growth = []
        for x in range(self.future_bs.shape[0]):
            cogs_growth.append((cogs_val[x + 1] / cogs_val[x]) - 1)

        new_inv = [
            self.hist_bs[self.hist_bs["year"] == self.hist_bs["year"].max()][
                "inventories"
            ].values[0]
        ]
        for x in range(self.future_bs.shape[0]):
            new_inv.append(new_inv[-1] * (1 + cogs_growth[x]))

        self.future_bs["fut_inventories"] = new_inv[1:]

    def accounts_payable_forecast(self):
        cogs_val = [
            self.hist_income[
                self.hist_income["year"] == self.hist_income["year"].max()
            ]["cost_of_sales_neg"].values[0]
        ]
        for x in range(self.future_bs.shape[0]):
            cogs_val.append(self.future_income["fut_Cost_of_Sales"].values[x])

        cogs_growth = []
        for x in range(self.future_bs.shape[0]):
            cogs_growth.append((cogs_val[x + 1] / cogs_val[x]) - 1)

        new_ap = [
            self.hist_bs[self.hist_bs["year"] == self.hist_bs["year"].max()][
                "accounts_payable"
            ].values[0]
        ]
        for x in range(self.future_bs.shape[0]):
            new_ap.append(new_ap[-1] * (1 + cogs_growth[x]))

        self.future_bs["fut_accounts_payable"] = new_ap[1:]

    def vendor_non_trade_receivables_forecast(self):
        new_vendor_ntr = [
            self.hist_bs[self.hist_bs["year"] == self.hist_bs["year"].max()][
                "vendor_non_trade_receivables"
            ].values[0]
        ]

        for x in range(self.future_bs.shape[0]):
            new_vendor_ntr.append(
                new_vendor_ntr[-1] * (1 + self.growth_rates["Revenue growth"].values[x])
            )

        self.future_bs["fut_vendor_non_trade_receivables"] = new_vendor_ntr[1:]

    def other_current_assets_forecast(self):
        new_oca = [
            self.hist_bs[self.hist_bs["year"] == self.hist_bs["year"].max()][
                "other_current_assets"
            ].values[0]
        ]

        for x in range(self.future_bs.shape[0]):
            new_oca.append(
                new_oca[-1] * (1 + self.growth_rates["Revenue growth"].values[x])
            )

        self.future_bs["fut_other_current_assets"] = new_oca[1:]

    def other_current_liabilities_forecast(self):
        new_ocl = [
            self.hist_bs[self.hist_bs["year"] == self.hist_bs["year"].max()][
                "other_current_liabilities"
            ].values[0]
        ]

        for x in range(self.future_bs.shape[0]):
            new_ocl.append(
                new_ocl[-1] * (1 + self.growth_rates["Revenue growth"].values[x])
            )

        self.future_bs["fut_other_current_liabilities"] = new_ocl[1:]

    def deferred_rev_forecast(self):
        new_def_rev = [
            self.hist_bs[self.hist_bs["year"] == self.hist_bs["year"].max()][
                "deferred_revenue_current_and_non"
            ].values[0]
        ]

        for x in range(self.future_bs.shape[0]):
            new_def_rev.append(
                new_def_rev[-1] * (1 + self.growth_rates["Revenue growth"].values[x])
            )

        self.future_bs["fut_deferred_revenue"] = new_def_rev[1:]

    def other_non_current_liabilities_forecast(self):
        new_oncl = [
            self.hist_bs[self.hist_bs["year"] == self.hist_bs["year"].max()][
                "other_non_current_liabilities"
            ].values[0]
        ]

        for x in range(self.future_bs.shape[0]):
            new_oncl.append(
                new_oncl[-1] * (1 + self.growth_rates["Revenue growth"].values[x])
            )

        self.future_bs["fut_other_non_current_liabilities"] = new_oncl[1:]

    def long_term_debt_forecast(self):
        long_term_debt_value = self.hist_bs[
            self.hist_bs["year"] == self.hist_bs["year"].max()
        ]["long_term_debt_incl_current"].values[0]

        new_other_exp = [
            long_term_debt_value for _ in range(self.future_income.shape[0] + 1)
        ]

        self.future_bs["fut_long_term_debt"] = new_other_exp[1:]

    def common_stock_forecast(self):
        new_common_stock = [
            self.hist_bs[self.hist_bs["year"] == self.hist_bs["year"].max()][
                "common_stock"
            ].values[0]
        ]

        for x in self.future_income["fut_stock_based_comp"].values:
            new_common_stock.append(new_common_stock[-1] + x)

        self.future_bs["fut_common_stock"] = new_common_stock[1:]

    def other_comprehensive_income_forecast(self):
        other_comp_income = self.hist_bs[
            self.hist_bs["year"] == self.hist_bs["year"].max()
        ]["other_comp_income"].values[0]

        new_other_comp_income = [
            other_comp_income for _ in range(self.future_income.shape[0] + 1)
        ]

        self.future_bs["fut_other_comp_income"] = new_other_comp_income[1:]

    def change_in_wc_assets(self):
        wc_assets = self.hist_bs[self.hist_bs["year"] == self.hist_bs["year"].max()][
            [
                "accounts_receivable",
                "inventories",
                "vendor_non_trade_receivables",
                "other_current_assets",
            ]
        ]
        wc_assets["wc_assets_sum"] = wc_assets[
            [
                "accounts_receivable",
                "inventories",
                "vendor_non_trade_receivables",
                "other_current_assets",
            ]
        ].sum(axis=1)
        # print(wc_assets)

        fut_wc_assets = self.future_bs[
            [
                "fut_accounts_receivable",
                "fut_inventories",
                "fut_vendor_non_trade_receivables",
                "fut_other_current_assets",
            ]
        ].copy()
        fut_wc_assets["fut_wc_assets_sum"] = fut_wc_assets[
            [
                "fut_accounts_receivable",
                "fut_inventories",
                "fut_vendor_non_trade_receivables",
                "fut_other_current_assets",
            ]
        ].sum(axis=1)
        # print(fut_wc_assets)

        wc_asset_changes = []
        wc_asset_changes.append(wc_assets["wc_assets_sum"].values[0] - fut_wc_assets["fut_wc_assets_sum"].values[0])
        for x in range(len(fut_wc_assets)-1):
                wc_asset_changes.append(fut_wc_assets["fut_wc_assets_sum"].values[x] - fut_wc_assets["fut_wc_assets_sum"].values[x+1])
        # print(wc_asset_changes)

        self.future_cf["fut_wc_asset_changes"] = wc_asset_changes

    def change_in_wc_liabilities(self):
        wc_liabilities = self.hist_bs[self.hist_bs["year"] == self.hist_bs["year"].max()][
            [
                "accounts_payable",
                "other_current_liabilities",
                "deferred_revenue_current_and_non",
            ]
        ]
        wc_liabilities["wc_liabilities_sum"] = wc_liabilities[
            [
                "accounts_payable",
                "other_current_liabilities",
                "deferred_revenue_current_and_non",
            ]
        ].sum(axis=1)
        # print(wc_liabilities)

        fut_wc_liabilities = self.future_bs[
            [
                "fut_accounts_payable",
                "fut_other_current_liabilities",
                "fut_deferred_revenue",
            ]
        ].copy()
        fut_wc_liabilities["fut_wc_liabilities_sum"] = fut_wc_liabilities[
            [
                "fut_accounts_payable",
                "fut_other_current_liabilities",
                "fut_deferred_revenue",
            ]
        ].sum(axis=1)
        # print(fut_wc_liabilities)

        wc_liabilities_changes = []
        wc_liabilities_changes.append(fut_wc_liabilities["fut_wc_liabilities_sum"].values[0] - wc_liabilities["wc_liabilities_sum"].values[0])
        for x in range(len(fut_wc_liabilities)-1):
                wc_liabilities_changes.append(fut_wc_liabilities["fut_wc_liabilities_sum"].values[x+1] - fut_wc_liabilities["fut_wc_liabilities_sum"].values[x])
        # print(wc_liabilities_changes)

        self.future_cf["fut_wc_liabilities_changes"] = wc_liabilities_changes

    def change_other_non_current_liabilities(self):
        new_oncl = [
            self.hist_bs[self.hist_bs["year"] == self.hist_bs["year"].max()][
                "other_non_current_liabilities"
            ].values[0]
        ]

        for x in range(self.future_bs.shape[0]):
            new_oncl.append(
                new_oncl[-1] * (1 + self.growth_rates["Revenue growth"].values[x])
            )

        change_oncl = []
        for x in range(1, len(new_oncl)):
            change_oncl.append(new_oncl[x] - new_oncl[x-1])

        self.future_cf["fut_other_non_current_liabilities"] = change_oncl


    def change_long_term_debt(self):
        long_term_debt_value = self.hist_bs[
            self.hist_bs["year"] == self.hist_bs["year"].max()
        ]["long_term_debt_incl_current"].values[0]

        new_other_exp = [
            long_term_debt_value for _ in range(self.future_income.shape[0] + 1)
        ]

        change_ltd = []
        for x in range(1, len(new_other_exp)):
            change_ltd.append(new_other_exp[x] - new_other_exp[x-1])

        self.future_cf["fut_long_term_debt"] = change_ltd

    def change_revolver(self): # need to plug to really solve
        pass
