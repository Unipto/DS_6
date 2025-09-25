"""Analyse d'une colonne de datetime"""
import pandas as pd
import plotly.express as px
from .commons import get_part
from datetime import datetime

def analyse_datetime(ser: pd.Series, type_name: str) -> str:
    """Analyse d'une colonne/series de type datetime. N'importe quel datetime
    peut fonctionner


    :param pd.Series ser: Serie à analyser
    :param str type_name: Type exact de la colonne passée (différents datetime
    peuvent être passés ici)
    :return str: Code HTML généré en se basant sur le template "datetime"
    """
    df = pd.DataFrame(ser)

    str_col_name = df.columns[0]
    dt_mean: datetime = df[str_col_name].mean()
    dt_min: datetime = df[str_col_name].min()
    dt_qt1: datetime = df[str_col_name].quantile(0.25)
    dt_qt2: datetime = df[str_col_name].quantile(0.50)
    dt_qt3: datetime = df[str_col_name].quantile(0.75)
    dt_max: datetime = df[str_col_name].max()
    
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
        "datetime",
        {
            "COL_TITLE": str_col_name,
            "COL_TYPE": type_name,
            "GRAPH_HTML": str_graph_repartition,
            "TOP5_TABLE": df_repartition.sort_values("Nb", ascending=False)[:5].to_html(index=False, border=0, justify="inherit", classes="table table-sm table-hover"),
            "FLOP5_TABLE": df_repartition.sort_values("Nb")[:5].to_html(index=False, border=0, justify="inherit", classes="table table-sm table-hover"),
            "DT_MEAN": dt_mean.strftime("%Y-%m-%d %H:%M:%S"),
            "DT_MIN": dt_min.strftime("%Y-%m-%d %H:%M:%S"),
            "DT_QT1": dt_qt1.strftime("%Y-%m-%d %H:%M:%S"),
            "DT_QT2": dt_qt2.strftime("%Y-%m-%d %H:%M:%S"),
            "DT_QT3": dt_qt3.strftime("%Y-%m-%d %H:%M:%S"),
            "DT_MAX": dt_max.strftime("%Y-%m-%d %H:%M:%S")
        }
    )
