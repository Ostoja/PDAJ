import sys
import numpy as np
import csv

import argparse
import logging
import os

from scipy.integrate import odeint


# The gravitational acceleration (m.s-2).
g = 9.81
DEFAULT_RESOLUTION = 5
DEFAULT_DT = 0.01
DEFAULT_TMAX = 30

def deriv(y, t, L1, L2, m1, m2):
    """Return the first derivatives of y = theta1, z1, theta2, z2."""
    theta1, z1, theta2, z2 = y

    c, s = np.cos(theta1-theta2), np.sin(theta1-theta2)

    theta1dot = z1
    z1dot = (m2*g*np.sin(theta2)*c - m2*s*(L1*z1**2*c + L2*z2**2) -
             (m1+m2)*g*np.sin(theta1)) / L1 / (m1 + m2*s**2)
    theta2dot = z2
    z2dot = ((m1+m2)*(L1*z1**2*s - g*np.sin(theta2) + g*np.sin(theta1)*c) +
             m2*L2*z2**2*s*c) / L2 / (m1 + m2*s**2)
    return theta1dot, z1dot, theta2dot, z2dot

def solve(L1, L2, m1, m2, tmax, dt, y0):
    t = np.arange(0, tmax+dt, dt)

    # Do the numerical integration of the equations of motion
    y = odeint(deriv, y0, t, args=(L1, L2, m1, m2))
    theta1, theta2 = y[:,0], y[:,2]

    # Convert to Cartesian coordinates of the two bob positions.
    x1 = L1 * np.sin(theta1)
    y1 = -L1 * np.cos(theta1)
    x2 = x1 + L2 * np.sin(theta2)
    y2 = y1 - L2 * np.cos(theta2)

    return theta1, theta2, x1, y1, x2, y2

def simulate_pendulum(theta_resolution, datafile, tmax, dt):
    # Pendulum rod lengths (m), bob masses (kg).
    L1, L2 = 1.0, 1.0
    m1, m2 = 1.0, 1.0

    # Maximum time, time point spacings (all in s).
    #tmax, dt = 30.0, 0.01

    for theta1_init in np.linspace(0, 2*np.pi, theta_resolution):
        for theta2_init in np.linspace(0, 2*np.pi, theta_resolution):
            # Initial conditions: theta1, dtheta1/dt, theta2, dtheta2/dt.
            y0 = np.array([
                theta1_init,
                0.0,
                theta2_init,
                0.0
            ])

            theta1, theta2, x1, y1, x2, y2 = solve(L1, L2, m1, m2, tmax, dt, y0)
	    
            with open(datafile, 'a') as csvfile:
            	writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            	writer.writerow(['Theta1_init: ', theta1_init] + ['Theta2_init: ', theta2_init] + ['Theta1: ', theta1[-1]] + ['Theta2: ', theta2[-1]] + ['x1: ', x1] 				+ ['y1: ', y1] + ['x2: ', x2] + ['y2: ', y2])

            #print theta1_init, theta2_init, theta1[-1], theta2[-1]

def main():
    parser = argparse.ArgumentParser(
        description='Parametric modeling of buckling and free vibration in '\
                    'prismatic shell structures, performed by solving the '\
                    'eigenvalue problem in HCFSM.'
    )
    parser.add_argument(
        'data_file',
        help="Data file where results are saved"
    )
    
    parser.add_argument(
        '-r',
        '--resolution',
        metavar='NUM',
        type=int,
        default=DEFAULT_RESOLUTION,
        help="Resolution, %d by default" % DEFAULT_RESOLUTION
    )
    parser.add_argument(
        '-tm',
        '--tmax',
        metavar='NUM',
        type=float,
        default=DEFAULT_TMAX,
        help="Tmax, %d by default" % DEFAULT_TMAX
    )
    parser.add_argument(
        '-dt',
        '--dt',
        metavar='NUM',
        type=float,
        default=DEFAULT_DT,
        help="Step, %d by default" % DEFAULT_DT
    )
    args = parser.parse_args()
    
    print 'Printam '
    print args.resolution
    # Configure logging
    #log_level = args.verbosity or logging.INFO
    #logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s")

    #if not args.results_file:
    #    args.results_file = os.path.splitext(args.data_file)[0] + '.hdf5'

    
    #do_everything(
    #    data_file=args.data_file,
    #    results_file=args.results_file,
    #    purge_integral_db_cache=args.purge_integral_db_cache,
    #    paginate_by=args.paginate_by,
    #)
    simulate_pendulum(args.resolution, args.data_file, args.tmax, args.dt)

if __name__ == "__main__":
    main()

