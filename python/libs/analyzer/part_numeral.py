"""Analyse d'une colonne de numeral"""
import pandas as pd
import plotly.express as px
from .commons import get_part

def analyse_numeral(ser: pd.Series, type_name: str) -> str:
    """Analyse d'une colonne/series de type numeral (float, int, etc...). N'importe quel numeral
    peut fonctionner


    :param pd.Series ser: Serie à analyser
    :param str type_name: Type exact de la colonne passée (différents numeral
    peuvent être passés ici)
    :return str: Code HTML généré en se basant sur le template "numeral"
    """
    df = pd.DataFrame(ser)

    str_col_name = df.columns[0]
    dt_mean: float = df[str_col_name].mean()
    dt_min: float = df[str_col_name].min()
    dt_qt1: float = df[str_col_name].quantile(0.25)
    dt_qt2: float = df[str_col_name].quantile(0.50)
    dt_qt3: float = df[str_col_name].quantile(0.75)
    dt_max: float = df[str_col_name].max()
    
    df_repartition = df[str_col_name].value_counts().reset_index().rename(columns={"count": "Nb"})
    str_graph_repartition: str
    if df_repartition[str_col_name].unique().shape[0] > 5:
        str_graph_repartition = px.bar(
            df_repartition[:1000],
            x=str_col_name,
            y="Nb",
            subtitle="Uniquement le top 1000 des valeurs"
        ).to_html(
            include_plotlyjs=False,
            full_html=False
        )
    else:
        str_graph_repartition = px.pie(
            df_repartition[:1000],
            names=str_col_name,
            values="Nb",
            hole=.8,
            subtitle="Uniquement le top 1000 des valeurs"
        ).to_html(
            include_plotlyjs=False,
            full_html=False            
        )

    return get_part(
        "numeral",
        {
            "COL_TITLE": str_col_name,
            "COL_TYPE": type_name,
            "GRAPH_HTML": str_graph_repartition,
            "TOP5_TABLE": df_repartition.sort_values("Nb", ascending=False)[:5].to_html(index=False, border=0, justify="inherit", classes="table table-sm table-hover"),
            "FLOP5_TABLE": df_repartition.sort_values("Nb")[:5].to_html(index=False, border=0, justify="inherit", classes="table table-sm table-hover"),
            "DT_MEAN": f"{dt_mean:,.2f}".replace(",", " "),
            "DT_MIN": f"{dt_min:,.2f}".replace(",", " "),
            "DT_QT1": f"{dt_qt1:,.2f}".replace(",", " "),
            "DT_QT2": f"{dt_qt2:,.2f}".replace(",", " "),
            "DT_QT3": f"{dt_qt3:,.2f}".replace(",", " "),
            "DT_MAX": f"{dt_max:,.2f}".replace(",", " ")
        }
    )