from typing import TypedDict
from plotly.graph_objects import Figure
import os
import plotly.graph_objects as go
import pandas as pd

class ColumnInformations(TypedDict):
    """Objet retourné par les fonctions d'analyse de colonne

    :cvar str html: Code HTML correspondant à la colonne
    :cvar dict[str, Figure] plots: Dictionnaire ayant comme clé le chemin vers un
      fichier image, et en valeur le plot correspondant à l'image
    """
    html: str
    plots: dict[str, Figure]

def get_part(part_name: str, parameters: dict = {}) -> str:
    """Récupère le code HTML

    :param str part_name: Nom du fichier
    :param dict parameters: Dictionnaire avec en clé le mot-clé dans l'HTML et
        en valeur la valeur à insérer dans l'HTML
    :return str: Le bout de code HTML avec les mot-clés remplacés par leurs valeurs
    """
    str_part_code: str = ""
    str_part_path = os.path.join(os.path.dirname(__file__), "html_parts", f"{part_name}.html")
    with open(str_part_path, mode="r", encoding="utf-8") as f:
        str_part_code = f.read()
    
    for k,v in parameters.items():
        str_part_code = str_part_code.replace(f"%%{k}%%", str(v))

    return str_part_code


###############################################################################
#                                                                             #
#                   STANDARD ANALYSIS UTILS FUNCTIONS                         #
#                                                                             #
###############################################################################


def draw_top(
    df: pd.DataFrame,
    variable: str,
    top_n: int|None = 15,
    thing_to_count: str|None = None,
    orient: str = 'h',
    show_labels: bool = True,
    **plot_params
) -> go.Figure:
    """
    Draws a barplot of top values for a given variable of a given dataframe using Plotly.

    Parameters:
    - df (pd.DataFrame): DataFrame to use
    - variable (str): Variable for which the top values will be plotted.
    - top_n (int|None): How many values should be plotted; None => plot all
    - thing_to_count (str|None): used to build the title (e.g. "Customer" -> "Customer count per ...")
    - orient (str): 'h' or 'v' (horizontal / vertical)
    - show_labels (bool): show the numeric counts on the bars
    - plot_params: passed to go.Bar (e.g. color -> marker_color)
    
    Returns:
    - plotly.graph_objects.Figure
    """
    def format_label(var_name:str):
        return var_name.replace("_", " ").capitalize() # Replace underscores by white spaces and make the first letter uppercase.

    if variable not in df.columns:
        raise ValueError(f"Variable '{variable}' not found in dataframe columns")

    # Build counts DataFrame
    counts = (
        df[variable]
        .astype(str)
        .value_counts()   # sorted descending
        .reset_index()
        # .rename(columns={'index': variable, 'variable': 'count'})
    )

    if top_n is not None:
        counts = counts.iloc[:top_n].copy()

    
    # Ensure count is numeric
    counts['count'] = counts['count'].astype(int)

    formatted_variable = format_label(variable)
    title = f"{(thing_to_count + ' ') if thing_to_count else ''}count per {formatted_variable}{f' (top {top_n})' if top_n is not None else ''}"

    # Prepare bar kwargs: allow passing 'color' to map to marker_color
    bar_kwargs = dict(plot_params)  # copy
    if 'color' in bar_kwargs:
        bar_kwargs.setdefault('marker', {})
        # if marker is dict, set color there, else set marker_color
        if isinstance(bar_kwargs['marker'], dict):
            bar_kwargs['marker'] = {**bar_kwargs['marker'], 'color': bar_kwargs.pop('color')}
        else:
            # fallback: use marker_color argument
            bar_kwargs['marker_color'] = bar_kwargs.pop('color')

    # Text settings
    text_vals = counts['count'].astype(str) if show_labels else None
    textposition = None
    if show_labels:
        # For vertical, place labels above bars; for horizontal, place to the right
        if orient == 'h':
            textposition = plot_params.get('textposition', 'outside')
        else:
            textposition = plot_params.get('textposition', 'outside')

    if orient == 'h':
        # For horizontal bars: x=count, y=category
        y_vals = counts[variable].tolist()
        x_vals = counts['count'].tolist()

        # Plotly lists y categories bottom->top. To show largest on top (like seaborn),
        # reverse the lists.
        y_vals_rev = y_vals[::-1]
        x_vals_rev = x_vals[::-1]
        text_vals_rev = text_vals[::-1] if show_labels else None

        bar = go.Bar(
            x=x_vals_rev,
            y=y_vals_rev,
            orientation='h',
            text=text_vals_rev,
            textposition=textposition,
            hovertemplate='%{y}: %{x}<extra></extra>',
            **bar_kwargs
        )

        fig = go.Figure(data=[bar])
        # ensure category order matches our reversed list
        fig.update_layout(
            yaxis = dict(categoryorder='array', categoryarray=y_vals_rev),
            xaxis_title='Count',
            yaxis_title=format_label(variable),
            title=title,
            margin=dict(l=120)  # give room for long category names
        )

    else:
        # Vertical: x=category, y=count, keep order left->right as in counts
        x_vals = counts[variable].tolist()
        y_vals = counts['count'].tolist()
        bar = go.Bar(
            x=x_vals,
            y=y_vals,
            orientation='v',
            text=text_vals if show_labels else None,
            textposition=textposition,
            hovertemplate='%{x}: %{y}<extra></extra>',
            **bar_kwargs
        )
        fig = go.Figure(data=[bar])
        fig.update_layout(
            xaxis = dict(categoryorder='array', categoryarray=x_vals),
            xaxis_title=format_label(variable),
            yaxis_title='Count',
            title=title,
            margin=dict(b=120)  # room for rotated labels if needed
        )

    # If labels are shown and there are many categories, consider rotating labels for vertical case
    if show_labels and orient != 'h' and len(counts) > 10:
        fig.update_xaxes(tickangle=-45)

    return fig
