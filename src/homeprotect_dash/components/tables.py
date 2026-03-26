from __future__ import annotations

import pandas as pd
from dash import dash_table


def dataframe_table(df: pd.DataFrame, table_id: str) -> dash_table.DataTable:
    return dash_table.DataTable(
        id=table_id,
        columns=[{"name": col.replace("_", " ").title(), "id": col} for col in df.columns],
        data=df.to_dict("records"),
        page_size=8,
        sort_action="native",
        filter_action="native",
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "10px",
            "whiteSpace": "normal",
            "height": "auto",
            "fontFamily": "Inter, Arial, sans-serif",
            "fontSize": "14px",
        },
        style_header={
            "fontWeight": "600",
            "backgroundColor": "#f5f7fb",
        },
    )
