# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 14:57:32 2022

@author: Luiz
"""
import numpy as np
from scipy.constants import g

def dens(h:int) -> float: #[kg/m3] Densidade do ar a altitude h
    H:float = 3.28*h
    return ((1-6.875E-6*H)**5.2561)/(1-6.875E-6*H)*1.225

# ---------------------------Constantes-----------------------------
ground:int   = 0  # [m] Altitude do solo em relação ao nível do mar (Joinville = 4m)
S:float      = 1.15#[m2] Área da asa
v:np.ndarray = np.arange(3, 20, 0.1) #[m/s] range de velocidades
rho0:float   = dens(ground) #[kg/m3] Densidade para solo de Joinville
CD0:float    = 0.042 #[adim.] CD0 da aeronave, aerodinâmica
K:float      = 0.073 #[adim.] Constante K da aeronave, aerodinãmica
CLmax:float  = 1.9235 #[adim.] CL máximo na decolagem, aerodinâmica.
m:float      = 13.9447 #[kg] Critério de massa máxima da aeronave para h = 600 m
MTOW:float   = m #[kg] MTOW da aeronaveusando bisseção para h = 1000 m
W:float      = MTOW*g #força peso
W_S          = W/S #carga alar

# ---------------------------Funções------------------------------
def q(v:float,h:int) -> float: #[N/m2] Pressão dinâmica função de v e h
    return 0.5*dens(h)*v**2

def CL(v:float, h:int, W:float) -> float: #[adim.] Coeficiente de sustentação total da aeronave, função de v, h e weight
        return  W/(q(v,h) * S)

def CD(v:float,h:int, W:float) -> float: #[adim.] Coeficiente de arrasto total da aeronave, função de v, h e weight
    return CD0 + K*CL(v,h,W)**2
   
def Td(v:float,h:int) -> float: #[N] Tração disponível da aeronave,  função de v e h
    return (-0.00406858*v**3 + 0.04747268*v**2 + -0.82234378*v + 37.646747775305954)*dens(h)/rho0
    # return (-0.007666317579360982*v**3+ 0.030973683321508697*v**2+ -0.9194989133250041*v+ 34.36362393162395)*dens(h)/rho0
    # return (-0.002378537089326893*v**3+ 0.02453091279009248*v**2+ -0.739071505421641*v+ 35.0028350945495)
    # return (-0.002373529943051733*v**3+ 0.023714566856950295*v**2+ -0.725324364950364*v+ 34.161817296996716)*dens(h)/rho0
    # return (-0.0058191152562674375*v**3+ 0.039460173493538656*v**2+ -1.0618404685167253*v+ 44.800907357381064)*dens(h)/rho0
    # return (-0.0054450022025105405*v**3+ 0.03554673419523681*v**2+ -1.0704566898824777*v+ 46.79801307007784)*dens(h)/rho0
    

# print(Td(11, 346))
# Td = lambda v, h=1000: (32.938595 + -0.800094*v + 0.053774*v**2 + -0.010142*v**3)*dens(h)/dens(0)

def Ct(v:float, h:int) -> float:
    return Td(v, h)/(q(v,h) * S)

def Pd(v:float,h:int) -> float: #[W] Potência disponível da aeronave,  função de v e h
    return Td(v, h)*v

def Treq(v:float,h:int, W:float) -> float: #[N] Tração requerida da aeronave,  função de v, h e weight
        return CD(v,h,W)*q(v,h)*S

def Preq(v:float,h:int, W:float) -> float: #[W] Potência requerida da aeronave,  função de v, h e weight
    return Treq(v,h,W)*v

def V_stall(h:int, m:float) -> float: #velocidade de estol da aeronave
    W:float = m*9.81
    return  np.sqrt(2*W/(dens(h)*CLmax*S))

def atrito(h:int, m:int, ds:int) -> float:
    return V_stall(h, m)**2/(2*g*ds)

def gamma(v:float, h:int, W:float) -> float:
    return np.arctan(1/(CL(v,h,W)/CD(v,h,W)))*180/np.pi #[graus] Retorna o ângulo de planeio

def Thrust(v, *args, h=0):
    a, b, c, d = args
    
    return (a*v**3 + b*v**2 + c*v + d)*dens(h)/dens(0)

def bissecao(f:callable, *args:tuple, a:float, b:float, h:int, wind:int, tol = 1e-4) -> float:
  """
  Calcula a raiz de uma função utilizando o método da bissecção
  
  Recebe:
    f       => Função para encontrar a raiz
    a,b     => Intervalo de busca (b>a)
    h       => altitude densidade
    tol     => Tolerância a se alcançar (b-a)/2 < tol    
  Retorna:
    n    => Número de iterações
    p    => Raiz
    erro => Erro (b-a)/2  
  """

  n      = 0
  p      = (a+b)/2.0
  imag_a = f(Thrust,a, *args, h=h, hw=0)
  imag_p = f(Thrust,p, *args, h=h, hw=0)
  erro   = (b-a)/2.0
      
  while erro>tol:
      if imag_a * imag_p < 0:
          b = p
      else:
          a = p
          imag_a = imag_p
      
      n     += 1
      p      = (a+b)/2.0
      erro   = (b - a)/2.0
      imag_p = f(Thrust,p, *args, h=h, hw=0)

  return p
