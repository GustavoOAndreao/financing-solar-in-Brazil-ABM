#!/usr/bin/env python
# coding: utf-8

# In[1]:


import random
import feather

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import simpy
import numpy as np
import pandas as pd
import math as math

def run_simulation(fALPHA, fBETA, fN_of_firms, finitial_tc_upper, finitial_tc_lower, finitial_cc_upper, 
                   finitial_cc_lower, finitial_projects_total, finitial_lc_mean, finitial_lc_variance, 
                   fOKshare, fSIM_TIME, fRANDOM_SEED, fNUMBER_OF_REPETITIONS, fRANDOMIZE):
    
    '''
    This prevents the simulation from crashing
    '''
    
    global ALPHA
    global BETA
    global N_of_firms
    global initial_tc_upper
    global initial_tc_lower
    global initial_cc_upper
    global initial_cc_lower
    global initial_projects_total
    global initial_lc_mean
    global initial_lc_variance
    global RS
    global SIM_TIME
    global RANDOM_SEED
    global NUMBER_OF_REPETITIONS
    global OKshare
    
    '''
    We must tell the simulation that the parameters are the function's inputs
    '''
    
   #Parameter_in_the_smiulation = function_input
    ALPHA = fALPHA
    BETA = fBETA
    N_of_firms = fN_of_firms
    initial_tc_upper = finitial_tc_upper
    initial_tc_lower = finitial_tc_lower
    initial_cc_upper = finitial_cc_upper
    initial_cc_lower = finitial_cc_lower
    initial_projects_total = finitial_projects_total
    initial_lc_mean = finitial_lc_mean
    initial_lc_variance = finitial_lc_variance
    SIM_TIME = fSIM_TIME
    RANDOM_SEED = fRANDOM_SEED
    NUMBER_OF_REPETITIONS = fNUMBER_OF_REPETITIONS
    RANDOMIZE = fRANDOMIZE
    OKshare = fOKshare
       
    global endDF
    endDF = pd.DataFrame() #we have to set a initial main dataframe
    
    for rep in range (RANDOM_SEED, RANDOM_SEED + NUMBER_OF_REPETITIONS): #the +1 produces 1 repetition
        random.seed(rep) #in order to have pseudo-random numbers, allowing greater replicability
        global SIM
        SIM = rep
        print(round(SIM/NUMBER_OF_REPETITIONS, 3), end = '...')
        
        for j in (0, 0.25, 0.5, 0.75, 1):
            RS = j
            env = simpy.Environment() #starts the environment in each iteration
            env.process(outside_firm(env)) #starts the outside_firm process

            global Df
            Df = pd.DataFrame() # starts the result dataframe for each repetition
          
            projects_dictionary = {0: 22,
                                  1: 11,
                                  2: 9,
                                  3: 7,
                                  4: 5,
                                  5: 5,
                                  6: 3,
                                  7: 3,
                                  8: 2,
                                  9: 2,
                                  10: 2,
                                  11: 2,
                                  12: 2,
                                  13 : 1, 14 : 1, 15 : 1, 16 : 1, 17 : 1, 18 : 1, 19 : 1, 20 : 1, 21 : 1, 22 : 1, 23 : 1,
                                   24 : 1, 25 : 1, 26 : 1, 27 : 1, 28 : 1, 29 : 1}

            for i in range(N_of_firms): #This starts us with the number of firms
                if RANDOMIZE is True:
                    env.process(firm(env, 'Firm %d' % i, 0, 0, random.uniform(initial_tc_lower, initial_tc_upper), 
                                     random.uniform(initial_cc_lower, initial_cc_upper),
                                     math.ceil(initial_projects_total/(i+1)),
                                     math.ceil(initial_projects_total/(i+1)), 0, 0, 0))
                    #with this we have a geometric progression of projects, similar to our case

                    """elif SEMI_RANDOM is True: #TBD
                    initial_projects_total = random
                    env.process(firm(env, 'Firm %d' % i, 0, 0, random.uniform(initial_tc_lower, initial_tc_upper),
                                     random.uniform(initial_cc_lower, initial_cc_upper), initial_projects_total,
                                     initial_projects_total, 0, 0, 0)) 
                    #we produce N_of_firms firms with the previous parameters"""

                else:
                    env.process(firm(env, 'Firm %d' % i, 0, 0, random.uniform(initial_tc_lower, initial_tc_upper),
                                     random.uniform(initial_cc_lower, initial_cc_upper), projects_dictionary.get(i),
                                     projects_dictionary.get(i), 0, 0, 0))                    
            env.run(until=SIM_TIME) # we then run the simulation

            endDF = pd.concat([endDF, Df])
        
    
    endDF = endDF.rename(columns={0: "step", 1: "cc", 2: "tc", 3: "lc", 4: "# of BNDES financed projects", 
                                  5: "# of other banks financed projects", 6: "# of rounds without access to finance", 
                                  7: "# of projects yet to be financed", 8: "name", 9: "run",
                                 10: "internalisation_index", 11: 'rs'})
    
    return print('DONE')

'''
Course of action:
1- Firms attempt to finance their plants
2- Firms attempt to enhance their capabilities
3- BNDES analyses what happened and decides to lower, raise or maintain its requirements
4- Rinse and repeat
'''


def outside_firm(env):
    global LC
    global SIM_TIME
    global OKshare
    global PROJECTS_FINANCED_BNDES
    global INITIAL_NUMBER_OF_PROJECTS
    global SUM_OF_CC_t1
    global SUM_OF_TC_t1
    global SUM_OF_CC
    global SUM_OF_TC
    while True:
        if (env.now >= 1):
            global RS
            rs= RS
            SUM_OF_CC=SUM_OF_CC_t1
            SUM_OF_TC=SUM_OF_TC_t1
            numerator = PROJECTS_FINANCED_BNDES
            denominator = INITIAL_NUMBER_OF_PROJECTS
            Delta_lc = (numerator/denominator - OKshare)*(env.now/SIM_TIME)
            _LC = LC
            _LC *= (1+rs*Delta_lc)
            LC = _LC if (_LC<=1) else 0.99999999
            SUM_OF_CC_t1 = 0
            SUM_OF_TC_t1 = 0
        else:
            LC = np.random.normal(initial_lc_mean, initial_lc_variance) #the initial local content is established
            if LC<0:
                LC=0.00000001
            if LC>1:
                LC=0.99999999
            SUM_OF_CC=0
            SUM_OF_TC=0
            PROJECTS_FINANCED_BNDES=0
            INITIAL_NUMBER_OF_PROJECTS=0
            SUM_OF_CC_t1=0
            SUM_OF_TC_t1=0
        yield env.timeout(1)

def firm(env, name, fBNDES, fbanks, tc, cc, projects_total, projects_remaining, projects_financed_BNDES,
         projects_financed_bank, projects_failed_BNDES):
    
    while True:
        global SUM_OF_CC #put global to avoid problems...
        global SUM_OF_TC #again, put global to avoid problems...
        global LC
        global SIM
        global RS
        global PROJECTS_FINANCED_BNDES
        global INITIAL_NUMBER_OF_PROJECTS
        global SUM_OF_CC_t1
        global SUM_OF_TC_t1
        #attempting to finance power plants
        
        projects_financed_BNDES_tminus1 = projects_financed_BNDES
        if (tc>=1 and cc>=1 and env.now>0):
            fBNDES = np.random.poisson(np.floor(tc)) if projects_remaining>0 else 0
            #number of projects financed by BNDES
            if fBNDES>=1:
                projects_financed_BNDES += fBNDES if fBNDES<projects_remaining else projects_remaining
                projects_remaining -= fBNDES if fBNDES<projects_remaining else projects_remaining
            else:
                projects_failed_BNDES += 1 if projects_remaining>0 else 0
                fbank = np.random.poisson(np.floor(cc)) if projects_remaining>0 else 0
                if fbank>=1:
                    #number of projects financed by another bank
                    projects_financed_bank += fbank if fbank<projects_remaining else projects_remaining
                    projects_remaining -= fbank if fbank<projects_remaining else projects_remaining
        elif (tc>=1 and cc<1 and env.now>0):
            fBNDES = np.random.poisson(np.floor(tc)) if projects_remaining>0 else 0
            if fBNDES>=1:
                projects_financed_BNDES += fBNDES if fBNDES<projects_remaining else projects_remaining
                projects_remaining -= fBNDES if fBNDES<projects_remaining else projects_remaining
            else:
                projects_failed_BNDES += 1 if projects_remaining>0 else 0
        elif (tc<1 and cc>=1 and env.now>0):
            fbank = np.random.poisson(np.floor(cc)) if projects_remaining>0 else 0 
            #number of projects financed by another bank
            projects_failed_BNDES += 1 if projects_remaining>0 else 0
            projects_financed_bank += fbank if fbank<projects_remaining else projects_remaining
            projects_remaining -= fbank if fbank<projects_remaining else projects_remaining
        else:
            projects_failed_BNDES += 1 if projects_remaining>0 else 0
        
        PROJECTS_FINANCED_BNDES += projects_financed_BNDES - projects_financed_BNDES_tminus1
        responsivity = RS 
        # Revision of capabilities
        
        if env.now>0:
            cc_tminus1 = cc
            tc_tminus1 = tc
            alpha = ALPHA #small is internal to the firm CAPITAL IS THE OUTSIDE PARAMETER/VARIABLE
            beta = BETA
            sum_of_cc = SUM_OF_CC
            sum_of_tc = SUM_OF_TC
            EIcc = (cc/(cc+tc))/(sum_of_cc/(sum_of_cc+sum_of_tc)) 
            #efficiency index for the commercial capability
            EItc = (tc/(cc+tc))/(sum_of_tc/(sum_of_cc+sum_of_tc))
            #efficiency index for the technological capability
            tc += random.gammavariate(1, EIcc*beta*((1-LC)**alpha)) 
            # += means: the previous value plus something
            cc += random.gammavariate(1, EItc*beta*((LC)**alpha))
        SUM_OF_CC_t1 += cc
        SUM_OF_TC_t1 += tc
        
        #our firm has done everything it should, 
        #now we have to save what it did, or it will be lost, like tears in the rain
        
        if env.now>0:
            time_t.append(env.now)
            cc_t.append(cc)
            tc_t.append(tc)
            LC_t.append(LC)
            projects_financed_BNDES_t.append(projects_financed_BNDES)
            projects_financed_bank_t.append(projects_financed_bank)
            projects_failed_BNDES_t.append(projects_failed_BNDES)
            projects_remaining_t.append(projects_remaining)
            name_t.append(name)
            SIM_t.append(SIM)
            index_t.append(LC*(projects_financed_BNDES-projects_financed_BNDES_tminus1))
            responsivity_t.append(responsivity)
        else:
            time_t = [env.now]
            DfFirm = pd.DataFrame()
            cc_t = [cc]
            tc_t = [tc]
            LC_t = [LC]
            projects_financed_BNDES_t = [projects_financed_BNDES]
            projects_financed_bank_t = [projects_financed_bank]
            projects_failed_BNDES_t = [projects_failed_BNDES]
            projects_remaining_t = [projects_remaining]
            INITIAL_NUMBER_OF_PROJECTS += projects_remaining
            name_t = [name]
            SIM_t = [SIM]
            index_t = [LC*(projects_financed_BNDES-projects_financed_BNDES_tminus1)]
            responsivity_t = [responsivity]
                           
        if env.now == SIM_TIME-1:
            dict_firm = {0: time_t, 1: cc_t, 2: tc_t, 3: LC_t,4: projects_financed_BNDES_t,5: projects_financed_bank_t,
                         6: projects_failed_BNDES_t,7: projects_remaining_t
                         ,8: name_t,9: SIM_t,10: index_t,11:responsivity_t}
            DfFirm = pd.DataFrame(dict_firm)
            
        
        global Df #we have to indicate that the Df that it is looking is the global Df, not some local Df.
        Df = pd.concat([Df, DfFirm]) #then we concatenate this firm's a_row into the main dataframe.
        
        
        yield env.timeout(1) #until which step should this event occur? with 1 it occurs each step        
         

