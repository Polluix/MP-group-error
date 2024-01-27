import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, Input, Output,callback, dash_table
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

def dens(h:int) -> float: #[kg/m3] Densidade do ar a altitude h
    H:float = 3.28*h
    return ((1-6.875E-6*H)**5.2561)/(1-6.875E-6*H)*1.225

#Thust(v) function for each set:
def Thrust(v, *args, h=1000):
    a, b, c, d = args
    
    return (a*v**3 + b*v**2 + c*v + d)*dens(h)/dens(0)

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

#Sg for a propulsion set
from src.flightlib import *
from src.perflib import *

dist_16 = []
dist_17 = []
dist_19 = []
for j in range(3):
    
    tuplef = (coefs[j][0],coefs[j][1],coefs[j][2],coefs[j][3])

    for i in range(2):
        distance = Sg(Thrust, 1000, mi, m, 0, *tuplef)

        if j!=2:
            if j!=1:
                dist_16.append(distance)
            else: dist_17.append(distance)
        else: dist_19.append(distance)

        tuplef = (coefs[j+3][0],coefs[j+3][1],coefs[j+3][2],coefs[j+3][3])

# [-0.004068575720411194, 0.04747268366289824, -0.8223437807712293, 37.64674777530596]
# -0.00406858*v**3 + 0.04747268*v**2 + -0.82234378*v + 37.646747775305954

#MTOW for a propulsion set
tuplef = (coefs[0][0],coefs[0][1],coefs[0][2],coefs[0][3])
mtow_16 = []
mtow_17 = []
mtow_19 = []

for j in range(3):
    tuplef = (coefs[j][0],coefs[j][1],coefs[j][2],coefs[j][3])
    for i in range(2):
        mtow = bissecao(MTOW_func, *tuplef, a=8, b=25, h=1000, wind=0)

        if j!=2:
            if j!=1:
                mtow_16.append(mtow)
            else: mtow_17.append(mtow)
        else: mtow_19.append(mtow)

        tuplef = (coefs[j+3][0],coefs[j+3][1],coefs[j+3][2],coefs[j+3][3])

table = {
    'Propeller': [
            props[0],
            props[0],
            props[1],
            props[1],
            props[2],
            props[2]
        ],
    'Takeoff distance [m]':[
            dist_16[0],
            dist_16[1],
            dist_17[0],
            dist_17[1],
            dist_19[0],
            dist_19[1],
        ],
    'MTOW [kg]':[
        mtow_16[0],
        mtow_16[1],
        mtow_17[0],
        mtow_17[1],
        mtow_19[0],
        mtow_19[1],
    ],
    'Static thrust [N]':[
        coefs[0][-1],
        coefs[3][-1],
        coefs[1][-1],
        coefs[4][-1],
        coefs[2][-1],
        coefs[5][-1],
    ],
    'Software': [
        'Aerodesign Propeller Selector',
        'Motocalc',
        'Aerodesign Propeller Selector',
        'Motocalc',
        'Aerodesign Propeller Selector',
        'Motocalc'
    ]
}
tableframe = pd.DataFrame(table)

row = dbc.Row(
    [
        dropdown_thrust,
        dcc.Graph(figure=T, id='thrust-fig'),
    ],
    style={
        'width':'60vw',
    }
)
row2 = dbc.Row(
    style={
        'height':'15vh'
    }
)

app.layout = dbc.Container(
    [
        dbc.Row(
            dash_table.DataTable(tableframe.to_dict('records'),
                                 [{"name": i, "id": i} for i in tableframe.columns],
                                 ),
            style={
                'width':'60vw',
                'height':'20vh'
            }
        ),
        row2,
        row
    ],
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
    v = np.linspace(0,50,30)
    index = props.index(value)
    dist = len(props)
    tuplef = (coefs[index][0],coefs[index][1],coefs[index][2],coefs[index][3])
    
    software = 'Aerodesign Propeller Selector'
    for i in df:
        T = T.add_trace(go.Scatter(
                            x=v,
                            y=Thrust(v, *tuplef),
                            name=software, 
                            ),
                        )
        tuplef = (coefs[index+dist][0],coefs[index+dist][1],coefs[index+dist][2],coefs[index+dist][3])
        software = 'Motocalc'

    T.update(
        layout_yaxis_range=[0,45],
        layout_xaxis_range=[0,30]
    )
    T.update_layout(
        {
            'plot_bgcolor':'rgba(0,0,0,0)',
            'paper_bgcolor':'rgba(0,0,0,0)',
            'font_color':'white'
        },
        yaxis_title="Thrust [N]",
        xaxis_title="Velocity [m/s]",
        title={
        'text': "Dynamic Thrust",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    )
    return T

if __name__=='__main__':
    app.run_server(debug=True)
