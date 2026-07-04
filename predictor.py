import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def predict_next_month_expense(transactions):

    if len(transactions) < 2:
        return None

    df = pd.DataFrame(
        transactions,
        columns=["date", "amount"]
    )

    df["date"] = pd.to_datetime(df["date"])

    df["month"] = (
        df["date"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_expense = (
        df.groupby("month")["amount"]
        .sum()
        .reset_index()
    )

    if len(monthly_expense) < 2:
        return None

    monthly_expense["month_number"] = range(
        1,
        len(monthly_expense) + 1
    )

    X = monthly_expense[["month_number"]]
    y = monthly_expense["amount"]

    model = LinearRegression()

    model.fit(X, y)

    next_month = len(monthly_expense) + 1

    prediction = model.predict(
        [[next_month]]
    )[0]

    return round(max(prediction, 0), 2)