#!/usr/bin/env python

# TAUPI FILTERING applied to Seismic Data
# by Asdrubal Ovalles, Luis Martinez, Ilich Garcia
# 2016, April
# ovallesa@me.com


import gtk
from matplotlib.figure import Figure
import pygtk
pygtk.require('2.0')
import matplotlib.pyplot as plt
import read_segy
import numpy as np
import pdb
from matplotlib import path
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar


def trace_lmo(trace,Shift_nm,ns):
    if Shift_nm > ns:
       Shift_nm = ns-1 
    tracelmo=trace[Shift_nm:ns]
    tracelmo = np.append(tracelmo,np.zeros(Shift_nm))
    return tracelmo

def gather_lmo(section,Shift_nm,ns):
    nt = len(section[0,:])
    gatherlmo = np.zeros([ns,nt])
    for trace in range(0,len(Shift_nm)):
	gatherlmo[:,trace] = trace_lmo(section[:,trace],Shift_nm[trace],ns)
    return gatherlmo

def gathers_lmo(section,Shift_nm,ns): #section y Shift_nm (matrices) y ns escalar
    nt = len(section[0,:])
    gatherslmo = np.zeros([ns,nt,len(Shift_nm[0,:])])
    for trace in range (0, len(Shift_nm[0,:])):
        gatherslmo[:,:,trace] = gather_lmo(section,Shift_nm[:,trace],ns) #gatherslmo (cubo matricial)
    return gatherslmo

def trace_invlmo(trace,Shift_nm,ns): #trace(vector), Shift_nm y ns (escalar)
    trace=np.append(np.zeros(Shift_nm),trace) # anado zeros por arriba
    traceinvlmo=trace[0:ns] #mantengo dimensiones
    return traceinvlmo

def gather_invlmo(section,Shift_nm,ns): #section (matriz), Shift_nm (vector), ns (escalar)
    nt = len(section[0,:])
    gatherinvlmo = np.zeros([ns,nt])
    for trace in range(0,len(Shift_nm)):
	    gatherinvlmo[:,trace] = trace_invlmo(section[:,trace],Shift_nm[trace],ns)
    return gatherinvlmo

def gathersinv_lmo(section,Shift_nm,ns): #section y Shift_nm (matrices) y ns escalar
    nt = len(section[0,:])
    gathersinvlmo = np.zeros([ns,nt,len(Shift_nm[0,:])])
    for trace in range (0, len(Shift_nm[0,:])):
        gathersinvlmo[:,:,trace] = gather_invlmo(section,Shift_nm[:,trace],ns) #gatherslmo (cubo matricial)
    return gathersinvlmo

def mutefilt(sectiontaupi,Coords,Ns,Nt):
    '''
    This function make a mute of the undesired portion
    in the TauPi panel. A mute  function must be prior 
    interactively designed in the TauPi panel. AJ
    '''

    ntraces,nsamples = sectiontaupi.shape
    sectionTaupiMute = np.zeros((nsamples,ntraces))
    pachi = path.Path(Coords)  # Creating the polygon vertex. AJ
    
    for trace in range(0,ntraces):
        for sample in range(0,nsamples):

            '''
            Is a point inside a poligon?
            '''
            inpoly = pachi.contains_points([(sample, trace)]) 
            if inpoly[0] == True:
                sectionTaupiMute[sample,trace] = 1
            else:
                sectionTaupiMute[sample,trace] = 0
                

    sectionTaupiMute = sectionTaupiMute.T
    sectionTaupiMute = sectiontaupi * sectionTaupiMute
    '''
    It is a great place to watch the filtered
    TauPi panel after mute. AJ
    '''
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.matshow(sectionTaupiMute)
    plt.show()
    '''
    return sectionTaupiMute


def onclickSeis(event):

    '''
    print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          (event.button, event.x, event.y, event.xdata, event.ydata))
    '''

def onclickFilt(event):
    '''
    It is a callback function which pick the points selected
    interactively by user in the TauPi panel. AJ
    '''

    global coords,ns,dt
    '''
    print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          (event.button, event.x, event.y, event.xdata, event.ydata))
    '''
    ix, iy = event.xdata, event.ydata/dt   
    coords.append((int(ix), int(iy)))
    #print 'Coordenadas picadas ',coords

    return coords
    

def seisDisplay(Seismic, Title, Xlabel, Ylabel,xMin,xMax,yMin,yMax,palette):
    '''
    It is the function which plot a embeed seismic data in GTK window. AJ
    '''

    figInput = plt.figure(figsize=(4, 4.5), dpi=100)  
    figInput.set_facecolor('white')
    figSection = figInput.add_subplot(111)
    plt.rcParams.update({'font.size': 06})
    plt.title(Title)
    plt.xlabel(Xlabel)
    plt.ylabel(Ylabel)
    figSection.imshow(Seismic, extent=[xMin, xMax, yMax, yMin], 
                      cmap=palette)
    figSection.set_aspect('auto')

    canvas = FigureCanvas(figInput)  # a gtk.DrawingArea
    hboxDisplay.pack_start(canvas)
    
    figInput.canvas.mpl_connect('button_press_event', onclickSeis)

    hboxDisplay.show_all()


def filtDisplay(Seismic, Title, Xlabel, Ylabel,xMin,xMax,yMin,yMax,palette):
    '''
    It is the function which plot a embeed TauPi  transform 
    data in GTK window. It is connected to picking callback
    function. AJ
    '''

    figInput = plt.figure(figsize=(4, 4.5), dpi=100)  
    figInput.set_facecolor('white')
    figSection = figInput.add_subplot(111)

    plt.rcParams.update({'font.size': 06})
    plt.title(Title)
    plt.xlabel(Xlabel)
    plt.ylabel(Ylabel)
    
    figSection.imshow(Seismic, extent=[xMin, xMax, yMax, yMin], 
                      cmap=palette)
    figSection.set_aspect('auto')

    #plt.show()
    
    canvas = FigureCanvas(figInput)  # a gtk.DrawingArea
    hboxDisplay.pack_start(canvas)
    
    figInput.canvas.mpl_connect('button_press_event', onclickFilt)

    line, = figSection.plot([0], [0])  # empty line
    linebuilder = LineBuilder(line)

    hboxDisplay.show_all()

class LineBuilder:
    '''
    This class plots the line segments in the TauPiPanel. AJ
    '''
    def __init__(self, line):
        self.line = line
        self.xs = list(line.get_xdata())
        self.ys = list(line.get_ydata())
        self.cid = line.figure.canvas.mpl_connect('button_press_event', self)

    def __call__(self, event):
        print('click', event)
        if event.inaxes!=self.line.axes: return
        self.xs.append(event.xdata)
        self.ys.append(event.ydata)
        self.line.set_data(self.xs, self.ys)
        self.line.figure.canvas.draw()
    
    


def on_loadSegy_clicked(widget):
    '''
    This button callback function loads the SEGY file. AJ
    '''

    global Imagehbox, Section, Record, Nrecord, Fold,nt,ns,dt, Offset, dt_s, tmax_ms, hboxDisplay, coords
    global FileIn, SectionTauPi, SectionFilt, p0, nume

    FileIn = entryFileIn.get_text()       #SEGY file name
    Nrecord = 1901                             #Number of CDP-Gathers
    Record = int(entryRecord.get_text())
    Fold = int(entryFold.get_text())      #Fold of the CDP-Record
    nt=read_segy.ntraces(FileIn)               #Number of traces in SEGY file
    ns=read_segy.nsamp_segy(FileIn)            #Number of samples per trace
    dt=int(read_segy.dt_segy(FileIn))/1000     #Sample rate (ms)
    dt_s = dt/1000.0                           #Sample rate (s) heavily used


    Section=read_segy.read_segy_record(FileIn,Record,Fold)
    Section=Section.T  # Section es la Matriz que contiene las trazas del CDP


    Offset=read_segy.read_segy_offset(FileIn,Record,Fold)  #List containing the
    coords = []  # Reseting the picked coords if youre loading a new gather :). AJ

    # Destroying seismic panels if youre loading a new gather :). AJ
    hboxDisplay.destroy()    
    hboxDisplay = gtk.HBox(False, 0)
    hboxDisplay.show()
    hbox.pack_start(hboxDisplay)
    
    # Displaying embeded seismic section. AJ
    seisDisplay(Section,'Input CDP' ,'Offset [m]' ,'Time [ms]' ,
                Offset[0],Offset[Fold-1],0,int((ns-1)*dt),plt.cm.gray)



def on_buttonNext_clicked(widget):

    Incr = int(entryIncrement.get_text())
    Record = int(entryRecord.get_text())
    entryRecord.set_text(str(Record+Incr))

    loadSegy.clicked()


def on_buttonSlantStack_clicked(widget):
    '''
    This button callback function perform the TauPi
    Transform. AJ
    '''
    global Section, Offset, SectionTauPi, ns, Fold, nt, dt, shift_nm, p0, nume

    SectionTauPi = Section
    coords = []

    Section = Section #matriz ns x nt
    Offset = Offset #vector offset de cda traza

   # p = np.linspace(0, (1.00000 / 1500), num=200)

    vel = int(entrypfactor.get_text())
    nume = int(entrynum.get_text())
    
    p_user = 1.0000 / vel
    p0 = np.linspace(0, p_user, num=nume) #construyo el vector p0 (barrido de Velocidades o de p)

    shift = np.zeros([len(Offset),len(p0)])
    for j in range(0,len(p0)):
        shift[:,j] = p0[j]*Offset

    shift_ms = shift * 1000
    shift_nm = np.round(shift_ms/dt)

    GathersLMO = gathers_lmo(Section,shift_nm,ns)
    SectionTaupi=np.zeros(GathersLMO[:,:,0].shape)
    for a in range(0,len(GathersLMO[0,0,:])):
        SectionTaupi[:,a]=np.sum(GathersLMO[:,:,a],axis=1)

    SectionTauPi=SectionTaupi

    filtDisplay(SectionTauPi,'Input CDP' ,'ray parameter','Time [ms]' ,
                0,nume-1,0,int((ns-1)*dt),
                plt.cm.jet)


def on_buttonFilter_clicked(widget):
    '''
    This   button  callback  function  performs  the
    inverse-transform of TauPi and lead to the filtered 
    seismic. AJ
    '''
    global Section, Offset, SectionTauPi, SectionFilt, ns, Fold, nt, dt
    global coords

    coords.insert(0,(0,0))
    coords.append((0,ns))


    #GatherinvLMO = gather_invlmo(SectionTauPi,shift_nm[:,199],ns)

    shift = np.zeros([len(p0),len(Offset)])
    for j in range(0,len(Offset)):
        shift[:,j] = p0*Offset[j]
    shift_ms = shift * 1000
    shift_nm = np.round(shift_ms/dt)

    
    # Applying Mute poligon to SectionTauPi. AJ
    
    if len(coords) == 2:
        SectionTauPiMute = SectionTauPi #The user pick nothing. :/ AJ
    else:
        SectionTauPiMute = mutefilt(SectionTauPi,coords,ns,nt)
    
    GathersinvLMO = gathersinv_lmo(SectionTauPiMute,shift_nm,ns)

    SectionFilt=np.zeros(GathersinvLMO[:,:,0].shape)
    for a in range(0,len(GathersinvLMO[0,0,:])):
        SectionFilt[:,a]=np.sum(GathersinvLMO[:,:,a],axis=1)


    seisDisplay(SectionFilt,'Input CDP' ,'Offset [m]' ,'Time',
                Offset[0],Offset[Fold-1],0,int((ns-1)*dt),plt.cm.gray)
    

    

######################### main ()  ###################################
'''
Initializing coords To store interactively 
picked points from Taupi panel. AJ
'''
coords = [] 

win = gtk.Window()
win.connect("destroy", lambda x: gtk.main_quit())
win.set_default_size(1200,400)
win.set_title("TauPi Filtering by Seismic Processing Toys, Vzla 2016")

hbox = gtk.HBox(False, 0)
hbox.show()
win.add(hbox)

tablePar = gtk.Table(16,4,False)
tablePar.show()
hbox.pack_start(tablePar,expand=False, fill=False, padding=0)

hboxDisplay = gtk.HBox(False, 0)
hboxDisplay.show()
hbox.pack_start(hboxDisplay)

labelfile = gtk.Label("Input File: ")
labelfile.show()
tablePar.attach(labelfile, 0, 4, 1, 2)

entryFileIn = gtk.Entry()
entryFileIn.set_text("CDPNMOSyn200t_801m.sgy")
entryFileIn.show()
tablePar.attach(entryFileIn, 0, 4, 2, 3)

labelfold = gtk.Label("Fold: ")
labelfold.show()
entryFold = gtk.Entry()
entryFold.set_text("200")
entryFold.show()
tablePar.attach(labelfold, 0, 2, 3, 4)
tablePar.attach(entryFold, 2, 4, 3, 4)

labelrecord = gtk.Label("CDP: ")
labelrecord.show()
entryRecord = gtk.Entry()
entryRecord.set_text("1")
entryRecord.show()
tablePar.attach(labelrecord, 0, 2, 4, 5)
tablePar.attach(entryRecord, 2, 4, 4, 5)

loadSegy = gtk.Button(label="Load CDP")
loadSegy.show()
tablePar.attach(loadSegy, 0, 4, 5, 6)
loadSegy.connect("clicked", on_loadSegy_clicked)

labelIncrement = gtk.Label("CDP Increment: ")
labelIncrement.show()
entryIncrement = gtk.Entry()
entryIncrement.set_text("200")
entryIncrement.show()
tablePar.attach(labelIncrement, 0, 3, 6, 7)
tablePar.attach(entryIncrement, 3, 4, 6, 7)


buttonNext = gtk.Button(label="Next CDP")
buttonNext.show()
tablePar.attach(buttonNext, 0, 4, 7, 8)
buttonNext.connect("clicked", on_buttonNext_clicked)


labelpfactor = gtk.Label("Lowest Velocity: ")
labelpfactor.show()
entrypfactor = gtk.Entry()
entrypfactor.set_text("1500")
entrypfactor.show()
tablePar.attach(labelpfactor, 0, 2, 8, 9)
tablePar.attach(entrypfactor, 3, 4, 8, 9)

labelnum = gtk.Label("Number of p: ")
labelnum.show()
entrynum = gtk.Entry()
entrynum.set_text("200")
entrynum.show()
tablePar.attach(labelnum, 0, 2, 9, 10)
tablePar.attach(entrynum, 3, 4, 9, 10)


buttonSlantStack = gtk.Button(label="Show TauPi Transform")
#buttonSlantStack.set_usize(5,5)
buttonSlantStack.show()
tablePar.attach(buttonSlantStack, 0, 4, 10, 11)
buttonSlantStack.connect("clicked", on_buttonSlantStack_clicked)

'''
button = gtk.RadioButton(None, "Pass")
button.connect("toggled", callback, "Pass")
tablePar.attach(button, True, True, 0)
button.show()
   	
button = gtk.RadioButton(button, "Reject")
button.connect("toggled", callback, "Reject")
button.set_active(True)
box2.pack_start(button, True, True, 0)
button.show()
'''

buttonFilter = gtk.Button(label="Apply Filter")
buttonFilter.show()
tablePar.attach(buttonFilter, 0, 4, 11, 12)
buttonFilter.connect("clicked", on_buttonFilter_clicked)

'''
buttonExport = gtk.Button(label="Export Filtered SEGY")
buttonExport.show()
tablePar.attach(buttonExport, 0, 4, 12, 13)
buttonExport.connect("clicked", on_buttonExport_clicked)
'''

#window.connect("destroy", lambda w: gtk.main_quit())


win.show_all()
gtk.main()
