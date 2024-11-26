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

            growth_rates = pd.read_excel(
                "C:/Users/loren/OneDrive/Documents/extra/code_projects/financial_statement_modeling/data/growth_rates_margins.xlsx"
            )

            model = FinancialStatementModel(
                hist_income=hist_income, growth_rates=growth_rates
            )

            model.historical_income_calcs()
            model.revenue_forecast()
            model.gross_profit_forecast()
            model.cost_of_sales_forecast()
            model.sga_forecast()
            model.r_and_d_forecast()
            model.operating_profit_forecast()
            

            a = model.future_income
            print(a)

        case "sensitivity":
            pass


if __name__ == "__main__":
    main("fsm")
    # main("sensitivity")
