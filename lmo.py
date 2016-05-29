
import numpy as np
import multiprocessing as mp
from scipy import signal
import matplotlib.pyplot as plt
import struct
import pdb
import time


def trc_lmo(trace,x,p,dt):

    ns = len(trace)
    timeLmo= (x*p)*1000 #Converting to msec
    nmLmo = np.round(timeLmo/dt)
    #print p,x,timeLmo,nmLmo
    
    trcLmo= trace[nmLmo:ns]

    trcLmo = np.lib.pad(trcLmo, (0,ns-len(trcLmo)), 
                        'constant', constant_values=(0))

    
    return trcLmo


'''
LINEAR MOVEOUT FOR A CDP-GATHER
'''
def gat_lmo(section,offsets,p,dt):
    nt = len(section[0,:])
    ns = len(section[:,0])
    SectionLmo = np.zeros(ns)
        
    for trace in range(0, nt):
        TrcLmo = trc_lmo(section[:,trace], offsets[trace],p,dt)
        SectionLmo = np.vstack((SectionLmo,TrcLmo))
            
    SectionLmo = SectionLmo[1:len(SectionLmo),:]
    #print "Leaving lmo module"
    return SectionLmo


'''
TAU-PI TRANSFORM FUNCTION FOR A GATHER
'''
def stkgat_lmo(section,offsets,p,dt):
    ns = len(section[:,0])
    SectionTauPi = np.zeros(ns)

    for pindex in np.arange(0,len(p)):
        #print p[pindex]
        sectionLmo = gat_lmo(section,offsets,p[pindex],dt)
        StkTrcLmo = np.sum(sectionLmo,axis=0)
        print "Processed p-SlantStack :", pindex
        SectionTauPi = np.vstack((SectionTauPi,StkTrcLmo))
        
    SectionTauPi = SectionTauPi[1:len(SectionTauPi),:]
    return SectionTauPi


'''
Functions for Linear move out Inversion
'''
    
def trc_lmo_inv(trace,x,p,dt):

    ns = len(trace)
    timeLmo= (x*p)*1000 #Converting to msec
    nmLmo = np.round(timeLmo/dt)
    print p,x,timeLmo,nmLmo
    
    trcLmo= trace[0:ns]

    trcLmo = np.lib.pad(trcLmo, (nmLmo,0), 
                        'constant', constant_values=(0))

    trcLmo= trcLmo[0:ns]
    
    return trcLmo

'''
INVERSE LINEAR MOVEOUT FUNCTION
'''
def gat_lmo_inv(section,offsets,p,dt):
    
    nt = len(section[0,:])
    ns = len(section[:,0])
    SectionLmo = np.zeros(ns)
    
    for trace in range(0, nt):
        TrcLmo = trc_lmo_inv(section[:,trace], offsets[trace],p,dt)
        SectionLmo = np.vstack((SectionLmo,TrcLmo))
            
    SectionLmo = SectionLmo[1:len(SectionLmo),:]
    #print "Leaving lmo module"
    return SectionLmo

'''
INVERSE P-trace Linear Moveout (tauPi)
'''
def trc_lmo_inv_tp(trace,x,p,dt):

    ns = len(trace)
    timeLmo= (x*p)*1000 #Converting to msec
    nmLmo = np.round(timeLmo/dt)
    #print p,x,timeLmo,nmLmo
    
    trcLmo= trace[0:ns]

    trcLmo = np.lib.pad(trcLmo, (nmLmo,0), 
                        'constant', constant_values=(0))

    trcLmo= trcLmo[0:ns]
    
    return trcLmo
'''
INVERSE LINEAR MOVEOUT FUNCTION OF TAUPi DOMAIN
'''
def gat_lmo_inv_tp(section,offsets,p,dt):
    
    nt = len(section[0,:])
    ns = len(section[:,0])
    SectionLmo = np.zeros(ns)
    
    for trace in range(0, nt):
        TrcLmo = trc_lmo_inv_tp(section[:,trace], offsets,p[trace],dt)
        SectionLmo = np.vstack((SectionLmo,TrcLmo))
            
    SectionLmo = SectionLmo[1:len(SectionLmo),:]
    #print "Leaving lmo module"
    return SectionLmo


'''
INVERSE TAUPI TRANSFORM
'''
def stkgat_lmo_Inv(section,offsets,p,dt):
    ns = len(section[:,0])
    SectionTauPiinv = np.zeros(ns)

    for pindex in np.arange(0,len(offsets)):
        #print p[pindex]
        sectionLmo = gat_lmo_inv_tp(section,offsets[pindex],p,dt)
        StkTrcLmo = np.sum(sectionLmo,axis=0)
        print "Processed pInv-SlantStack :", pindex
        SectionTauPiinv = np.vstack((SectionTauPiinv,StkTrcLmo))
        
    SectionTauPiinv = SectionTauPiinv[1:len(SectionTauPiinv),:]
    return SectionTauPiinv
