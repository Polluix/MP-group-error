import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output,callback
import dash_bootstrap_components as dbc
import pandas as pd

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = Dash(__name__, external_stylesheets=external_stylesheets)

#dataframes for each set
df_ps_16x10 = pd.read_csv('./src/16x10_prop_selector.txt', sep=',', names=['Velocity', 'Thrust'])
df_ps_17x10 = pd.read_csv('./src/17x10_prop_selector.txt', sep=',', names=['Velocity', 'Thrust'])
df_ps_19x12 = pd.read_csv('./src/19x12_prop_selector.txt', sep=',', names=['Velocity', 'Thrust'])
df_16x10 = pd.read_csv('./src/Xoar_T5015_16x10.txt', sep=',', names=['Velocity', 'Thrust'])
df_17x10 = pd.read_csv('./src/Xoar_T5015_17x10.txt', sep=',', names=['Velocity', 'Thrust'])
df_19x12 = pd.read_csv('./src/Xoar_T5015_19x12.txt', sep=',', names=['Velocity', 'Thrust'])

df_options = ['df_ps_16x10','df_ps_17x10','df_ps_19x12','df_16x10','df_17x10','df_19x12']
dfs = {
    'df_ps_16x10':df_ps_16x10,
    'df_ps_17x10':df_ps_17x10,
    'df_ps_19x12':df_ps_19x12,
    'df_16x10':df_16x10,
    'df_17x10':df_17x10,
    'df_19x12':df_19x12
}

dfs_16 = {
    'df_ps_16x10':df_ps_16x10,
    'df_16x10':df_16x10
}
dfs_17 = {
    'df_ps_17x10':df_ps_17x10,
    'df_17x10':df_17x10
}
dfs_19 = {
    'df_ps_19x12':df_ps_19x12,
    'df_19x12':df_19x12
}

#Thust(v) function for each set:
def Thrust(v, *args, h=0):
    a, b, c, d = args
    
    return (a*v**3 + b*v**2 + c*v + d)

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

poly = PolynomialFeatures(degree=3)

coefs = []

for key, value in dfs.items():
    lin = LinearRegression()

    v,t = np.array(value['Velocity']), np.array(value['Thrust'])
    
    v = v.reshape(-1,1)

    v_polinomio = poly.fit_transform(v)
    
    lin.fit(v_polinomio, t)
    t_polinomio = lin.predict(v_polinomio)
    
    coefs.append([lin.coef_[3],lin.coef_[2],lin.coef_[1], lin.intercept_]) #appends the function coefs

v = np.linspace(0,50,30)

T = go.Figure()

tuplef = (coefs[0][0],coefs[0][1],coefs[0][2],coefs[0][3])
for i in dfs_16:
    T = T.add_trace(go.Scatter(
                        x=v,
                        y=Thrust(v, *tuplef),
                        name=i),
                    )
    tuplef = (coefs[3][0],coefs[3][1],coefs[3][2],coefs[3][3])

T.update(
    layout_yaxis_range=[0,40],
    layout_xaxis_range=[0,30]
)
T.update_layout(
    {
        'plot_bgcolor':'rgba(0,0,0,0)',
        'paper_bgcolor':'rgba(0,0,0,0)',
        'font_color':'white'
    }
)



props = ['16x10', '17x10', '19x12']

dropdown_thrust = dcc.Dropdown(
    id='dropdown-thrust',
    clearable=False,
    options = props,
    value=props[0]
)

row = dbc.Row(
    [
        dbc.Col(
            [
                dropdown_thrust,
                dcc.Graph(figure=T, id='thrust-fig'),
            ]
        ),
        dbc.Col(
            dcc.Graph(),
        )
    ]
)


app.layout = dbc.Container(
    row,
    fluid=True,
    style={'backgroundColor':'#092635'}
)

@app.callback(
    Output('thrust-fig', 'figure'),
    Input('dropdown-thrust', 'value')
)
def update_output(value):
    
    if value=='16x10':
        df = dfs_16
    elif value=='17x10':
        df = dfs_17
    elif value=='19x12':
        df = dfs_19

    T = go.Figure()
    
    index = props.index(value)
    dist = len(props)
    tuplef = (coefs[index][0],coefs[index][1],coefs[index][2],coefs[0][3])
    
    for i in df:
        T = T.add_trace(go.Scatter(
                            x=v,
                            y=Thrust(v, *tuplef),
                            name=i),
                        )
        tuplef = (coefs[index+dist][0],coefs[index+dist][1],coefs[index+dist][2],coefs[index+dist][3])

    T.update(
        layout_yaxis_range=[0,45],
        layout_xaxis_range=[0,30]
    )
    T.update_layout(
        {
            'plot_bgcolor':'rgba(0,0,0,0)',
            'paper_bgcolor':'rgba(0,0,0,0)',
            'font_color':'white'
        }
    )
    return T

if __name__=='__main__':
    app.run_server(debug=True)
