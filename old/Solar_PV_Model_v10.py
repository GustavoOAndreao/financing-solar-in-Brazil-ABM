#!/usr/bin/env python
# coding: utf-8

# In[1]:
import random    
import feather
import simpy
import numpy as np
import pandas as pd
import math as math

def run_simulation(fALPHA, fBETA, finitial_tc_upper, finitial_tc_lower, finitial_cc_upper, finitial_cc_lower, finitial_projects_total, finitial_lc_mean, finitial_lc_variance, fOKshare, fSIM_TIME, fRANDOM_SEED, fNUMBER_OF_REPETITIONS, fresponsivities, fDICT_DF):
    

    '''
    This prevents the simulation from crashing: we are setting global variables, i.e., ALPHA points to fALPHA in every object, function etc.
    '''
    
    global ALPHA
    global BETA
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
    global DICT_DF
    
    '''
    We must tell the simulation that the parameters are the function's inputs
    '''
    #Parameter_in_the_smiulation = function_input
    ALPHA = fALPHA
    BETA = fBETA
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
    OKshare = fOKshare
    responsivities = fresponsivities
    DICT_DF = fDICT_DF
           
    global endDF
    endDF = pd.DataFrame() #we have to set a initial main dataframe
    
    '''
    We have to do three loops in the simulation process:
    #1 loop: changes the random seed and tell us where the simulation is (it is the repetition)
    #2 loop: changes the responsivity, starts the environment and produces the outside_firm process
    #3 loop: intialises the firms, runs the simulation and concatenates the resulting (Df) dataframe to the main dataframe (endDF)
    '''
    for rep in range (RANDOM_SEED, RANDOM_SEED + NUMBER_OF_REPETITIONS): #the +1 produces 1 repetition
        random.seed(rep) #in order to have pseudo-random numbers, allowing greater replicability
        np.random.seed(rep) #we have to set both random.seed and np.random.seed: they are different packages, as such they both must be initialised
        global SIM
        SIM = rep
        print(round(SIM/NUMBER_OF_REPETITIONS , 4), end = '...') #printing the status of the simulation
        
        for j in responsivities:
            RS = j
            env = simpy.Environment() #starts the environment in each iteration
            env.process(outside_firm(env)) #starts the outside_firm process

            global Df
            Df = pd.DataFrame() # starts the result dataframe for each repetition
            
            '''
            This is a dictionary to assign each project to its respective firm: the firm 0 is Enel, firm 1 is canandian, and so forth. It follows the table in our article
            '''
            
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
                                  13 : 1, 14 : 1, 15 : 1, 16 : 1, 17 : 1, 18 : 1, 19 : 1, 20 : 1, 21 : 1, 22 : 1, 23 : 1, 24 : 1, 25 : 1, 26 : 1, 27 : 1, 28 : 1, 29 : 1}

            #we first produce Enel: it has 
            env.process(firm(env, 'Firm 1', 0, 0, random.uniform(initial_tc_lower, initial_tc_upper), random.uniform(initial_tc_lower, initial_tc_upper), 22, 22, 0, 0, 0))
            
            '''
            it follows the function underneath:
            def firm(env, name, fBNDES, fbanks, tc, cc, projects_total, projects_remaining, projects_financed_BNDES, projects_financed_bank, projects_failed_BNDES)
            '''
            
            for i in range(1, 29): #This starts us with the number of firms
                env.process(firm(env, 'Firm %d' % i, 0, 0, random.uniform(initial_tc_lower, initial_tc_upper), random.uniform(initial_cc_lower, initial_cc_upper), projects_dictionary.get(i), projects_dictionary.get(i), 0, 0, 0))                    
        
            
            env.run(until=SIM_TIME) # we then run the simulation

            endDF = pd.concat([endDF, Df]) #we concatenate that specific run's simulation with the final table
    
    #we run those lines to rename the columns according to the recorded variables
    _DICT_DF = DICT_DF #first we get the variable from the input
    arguments = ['time_t', 'SIM_t', 'rs_t'] #we select these three arguments that must always be present regardless of what variables we want to observe
    for i in range(len(_DICT_DF)): #len() is lenght, i.e., the number of elements in that list
        arguments.append(_DICT_DF[i]) #we are appending the names of the variables that we want to observe along with the arguments list
        dict_firm = dict((_,arguments[_]) for _ in range(len(arguments))) #we produce a dict {number : name} for each variable in the argument list
    
    endDF = endDF.rename(columns=dict_firm) #lastly we rename the columns in our final table
    
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
        if (env.now >= 1): #things that we have to do after the first step
            global RS
            rs= RS
            SUM_OF_CC=SUM_OF_CC_t1 #we are matching the next period's sums with the current, i.e., the step is passing by for that variable
            SUM_OF_TC=SUM_OF_TC_t1
            numerator = PROJECTS_FINANCED_BNDES
            denominator = INITIAL_NUMBER_OF_PROJECTS
            Delta_lc = (numerator/denominator - OKshare)*(env.now/SIM_TIME)
            _LC = LC
            _LC *= (1+rs*Delta_lc)
            LC = _LC if (_LC<=1) else 0.99999999 #the next lines are to make sure that LC stays between (0,1)
            SUM_OF_CC_t1 = 0 #we now reset the sums for the next period, in order for the companies to change it
            SUM_OF_TC_t1 = 0
        else:
            LC = np.random.normal(initial_lc_mean, initial_lc_variance) #the initial local content is established
            if LC<0:
                LC=0.00000001
            if LC>1:
                LC=0.99999999
            #we have to initialised 
            SUM_OF_CC=0
            SUM_OF_TC=0
            PROJECTS_FINANCED_BNDES=0
            INITIAL_NUMBER_OF_PROJECTS=0
            SUM_OF_CC_t1=0
            SUM_OF_TC_t1=0
        yield env.timeout(1)

def firm(env, name, fBNDES, fbanks, tc, cc, projects_total, projects_remaining, projects_financed_BNDES, projects_financed_bank, projects_failed_BNDES):
    
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
        _LC = LC
        
        projects_financed_BNDES_tminus1 = projects_financed_BNDES
        if ((tc/_LC)>=1 and cc>=1 and env.now>0):
            fBNDES = np.random.poisson(np.floor(tc/(1+_LC))) if projects_remaining>0 else 0
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
        elif ((tc/_LC)>=1 and cc<1 and env.now>0):
            fBNDES = np.random.poisson(np.floor(tc/(1+_LC))) if projects_remaining>0 else 0
            if fBNDES>=1:
                projects_financed_BNDES += fBNDES if fBNDES<projects_remaining else projects_remaining
                projects_remaining -= fBNDES if fBNDES<projects_remaining else projects_remaining
            else:
                projects_failed_BNDES += 1 if projects_remaining>0 else 0
        elif ((tc/_LC)<1 and cc>=1 and env.now>0):
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
            alpha = ALPHA #small is internal to the firm CAPITAL IS THE OUTSIDE PARAMETER/VARIABLE
            beta = BETA
            sum_of_cc = SUM_OF_CC
            sum_of_tc = SUM_OF_TC
            EIcc = (cc/(cc+tc))/(sum_of_cc/(sum_of_cc+sum_of_tc)) 
            #efficiency index for the commercial capability
            EItc = (tc/(cc+tc))/(sum_of_tc/(sum_of_cc+sum_of_tc))
            #efficiency index for the technological capability
            tc += random.gammavariate(1, EItc*beta*((1-LC)**alpha)) 
            # += means: the previous value plus something
            cc += random.gammavariate(1, EIcc*beta*((LC)**alpha))
        SUM_OF_CC_t1 += cc
        SUM_OF_TC_t1 += tc
        
        #our firm has done everything it should, now we have to save what it did, or it will be lost, like tears in the rain
        
        if env.now>0:
            time_t.append(env.now)
            SIM_t.append(SIM)
            rs_t.append(responsivity)
            cc_t_add.append(cc - cc_t[-1])
            cc_t.append(cc)
            tc_t_add.append(tc - tc_t[-1])            
            tc_t.append(tc)
            LC_t_add.append(LC - LC_t[-1])            
            LC_t.append(LC)
            proj_fin_BNDES_t_add.append(projects_financed_BNDES - proj_fin_BNDES_t[-1])
            proj_fin_BNDES_t.append(projects_financed_BNDES)
            proj_fin_bank_t_add.append(projects_financed_bank - proj_fin_bank_t[-1])
            proj_fin_bank_t.append(projects_financed_bank)
            proj_fail_BNDES_t_add.append(projects_failed_BNDES - proj_fail_BNDES_t[-1])
            proj_fail_BNDES_t.append(projects_failed_BNDES)
            proj_remain_t_add.append(projects_remaining - proj_remain_t_add[-1])
            proj_remain_t.append(projects_remaining)
            name_t.append(name)
            ii_t_add.append(ii_t[-1] + LC*(projects_financed_BNDES-projects_financed_BNDES_tminus1))
            ii_t.append(LC*(projects_financed_BNDES-projects_financed_BNDES_tminus1))
        else:
            DfFirm = pd.DataFrame()
            INITIAL_NUMBER_OF_PROJECTS += projects_remaining
            time_t = [env.now]
            SIM_t = [SIM]
            rs_t = [responsivity]
            cc_t = [cc]
            cc_t_add = [0]
            tc_t = [tc]
            tc_t_add = [0]
            LC_t = [LC]
            LC_t_add = [0]
            proj_fin_BNDES_t = [projects_financed_BNDES]
            proj_fin_BNDES_t_add = [0]
            proj_fin_bank_t = [projects_financed_bank]
            proj_fin_bank_t_add = [0]
            proj_fail_BNDES_t = [projects_failed_BNDES]
            proj_fail_BNDES_t_add = [0]
            proj_remain_t = [projects_remaining]
            proj_remain_t_add = [0]
            name_t = [name]
            ii_t = [LC*(projects_financed_BNDES-projects_financed_BNDES_tminus1)]
            ii_t_add = [LC*(projects_financed_BNDES-projects_financed_BNDES_tminus1)]
                       
        if env.now == SIM_TIME-1:
            global DICT_DF
            _DICT_DF = DICT_DF
            
            output_dictionary1={'cc_t' : 0,'tc_t' : 1,'LC_t' : 2,'proj_fin_BNDES_t' : 3,'proj_fin_bank_t' : 4,'proj_fail_BNDES_t' : 5,'proj_remain_t' : 6, 'ii_t_add' : 7, 'cc_t_add' : 8, 'tc_t_add' : 9,  'LC_t_add' : 10, 'proj_fin_BNDES_t_add' : 11, 'proj_fin_bank_t_add' : 12, 'proj_fail_BNDES_t_add' : 13, 'proj_remain_t_add' : 14, 'ii_t' : 15}
            output_dictionary2={0 : cc_t,1 : tc_t, 2 : LC_t, 3 : proj_fin_BNDES_t, 4: proj_fin_bank_t, 5 : proj_fail_BNDES_t, 6 : proj_remain_t, 7 : ii_t_add, 8 : cc_t_add, 9 : tc_t_add, 10 :  LC_t_add, 11 : proj_fin_BNDES_t_add, 12 : proj_fin_bank_t_add, 13 : proj_fail_BNDES_t_add, 14 : proj_remain_t_add, 15 : ii_t}
            
            
            arguments = [time_t, SIM_t, rs_t]
            for i in range(len(_DICT_DF)):
                arguments.append(output_dictionary2.get(output_dictionary1.get(_DICT_DF[i])))

            dict_firm = dict((_,arguments[_]) for _ in range(len(arguments)))         
            
            
            
            # old dict -> {0: time_t,1: cc_t, 2: tc_t, 3: LC_t,4: projects_financed_BNDES_t,5: projects_financed_bank_t, 6: projects_failed_BNDES_t,7: projects_remaining_t ,8: name_t,9: SIM_t,10: index_t,11:responsivity_t}
            DfFirm = pd.DataFrame(dict_firm)
            
        
        global Df #we have to indicate that the Df that it is looking is the global Df, not some local Df.
        Df = pd.concat([Df, DfFirm]) #then we concatenate this firm's a_row into the main dataframe.
        
        
        yield env.timeout(1) #until which step should this event occur? with 1 it occurs each step