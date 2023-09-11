#!/usr/bin/env python # -*- coding: utf-8 -*-

import sympy
import numpy as np 
import pandas as pd

from scipy.optimize import curve_fit

import plotly.graph_objects as go 
from plotly.subplots import make_subplots


# 5 parameters logsitic 
def five_log_func(x, a, b, c, d, g):
    return d + (a - d)/(1 + (x/c)**b)**g


# curve fitting
def curve_fitting(x, y, func=five_log_func, method="trf", maxfev=5000):
    try: 
        params, _ = curve_fit(func, x, y, method=method, maxfev=maxfev)
    except RuntimeError as e:
        print(f"Warning: {e}!!!")
    else: 
        return params



# calculate values
def generate_values(x_value, y_value):
    a, b, c, d, g = curve_fitting(x_value, y_value)
    default_interval = np.linspace(0, 129, 130)

    x = sympy.Symbol("x")
    func = d + (a - d)/(1 + (x/c)**b)**g

    values = [func.subs({x: v}) for v in default_interval]
    float_values = [float(v) if v > 0 else 0 for v in values]
    return float_values

def generate_values_1st(x_value, y_value):
    a, b, c, d, g = curve_fitting(x_value, y_value)
    default_interval = np.linspace(0, 129, 130)

    x = sympy.Symbol("x")
    func = d + (a - d)/(1 + (x/c)**b)**g

    deriv_1st = func.diff()
    values_1st = [deriv_1st.subs({x: v}) for v in default_interval]
    float_values_1st = [float(v) for v in values_1st]
    return float_values_1st


def generate_values_2nd(x_value, y_value):
    a, b, c, d, g = curve_fitting(x_value, y_value)
    default_interval = np.linspace(0, 129, 130)

    x = sympy.Symbol("x")
    func = d + (a - d)/(1 + (x/c)**b)**g
  
    deriv_1st = func.diff()
    deriv_2nd = deriv_1st.diff()
    values_2nd = [deriv_2nd.subs({x: v}) for v in default_interval]
    float_values_2nd = [float(v) for v in values_2nd]
    return float_values_2nd 



# generate t values 
def t_value_func(values_1st, values_2nd, threshold=0.005):
    # t2
    t2_index = np.argmax(values_2nd)
    t2_value = values_1st[t2_index]
    # t3
    t3_index = np.argmax(values_1st)
    t3_value = np.max(values_1st)
    # t4
    t4_index = np.argmin(values_2nd)
    t4_value = values_1st[t4_index]
    # t1 
    t1_index = [idx for idx in range(len(values_2nd)) if values_2nd[idx] > threshold][0]
    t1_value = values_1st[t1_index]
    # t5
    t5_index = [idx for idx in range(len(values_2nd)-1, -1, -1) if values_2nd[idx] < -threshold][0]
    t5_value = values_1st[t5_index]

    t_values = {
            "t1": [t1_index, t1_value],
            "t2": [t2_index, t2_value],
            "t3": [t3_index, t3_value],
            "t4": [t4_index, t4_value],
            "t5": [t5_index, t5_value],
            }
    return t_values
    

# generate plot 
def plot_func(x_value, y_value, values, values_1st, values_2nd, threshold=0.005):
    default_interval = np.linspace(0, 129, 130)

    t_values = t_value_func(values_1st, values_2nd, threshold)

    fig = make_subplots(
            rows=2, cols=2,
            specs=[[{"colspan": 2}, None], [{}, {}]],
            subplot_titles=("Growth Function", "Frist Derivative", "Second Derivative"),
            row_heights=[0.6, 0.4] ,
            )

    # actual data
    fig.add_trace(
            go.Scatter(
                x=x_value, y=y_value, mode="markers", 
                marker=dict(size=8, color="red", opacity=0.5),
                ),
            row=1, col=1,
            )
    # infer data 
    fig.add_trace(
            go.Scatter(
                x=default_interval, y=values, mode="lines",
                line=dict(color="steelblue",),
                ),
            row=1, col=1 
            )
    # t1 line 
    fig.add_trace(
            go.Scatter(
                x=[t_values["t1"][0], t_values["t1"][0]],
                y=[0, values[t_values["t1"][0]]],
                mode="lines",
                line=dict(color="orange", dash="dash"),
                ),
            row=1, col=1,
            )
    # t2 line 
    fig.add_trace(
            go.Scatter(
                x=[t_values["t2"][0], t_values["t2"][0]],
                y=[0, values[t_values["t2"][0]]],
                mode="lines",
                line=dict(color="orange", dash="dash"),
                ),
            row=1, col=1,
            )
    # t3 line 
    fig.add_trace(
            go.Scatter(
                x=[t_values["t3"][0], t_values["t3"][0]],
                y=[0, values[t_values["t3"][0]]],
                mode="lines",
                line=dict(color="orange", dash="dash"),
                ),
            row=1, col=1,
            )
    # t4 line 
    fig.add_trace(
            go.Scatter(
                x=[t_values["t4"][0], t_values["t4"][0]],
                y=[0, values[t_values["t4"][0]]],
                mode="lines",
                line=dict(color="orange", dash="dash"),
                ),
            row=1, col=1,
            )
    # t5 line
    fig.add_trace(
            go.Scatter(
                x=[t_values["t5"][0], t_values["t5"][0]],
                y=[0, values[t_values["t5"][0]]],
                mode="lines",
                line=dict(color="orange", dash="dash"),
                ),
            row=1, col=1,
            )

    # annotation
    fig.add_annotation(
            x=t_values["t1"][0], y=values[t_values["t1"][0]],
            text="t1",
            font=dict(size=20),
            showarrow=True, 
            arrowhead=2,
            row=1, col=1
            )
    fig.add_annotation(
            x=t_values["t2"][0], y=values[t_values["t2"][0]],
            text="t2",
            font=dict(size=20),
            showarrow=True, 
            arrowhead=1,
            row=1, col=1
            )
    fig.add_annotation(
            x=t_values["t3"][0], y=values[t_values["t3"][0]],
            text="t3",
            font=dict(size=20),
            showarrow=True, 
            arrowhead=1,
            row=1, col=1
            )
    fig.add_annotation(
            x=t_values["t4"][0], y=values[t_values["t4"][0]],
            text="t4",
            font=dict(size=20),
            showarrow=True, 
            arrowhead=1,
            row=1, col=1
            )
    fig.add_annotation(
            x=t_values["t5"][0], y=values[t_values["t5"][0]],
            text="t5",
            font=dict(size=20),
            showarrow=True, 
            arrowhead=1,
            row=1, col=1
            )
    fig.update_yaxes(
            range=[-5, 150],
            row=1, col=1,

            )


    # first derivative
    fig.add_trace(
            go.Scatter(
                x=default_interval, y=values_1st, mode="lines",
                line=dict(color="steelblue"),
                ),
            row=2, col=1,
            )

    fig.add_trace(
            go.Scatter(
                x=[t_values["t3"][0], t_values["t3"][0]],
                y=[0, values_1st[t_values["t3"][0]]],
                mode="lines",
                line=dict(color="orange", dash="dash"),
                ),
            row=2, col=1,
            )
    fig.add_annotation(
            x=t_values["t3"][0], y=values_1st[t_values["t3"][0]],
            text="t3",
            font=dict(size=20),
            showarrow=True, 
            arrowhead=1,
            row=2, col=1
            )


    # second derivative
    fig.add_trace(
            go.Scatter(
                x=default_interval, y=values_2nd, mode="lines",
                line=dict(color="steelblue"),
                ),
            row=2, col=2,
            )
    fig.add_trace(
            go.Scatter(
                x=[t_values["t1"][0], t_values["t1"][0]],
                y=[0, values_2nd[t_values["t1"][0]]],
                mode="lines",
                line=dict(color="orange", dash="dash"),
                ),
            row=2, col=2,
            )
    fig.add_trace(
            go.Scatter(
                x=[t_values["t5"][0], t_values["t5"][0]],
                y=[0, values_2nd[t_values["t5"][0]]],
                mode="lines",
                line=dict(color="orange", dash="dash"),
                ),
            row=2, col=2,
            )
    fig.add_annotation(
            x=t_values["t1"][0], y=values_2nd[t_values["t1"][0]],
            text="t1",
            font=dict(size=20),
            showarrow=True, 
            arrowhead=1,
            row=2, col=2,
            )
    fig.add_annotation(
            x=t_values["t5"][0], y=values_2nd[t_values["t5"][0]],
            text="t5",
            font=dict(size=20),
            showarrow=True, 
            arrowhead=1,
            row=2, col=2,
            )

    fig.update_layout(
            showlegend=False,
            )

    # fig.show()
    return fig


def save_infer_values(data):
    keys = list(data.keys()).copy()
    keys.remove("x")

    df = {key: generate_values(data["x"], data[key]) for key in keys}
    df = pd.DataFrame(df)
    return df


def save_t_values(data, threshold=0.005):
    keys = list(data.keys()).copy()
    keys.remove("x")

    df = {}
    for key in keys: 
        values_1 = generate_values_1st(data["x"], data[key])
        values_2 = generate_values_2nd(data["x"], data[key])
        res = t_value_func(values_1, values_2, threshold)
        df[key] = res["t1"] + res["t2"] + res["t3"] + res["t4"] + res["t5"]
        
    df = pd.DataFrame(df, 
            index=[
                "t1_day", "t1_value", 
                "t2_day", "t2_value", 
                "t3_day", "t3_value", 
                "t4_day", "t4_value", 
                "t5_day", "t5_value", 
                ])
    return df 

def save_parameters_values(data):
    keys = list(data.keys()).copy()
    keys.remove("x")
    
    df = {key: curve_fitting(data["x"], data[key]) for key in keys}
    df = pd.DataFrame(df, index=["a", "b", "c", "d", "g"])
    return df




