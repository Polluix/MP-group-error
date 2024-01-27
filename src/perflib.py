"""
Biblioteca com as funções utilizadas nos scripts de voo
@author: Luiz
"""
import numpy as np
from src.flightlib import *

# ---------------------------Constantes-----------------------------
CD_to              = 0.0604 #coeficiente de arrasto na decolagem
CL_to              = 0.8317 #coeficiente de sustentação na decolagem
mi:float           = 0.02 #coeficiente de atrito da aeronave
h:int              = 1000 #altitude densidade
M_array:np.ndarray = np.linspace(8, 15, 3) #massas utilizadas nos plots
h_array:np.ndarray = np.linspace(0, h, 3) #altitudes utilizadas nos plots

def RC(v:float, h:int, W:float) -> float: #[m/s] Razão de subida da aeronave, em função de v, h e weight
    return (Pd(v,h)-Preq(v,h, W))/W

def theta(v:float, h:int, W:float) -> float:
    return np.arcsin(RC(v,h,W)/v)*180/np.pi #[graus] Retorna o ângulo de subida

DeltaP:float       = Pd(v,h)-Preq(v,h,W)
DeltaPMax:float    = max(DeltaP) #[W] Maior diferença entre potências
RCmax:float        = DeltaPMax/W #[m/s] Calcula a razão de subida máxima
theta_max:float    = max(theta(v,h,W)) #Razão de subida máximo
LDmax:float        = max(CL(v, h, W)/CD(v, h, W)) #[adim.] Razão L/D máxima
gammamin:float     = np.arctan(1/LDmax)*180/np.pi #[graus] Definindo o ângulo de planeio 
RDMAX:float        = max(-v*np.sin(gamma(v,h,m*g)*np.pi/180)) #Razão de planeio mínima

# ---------------------------Funções-----------------------------
def L_takeoff(v:float, h:int): #[N] Força sustentação da aeronave, função de CL, Q e S
    return CL_to*q(v,h)*S

def D_takeoff(v:float, h:int):
    return CD_to*q(v,h)*S

def S_takeoff(h:int, mi:float, m:float) -> np.ndarray:
    X:list   =[0]
    V:list   =[0]
    X0 = V0  = 0
    i:int    = 0
    dT:float = 0.005
    Vstall   = V_stall(h, m)
    while V[i]<= 1.1*Vstall: #ponto inicial da rotação
        A = (g/W)*( (Td(V[i], h) - D_takeoff(V[i], h) - mi*( W - L_takeoff(V[i], h))))
        V.append(V0 + A*dT)
        X.append(X0 + V[i]*dT)
        V0:float = V[i+1]
        X0:float = X[i+1]
        i=i+1
    V_array = np.array(V)
    X_array = np.array(X)
    return X_array, V_array  

def Sg(trac:callable, h:int, mi:float, m:float, Hw:float, *args:tuple) -> np.ndarray:
    X:list = []
    X.append(0)
    X0:float = 0
    V:list = []
    V0 = Hw
    V.append(Hw)
    i:int = 0
    dT:float = 0.005
    W:float = m*9.81
    Vstall = V_stall(h, m)
    while V[i]<= Vstall*1.1: #ponto inicial da rotação
        A = (g/W)*( (trac(V[i], *args) - D_takeoff(V[i], h) - mi*( W - L_takeoff(V[i], h))))
        V.append(V0 + A*dT)
        X.append(X0 + V[i]*dT)
        V0:float = V[i+1]
        X0:float = X[i+1]
        i=i+1
    X_array = np.array(X)
    return X_array[-1]

def MTOW_func(Td:callable,M:float, *args:tuple, h:int = 1000, hw:float = 0):
    return RC(1.1*V_stall(h, M),h,M*9.81) - np.sin(np.arctan(0.7/(55-Sg(Td, h, mi, m, 0, *args))))*1.1*V_stall(h, M)
