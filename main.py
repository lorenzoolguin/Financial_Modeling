import pandas as pd
import numpy as np
from fsm import FinancialStatementModel


def main(
    task: str,
):

    match task:
        case "fsm":
            hist_income = pd.read_excel(
                "C:/Users/loren/OneDrive/Documents/extra/code_projects/financial_statement_modeling/data/apple_fsm_data.xlsx",
                sheet_name="Income",
            )
            hist_bs = pd.read_excel(
                "C:/Users/loren/OneDrive/Documents/extra/code_projects/financial_statement_modeling/data/apple_fsm_data.xlsx",
                sheet_name="Balance",
            )
            hist_cf = pd.read_excel(
                "C:/Users/loren/OneDrive/Documents/extra/code_projects/financial_statement_modeling/data/apple_fsm_data.xlsx",
                sheet_name="Cashflow",
            )
            other = pd.read_excel(
                "C:/Users/loren/OneDrive/Documents/extra/code_projects/financial_statement_modeling/data/apple_fsm_data.xlsx",
                sheet_name="Other",
            )

            growth_rates = pd.read_excel(
                "C:/Users/loren/OneDrive/Documents/extra/code_projects/financial_statement_modeling/data/growth_rates_margins.xlsx"
            )

            model = FinancialStatementModel(
                hist_income=hist_income, hist_bs=hist_bs, hist_cf=hist_cf, other = other, growth_rates=growth_rates
            )

            model.historical_income_calcs()
            model.revenue_forecast()
            model.gross_profit_forecast()
            model.cost_of_sales_forecast()
            model.sga_forecast()
            model.r_and_d_forecast()
            model.operating_profit_forecast()

            model.capex_forecast(years_until_SL=2)
            model.ppe_forecast(step_percentage=0.02)
            model.deprec_and_amort_forecast()
            model.other_non_current_assets_forecast()

            model.other_expense_forecast()
            model.stock_based_comp_forecast()
            model.ar_forecast()
            model.inventory_forecast()
            model.vendor_non_trade_receivables_forecast()
            model.other_current_assets_forecast()
            model.accounts_payable_forecast()
            model.other_current_liabilities_forecast()
            model.deferred_rev_forecast()
            model.other_non_current_liabilities_forecast()
            model.long_term_debt_forecast()
            model.common_stock_forecast()
            model.other_comprehensive_income_forecast()
            model.change_in_wc_assets()
            model.change_in_wc_liabilities()
            model.change_other_non_current_liabilities()
            model.change_long_term_debt()



            a = model.future_income
            print(f"Forecasted Income Statement: \n{a}\n{a.columns}")
            b = model.future_bs
            print(f"Forecasted Balance Sheet: \n{b}")
            c = model.future_cf
            print(f"Forecasted Cashflow Statement: \n{c}")

        case "sensitivity":
            pass


if __name__ == "__main__":
    main("fsm")
    # main("sensitivity")
