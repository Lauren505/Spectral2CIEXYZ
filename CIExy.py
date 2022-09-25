from lib2to3.pgen2.pgen import DFAState
from math import exp
import numpy as np
import pandas as pd
import argparse

def read_data(filename):
    df = pd.read_csv(filename)
    return df

# NVIDIA: Simple Analytic Approximations to the CIE XYZ Color Matching Functions
# https://research.nvidia.com/publication/2013-07_simple-analytic-approximations-cie-xyz-color-matching-functions
def xFit_1931(wave):
    t1 = (wave-442.0)*(0.0624 if wave<442.0 else 0.0374)
    t2 = (wave-599.8)*(0.0264 if wave<599.8 else 0.0323)
    t3 = (wave-501.1)*(0.0490 if wave<501.1 else 0.0382)
    return 0.362*exp(-0.5*t1*t1) + 1.056*exp(-0.5*t2*t2) - 0.065*exp(-0.5*t3*t3)

def yFit_1931(wave):
    t1 = (wave-568.8)*(0.0213 if wave<568.8 else 0.0247)
    t2 = (wave-530.9)*(0.0613 if wave<530.9 else 0.0322)
    return 0.821*exp(-0.5*t1*t1) + 0.286*exp(-0.5*t2*t2)

def zFit_1931(wave):
    t1 = (wave-437.0)*(0.0845 if wave<437.0 else 0.0278)
    t2 = (wave-459.0)*(0.0385 if wave<459.0 else 0.0725)
    return 1.217*exp(-0.5*t1*t1) + 0.681*exp(-0.5*t2*t2)

def xyzFit():
    WL = np.arange(380, 781, 1)
    xFit, yFit, zFit = np.vectorize(xFit_1931), np.vectorize(yFit_1931), np.vectorize(zFit_1931)
    X, Y, Z = xFit(WL), yFit(WL), zFit(WL)
    d = {'WL (nm)': WL, 'X': X, 'Y': Y, 'Z': Z}
    df = pd.DataFrame(d)
    return df

# CIE(x,y) converter
def CIE_XYZ(spectral_data, xyz_color_matching):
    X = (spectral_data['irradiance'] * xyz_color_matching["X"]).sum()
    Y = (spectral_data['irradiance'] * xyz_color_matching["Y"]).sum()
    Z = (spectral_data['irradiance'] * xyz_color_matching["Z"]).sum()
    print('X: ', round(X, 3), 'Y: ', round(Y, 3), 'Z: ', round(Z, 3))
    x = X/(X+Y+Z)
    y = Y/(X+Y+Z)
    z = Z/(X+Y+Z)
    print(f'(x, y, z) = ({round(x, 3)}, {round(y, 3)}, {round(z, 3)})')
    return X, Y, Z, x, y, z

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", type=str, default="./spectral_data.csv")
    parser.add_argument("-xyz", "--xyzMatching", type=str, default="./color_matching_functions.csv", help="custom xyz color matching function file")
    parser.add_argument("-m", "--method", type=str, default="NVIDIA", help="custom or NVIDIA")
    args = parser.parse_args()
    spectral_data = read_data(args.data)
    xyz_color_matching = read_data(args.xyzMatching) if args.method=="custom" else xyzFit()
    print('Using method: ', args.method)
    X, Y, Z, x, y, z = CIE_XYZ(spectral_data, xyz_color_matching)