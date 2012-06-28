#!/usr/bin/python
import os,sys
sys.path.append("/home/timvb/app/python_spice-0.0.3/src")
import spice_read
import diffev
import string
from pylab import *

CIRCUIT_FILE = "schmitt.trigger.cir"
TMP_CIRCUIT_FILE = "tmp.cir"
RESULTS_FILE = "results.raw"
template = string.Template(open(CIRCUIT_FILE).read())

targets = [ 1.8,0.9]
#simulation variables
#    {variable_name:[lower_bound, upper_bound]}
def simulation(sim_vec, do_plot=False):
    '''
    perform a single simulation programatically.

    @input: simulation_vector - a vector of all simulation variables
    @return: a cost value related to the fitness function defined internally        
    '''
    

    dv = {"Rbias1": str(sim_vec[0]),
        "Rbias2": str(sim_vec[1]),
        "Rfb": str(sim_vec[2])
        }
    open(TMP_CIRCUIT_FILE,"wt").write(template.safe_substitute(dv))
    os.system("ngspice -b %s >/dev/null 2>/dev/null"%(TMP_CIRCUIT_FILE))
    #os.system("ngspice -b %s "%(TMP_CIRCUIT_FILE))    

    p = spice_read.spice_read(RESULTS_FILE).get_plots()[0]
    time = p.get_scalevector().get_data()
    utp = p.get_datavector(2).get_data()[0]
    ltp = p.get_datavector(3).get_data()[0]
    results = {'utp': utp, 'ltp':ltp}
    cost = fitness(results, targets)


    #plot and print results
    if do_plot:
        print "Simulation Inputs"
        print "Rbias1: %s; Rbias2: %s; Rfb: %s"%(str(sim_vec[0]), str(sim_vec[1]), str(sim_vec[2]))
        print
        print "Simulation Results"
        print "Upper Trip Point: %sV"%(str(utp))
        print "Lower Trip Point: %sV"%(str(ltp))
        print
        print "Cost: %s"%(str(cost))
        vin = p.get_datavector(0)
        vout = p.get_datavector(1)
        
        plot(time, vin.get_data(), label=vin.name)
        plot(time, vout.get_data(), label=vout.name)
        text(0, 3.5, "Rbias1: %.2e"%(float(dv["Rbias1"])), bbox={'facecolor':'red', 'alpha':0.9})
        text(0, 3.3, "Rbias2: %.2e"%(float(dv["Rbias2"])), bbox={'facecolor':'red', 'alpha':0.9})
        text(0, 3.1, "Rfb: %.2e"%(float(dv["Rfb"])), bbox={'facecolor':'red', 'alpha':0.9})
        text(0, 2.9, "UTP: %.2fV"%(float(results["utp"])), bbox={'facecolor':'blue', 'alpha':0.9},color='white')
        text(0, 2.7, "LTP: %.2fV"%(float(results["ltp"])), bbox={'facecolor':'blue', 'alpha':0.9},color='white')
        title("Schmitt Trigger Results")
        grid()
        legend()
        savefig("./img/schmitt.trigger.atuogen.png")
        close()
    
    return cost
    
def fitness(results, targets):
    # Custom fitness function to reach schmitt trigger targets
    cost = 0
    cost += abs(results['utp'] - targets[0])
    cost += abs(results['ltp'] - targets[1])
    
    return cost
        
if __name__ == "__main__":
    #simulation([1e4, 1e4, 1e6], do_plot=True)
    resistor_bound = [1e3, 1e7]
    sim_vars = {"Rbias1":resistor_bound,
            "Rbias2":resistor_bound,
            "Rfb":resistor_bound}

    npop = 100
    #initial_vectors = [[1e3, 1e3, 1e6]]*npop
    
    lbounds = []
    ubounds = []
    var_names = ["Rbias1", "Rbias2", "Rfb"]
    
    #for key in var_names:
    #    bounds = sim_vars[key]
    #    lbounds.append(bounds[0])
    #    ubounds.append(bounds[1])
    lbounds = [5e3, 5e3, 5e3]
    ubounds = [1e5, 1e5, 1e5]
    #de = diffev.DiffEvolver(simulation, initial_vectors)
    #de.set_boundaries(lbounds, ubounds)
    de = diffev.DiffEvolver.frombounds(simulation, lbounds, ubounds, npop)
    de.set_boundaries(np.asarray(lbounds),np.asarray(ubounds), mode='reject')
    for i in range(5):
        print "Simulation run", i
        best_vector = de.solve(2)
        simulation(best_vector, do_plot=True)
    #simulation([1e4, 1e4, 1e6], targets, do_plot=True)
