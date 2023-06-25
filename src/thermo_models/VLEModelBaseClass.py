import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt


class VLEModel:
    """
    A class used to represent a Vapor-Liquid Equilibrium (VLE) model.

    This base class provides methods for computing activity coefficients, vapor pressures, 
    and converting between liquid and vapor mole fractions. Derived classes provide
    specific calculation of activity coefficient and vapor pressure for different 
    types of mixtures.
    ...

    Attributes
    ----------
    num_comp : int
        The number of components in the mixture.
    P_sys : float
        The total pressure of the system.

    Methods
    -------
    get_activity_coefficient(*args) -> np.ndarray:
        Computes the activity coefficient for each component in the the model.
    get_vapor_pressure(*args) -> np.ndarray:
        Computes the vapor pressure for each component in the model.
    convert_x_to_y(x_array:np.ndarray) -> np.ndarray:
        Computes the conversion from liquid mole fraction to vapor mole fraction.
    compute_Txy(vars:np.ndarray, x_array:np.ndarray) -> list:
        Computes the system of equations for the T-x-y calculations.
    plot_binary_Txy(data_points:int, comp_index:int):
        Plots the T-x-y diagram for a binary mixture.
    """
    def __init__(self,num_comp:int,P_sys:float):
        self.num_comp = num_comp
        self.P_sys = P_sys
        
    def get_activity_coefficient(self, x_array=None)->np.ndarray:
        """
        Computes the activity coefficient for each component in the the model.

        Raises:
            NotImplementedError: _description_

        Returns:
            np.ndarray: _description_
        """
        raise NotImplementedError
    
    def get_vapor_pressure(self, Temp)->np.ndarray:
        """
        Compute the vapor pressure for each component in the model.

        Raises:
            NotImplementedError: _description_

        Returns:
            np.ndarray: _description_
        """
        raise NotImplementedError
    
    def convert_x_to_y(self, x_array:np.ndarray)->np.ndarray:
        """
        Computes the conversion from liquid mole fraction to vapor mole fraction.

        Args:
            x_array (np.ndarray): Liquid mole fraction of each component.

        Returns:
            solution (np.ndarray): The solution from the fsolve function, which includes the vapor mole fractions and the system temperature.
        """
        # Compute the boiling points for each component
        boiling_points = [eq.get_boiling_point(self.P_sys) for eq in self.partial_pressure_eqs]

        # Estimate the system temperature as the average of the maximum and minimum boiling points
        Temp_guess = np.mean([np.amax(boiling_points), np.amin(boiling_points)])

        # Create an initial guess for the vapor mole fractions and system temperature
        init_guess = np.append(np.full(self.num_comp, 1/self.num_comp), Temp_guess)

        # Use fsolve to find the vapor mole fractions and system temperature that satisfy the equilibrium conditions
        solution = fsolve(self.compute_Txy, init_guess, args=(x_array,))

        return solution
    
    def convert_y_to_x(self, y_array:np.ndarray)->np.ndarray:
        """
        Computes the conversion from vapor mole fraction to liquid mole fraction.

        Args:
            y_array (np.ndarray): Vapor mole fraction of each component.

        Returns:
            solution (np.ndarray): The solution from the fsolve function, which includes the liquid mole fractions and the system temperature.
        """
        boiling_points = [eq.get_boiling_point(self.P_sys) for eq in self.partial_pressure_eqs]
        Temp_guess = np.mean([np.amax(boiling_points), np.amin(boiling_points)])
        init_guess = np.append(np.full(self.num_comp, 1/self.num_comp), Temp_guess)
        solution = fsolve(self.compute_Txy2, init_guess, args=(y_array,))

        return solution
        
    def compute_Txy(self, vars:np.ndarray, x_array:np.ndarray)->list:
        """
        Computes the system of equations for the T-x-y calculations.

        This function is used as the input to the fsolve function to find the roots 
        of the system of equations, which represent the equilibrium conditions for 
        the vapor-liquid equilibrium calculations.

        Args:
            vars (np.ndarray): A 1D array containing the initial guess for the 
                vapor mole fractions and the system temperature.
            x_array (np.ndarray): A 1D array containing the liquid mole fractions.

        Returns:
            eqs (list): A list of equations representing the equilibrium conditions.
        """
        # Extract the vapor mole fractions and temperature from the vars array
        y_array = vars[:-1]
        Temp = vars[-1]

        # Compute the left-hand side of the equilibrium equations
        lefths = x_array * self.get_activity_coefficient(x_array) * self.get_vapor_pressure(Temp)

        # Compute the right-hand side of the equilibrium equations
        righths = y_array * self.P_sys

        # Form the system of equations by subtracting the right-hand side from the left-hand side
        # Also include the normalization conditions for the mole fractions
        eqs = (lefths - righths).tolist() + [np.sum(y_array) - 1]

        return eqs
    
    def compute_Txy2(self, vars:np.ndarray, y_array:np.ndarray)->list:
        x_array = vars[:-1]
        Temp = vars[-1]

        lhs = x_array * self.get_activity_coefficient(x_array) * self.get_vapor_pressure(Temp)
        rhs = y_array * self.P_sys

        eqs = (lhs - rhs).tolist() + [np.sum(x_array) - 1]

        return eqs



    def plot_binary_Txy(self, data_points:int, comp_index:int):
        """
        Plots the T-x-y diagram for a binary mixture.

        Args:
            data_points (int): Number of data points to use in the plot.
            comp_index (int): Index of the component to plot.

        Raises:
            ValueError: If the number of components is not 2.
        """
        if self.num_comp != 2:
            raise ValueError("This method can only be used for binary mixtures.")

        # Create an array of mole fractions for the first component
        x1_space = np.linspace(0, 1, data_points)

        # Create a 2D array of mole fractions for both components
        x_array = np.column_stack([x1_space, 1 - x1_space])

        # Initialize lists to store the vapor mole fractions and system temperatures
        y_array, t_evaluated = [], []

        # Compute the vapor mole fractions and system temperatures for each set of liquid mole fractions
        for x in x_array:
            solution = self.convert_x_to_y(x)
            y_array.append(solution[:-1])
            t_evaluated.append(solution[-1])

        # Convert the list of vapor mole fractions to a 2D numpy array
        y_array = np.array(y_array)

        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(x_array[:, comp_index], t_evaluated, label="Liquid phase")
        plt.plot(y_array[:, comp_index], t_evaluated, label="Vapor phase")
        plt.title("T-x-y Diagram")
        plt.xlabel(f"Mole fraction of component {comp_index + 1}")
        plt.ylabel("Temperature")
        plt.legend()
        plt.show()
    
    def plot_ternary_txy(self, data_points:int, comp_index:int):
        x_array = np.zeros((data_points**2, 3))
        idx = 0
        for x1 in np.linspace(0, 1, data_points):
            for x2 in np.linspace(0, 1-x1, data_points):
                x3 = 1 - x1 - x2
                x_array[idx] = np.array([x1, x2, x3])
                idx = idx + 1

        # Initialize lists to store the vapor mole fractions and system temperatures
        y_array, t_evaluated = [], []

        # Compute the vapor mole fractions and system temperatures for each set of liquid mole fractions
        for x in x_array:
            solution = self.convert_x_to_y(x)
            y_array.append(solution[:-1])
            t_evaluated.append(solution[-1])

        # Convert the list of vapor mole fractions to a 2D numpy array
        y_array = np.array(y_array)
        t_evaluated = np.array(t_evaluated)

        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(x_array[:, comp_index], t_evaluated, label="Liquid phase")
        plt.plot(y_array[:, comp_index], t_evaluated, label="Vapor phase")
        plt.title("T-x-y Diagram")
        plt.xlabel(f"Mole fraction of component {comp_index + 1}")
        plt.ylabel("Temperature")
        plt.legend()
        plt.show()


        
   

                
            
        
        


        