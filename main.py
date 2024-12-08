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
            

            a = model.future_cf
            print(a)

        case "sensitivity":
            pass


if __name__ == "__main__":
    main("fsm")
    # main("sensitivity")
