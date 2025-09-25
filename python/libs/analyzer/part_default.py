"""Analyse d'une colonne dont le type est inconnu"""
import pandas as pd
import plotly.express as px
from .commons import get_part

def analyse_default(ser: pd.Series, type_name: str) -> str:
    """Analyse d'une colonne/series dont le type est inconnu

    :param pd.Series ser: Serie à analyser
    :return str: Code HTML généré en se basant sur le template "default"
    """
    df = pd.DataFrame(ser)

    str_col_name = df.columns[0]

    df = df[str_col_name].value_counts().reset_index().rename(columns={"count": "Nb"})
    str_graph_repartition: str
    if df[str_col_name].unique().shape[0] > 5:
        str_graph_repartition = px.bar(
            df[:1000],
            x=str_col_name,
            y="Nb",
            subtitle="Uniquement le top 1000 des valeurs"
        ).to_html(
            include_plotlyjs=False,
            full_html=False
        )
    else:
        str_graph_repartition = px.pie(
            df[:1000],
            names=str_col_name,
            values="Nb",
            hole=.8,
            subtitle="Uniquement le top 1000 des valeurs"
        ).to_html(
            include_plotlyjs=False,
            full_html=False
        )

    return get_part(
        "default",
        {
            "COL_TITLE": str_col_name,
            "COL_TYPE": type_name,
            "GRAPH_HTML": str_graph_repartition,
            "TOP5_TABLE": df.sort_values("Nb", ascending=False)[:5].to_html(index=False, border=0, justify="inherit", classes="table table-sm table-hover"),
            "FLOP5_TABLE": df.sort_values("Nb")[:5].to_html(index=False, border=0, justify="inherit", classes="table table-sm table-hover"),
        }
    )
