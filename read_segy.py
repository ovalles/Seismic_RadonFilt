# by Asdrubal Ovalles 2016

import numpy as np
import multiprocessing as mp
from scipy import signal
import matplotlib.pyplot as plt
import struct
import pdb
import time

def nsamp_segy(filein):
   file=open(filein, 'rb')
   bytepos=3220
   file.seek(bytepos,0)
   #nsamp=np.array(struct.unpack(('H'),file.read(2)))   #NATIVE ENDIANNES
   nsamp=np.array(struct.unpack(('>H'),file.read(2)))  # BIG-ENDIAN FILE
   file.close()
   #print nsamp
   return nsamp

def dt_segy(filein):
   file=open(filein, 'rb')
   bytepos=3216
   file.seek(bytepos,0)
   dt=np.array(struct.unpack(('>H'),file.read(2)))
   file.close()
   #print dt
   return dt   

def ntraces(filein):

   file=open(filein, 'rb').read()
   FileSize = len(file)
   ns = nsamp_segy(filein)
   nt = (FileSize -3600)/(240 + 4*ns)
#   close(filein)
   #print nt
   return nt
   
def read_segy(filein):
   #nt = ntraces(filein)
   #ns = nsamp_segy(filein)
#   #print nt, ns
   y=np.zeros(ns)
   Section=np.zeros(ns)
 
   file=open(filein,'rb')
   j=0
   while (j<nt-1):
      bytepos=3600+240*(j+1)+(4*ns*j)
      #print '',bytepos
      file.seek(bytepos,0)
      i=0
      while (i<=ns-1):
#      y.append(struct.unpack(('f'),file.read(4)))   #Apendiza en listas
         y[i]=np.array(struct.unpack(('>f'),file.read(4)))
         i=i+1
      Section=np.vstack((Section,y))
      j=j+1
   file.close()
   return Section


def read_segy_trunc(filein,nto,ntf,nso,nsf):
   #nt = ntraces(filein)
   ns = nsamp_segy(filein)
   print 'Esto es read SEGY ',nto,ntf,nso, nsf
   y=np.zeros(nsf)
   Section=np.zeros(nsf)
 
   file=open(filein,'rb')
   j=nto
   while (j<ntf-1):
      bytepos=3600+240*(j+1)+(4*ns*j) + 4*nso
      #print '',bytepos
      file.seek(bytepos,0)
      i=nso
      while (i<=nsf-1):
#      y.append(struct.unpack(('f'),file.read(4)))   #Apendiza en listas
         y[i]=np.array(struct.unpack(('>f'),file.read(4)))
         i=i+1
      Section=np.vstack((Section,y))
      j=j+1
   file.close()
   #pdb.set_trace()
   Section = Section[:,nso:nsf]
   return Section


def read_segy_record(filein,rec_num,fold):

   #nt = ntraces(filein)
   ns = nsamp_segy(filein)
   y=np.zeros(ns)
   Section=np.zeros(ns)
 
   file=open(filein,'rb')
   bytepos_inic = 3600+240*(rec_num-1)*fold+4*ns*(rec_num-1)*fold
   #print 'Posicion de byte', bytepos_inic
   j=0
   while (j<fold):
      bytepos=bytepos_inic+240*(j+1)+(4*ns*j)
      file.seek(bytepos,0)
      i=0
      while (i<=ns-1):
#      y.append(struct.unpack(('f'),file.read(4)))   #Apendiza en listas
         y[i]=np.array(struct.unpack(('>f'),file.read(4)))
         i=i+1
      Section=np.vstack((Section,y))
      j=j+1
   file.close()
   Section = Section[1:len(Section[:,1]),:]
   #print 'Section Shape', Section.shape
   return Section



def read_segy_offset(filein,rec_num,fold):

   #nt = ntraces(filein)
   ns = nsamp_segy(filein)
   offset=np.zeros(fold)
   #Section=np.zeros(ns)
 
   file=open(filein,'rb')
   bytepos_inic = 3600+240*(rec_num-1)*fold+4*ns*(rec_num-1)*fold-204
   #print 'Posicion de byte', bytepos_inic
   j=0
   while (j<fold):
      bytepos=bytepos_inic+240*(j+1)+(4*ns*j)
      file.seek(bytepos,0)
      offset[j]=np.array(struct.unpack(('>i'),file.read(4)))
      j=j+1
   file.close()
   #print 'Offset Shape', offset.shape
   return offset
