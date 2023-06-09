import numpy as np
from utils.AntoineEquation import *
from thermo_models.VLEModelBaseClass  import *

class MargulesModel(VLEModel):
    """
    A class representing a thermodynamic model based on Margules.

    This model calculates the conversion between liquid mole fraction and vapor mole fraction
    based on Margules's model.

    Args:
        num_comp (int): The number of components of the system -- typically 2 or 3
        P_sys (float): The system pressure in units compatible with the vapor pressures.
        A_ (dict): Dictionary keys are tuples (i,j) that indicate the coefficient with corresponding value 
                             ex: A_[(1,2)] = A12

    Methods:
        get_activity_coefficient: Using the known Aij values, the gamma activity coefficients are computed according to Margules Equation
        get_vapor_pressure: Computes the vapor pressure for each component at a given temperature.
    """

    #CONSTRUCTOR 
    def __init__(self, num_comp:int, P_sys:float, A_:dict, partial_pressure_eqs: AntoineEquation):
        self.num_comp = num_comp
        self.P_sys = P_sys
        self.A_ = A_
        self.partial_pressure_eqs = partial_pressure_eqs
    
    def get_activity_coefficient(self, x_):
        #For binary mixtures, the Activity coefficients will be returned 
        if (self.num_comp == 2):
            gamma1 = np.exp((self.A_[(1,2)] + 2*(self.A_[(2,1)] - self.A_[(1,2)])*x_[0]) * (x_[1]**2))
            gamma2 = np.exp((self.A_[(2,1)] + 2*(self.A_[(1,2)] - self.A_[(2,1)])*x_[1]) * (x_[0]**2))     
            return np.array([gamma1, gamma2])
        else: 
            print("Margules model only handles binary mixtures")

    def get_vapor_pressure(self, Temp)->np.ndarray:
        """
        Args:
            Temp (float): The temperature at which to compute the vapor pressure.      
        Returns:
            np.ndarray: The vapor pressure for each component.
        """
        vap_pressure_array = []
        for partial_pressure_eq in self.partial_pressure_eqs:
            vap_pressure_array.append(partial_pressure_eq.get_partial_pressure(Temp))
        return np.array(vap_pressure_array)
            
  

    
