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

    # table des valeurs pour top/flop
    df_repartition = df[str_col_name].value_counts().reset_index().rename(columns={"count": "Nb"})

    if df_repartition[str_col_name].unique().shape[0] > 5:
        dt_mean: float = df[str_col_name].mean()
        dt_min: float = df[str_col_name].min()
        dt_qt1: float = df[str_col_name].quantile(0.25)
        dt_qt2: float = df[str_col_name].quantile(0.50)
        dt_qt3: float = df[str_col_name].quantile(0.75)
        dt_max: float = df[str_col_name].max()

        # Histogramme avec lignes pour min / qt1 / median / mean / qt3 / max
        # couleurs soft (alignées avec style doux du site)
        color_hist = "#cfe8ff"    # pale blue for bars
        color_mean = "#2b8cbe"    # blue for mean
        color_min = "#66c2a5"     # soft green for min
        color_max = "#fc8d62"     # soft orange for max
        color_q = "#8da0cb"       # soft purple for quantiles
        
        fig = px.histogram(
            df,
            x=str_col_name,
            nbins=50,
            opacity=0.9
        )
        fig.update_traces(marker_color=color_hist, marker_line_width=0)
        fig.update_layout(
            template="plotly_white",
            title="Répartition (histogramme)",
            xaxis_title=str_col_name,
            yaxis_title="Nombre",
            bargap=0.05,
            bargroupgap=0
        )

        # ajouter lignes verticales annotées (annotation en haut du graphique)
        def _add_line(x, label, color):
            fig.add_vline(
                x=x,
                line=dict(color=color, width=2, dash="dash"),
                annotation_text=f"{label}: {x:,.2f}".replace(",", " "),
                annotation_position="top right",
                annotation=dict(bgcolor="rgba(255,255,255,0.7)", font=dict(color=color))
            )

        _add_line(dt_min, "Min", color_min)
        _add_line(dt_qt1, "Q1", color_q)
        _add_line(dt_qt2, "Median", color_q)
        _add_line(dt_mean, "Mean", color_mean)
        _add_line(dt_qt3, "Q3", color_q)
        _add_line(dt_max, "Max", color_max)

        str_graph_repartition = fig.to_html(include_plotlyjs=False, full_html=False)
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