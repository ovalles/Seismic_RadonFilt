#!/usr/bin/env python

# RADON FILTERING applied to Seismic Data
# by Asdrubal Ovalles, Luis Martinez, Ilich Garcia
# 2016, April
# ovallesa@me.com , 

import pygtk
pygtk.require('2.0')
import gtk
import matplotlib.pyplot as plt
import read_segy
import variables
import numpy as np
import pdb

# Backing pixmap for drawing area
pixmap = None

# Create a new backing pixmap of the appropriate size
def configure_event(widget, event):
    global pixmap

    x, y, width, height = widget.get_allocation()
    #print width, height
    pixmap = gtk.gdk.Pixmap(widget.window, width, height)

    #Cargo mi imagen de fondo en un pixbux  
    pix = gtk.gdk.pixbuf_new_from_file("Filter.png")
    pix = pix.scale_simple(300, 500, gtk.gdk.INTERP_BILINEAR)
    #Tapizo la superfificie dibujable pixmap con la imagen del pixbuf  
    pixmap.draw_pixbuf(None, 
                       pix, 0, 0, 0, 0, width=-1, height=-1, 
                       dither=gtk.gdk.RGB_DITHER_NORMAL, x_dither=0, y_dither=0)
                       
    return True

# Redraw the screen from the backing pixmap
def expose_event(widget, event):
    x , y, width, height = event.area
    widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL],
                                pixmap, x, y, x, y, width, height)


    return False

# Draw a rectangle on the screen
def draw_brush(widget, x, y):
    rect = (int(x-5), int(y-5), 8, 8)
    pixmap.draw_rectangle(widget.get_style().white_gc, True,
                          rect[0], rect[1], rect[2], rect[3])
    widget.queue_draw_area(rect[0], rect[1], rect[2], rect[3])
 
def button_press_event(widget, event):

    if event.button == 1 and pixmap != None:
        draw_brush(widget, event.x, event.y)
        variables.xpick.append(event.x)
        variables.ypick.append(event.y)
    print "Printing clicking locations x,y: ",variables.xpick, variables.ypick
    return True

def motion_notify_event(widget, event):
    if event.is_hint:
        x, y, state = event.window.get_pointer()
        #print event.x, event.y
    else:
        x = event.x
        y = event.y
        state = event.state
    
    if state & gtk.gdk.BUTTON1_MASK and pixmap != None:
        draw_brush(widget, x, y)
    
    return True

# CREATES PNG FILES FROM DATA MATRIXs AND DISPLAY IT
def on_redisplay(widget):
    global Section, SectionTauPi, SectionFilt, Fold, ns, nt
    global dt, dt_s

    main.tableDis.destroy()
    main.tableDis = gtk.Table(2,3,False)
    main.tableDis.show()
    main.hbox.pack_start(main.tableDis)

    try:
        SectionTauPi.shape
    except NameError:
        SectionTauPi = Section
	#print "Entre a la excepcion"

    try:
        SectionFilt.shape
    except NameError:
        SectionFilt = Section
    
    # 3 PNG Files to display
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(Section,extent=[Offset[0],Offset[Fold-1],int((ns-1)*dt),0], cmap='gray')
    ax.set_xlim(Offset[0], Offset[Fold-1])
    ax.set_aspect(0.5)
    #plt.colorbar()
    plt.title('Input CDP')    
    plt.xlabel('Offset [m]')
    plt.ylabel('Time [ms]')
    fig.savefig('Input.png', bbox_inches='tight')
    fig.clf()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(SectionTauPi,extent=[Offset[0],Offset[Fold-1],int((ns-1)*dt),0]) 
    ax.set_xlim(Offset[0], Offset[Fold-1])
    ax.set_aspect(0.5)
    #plt.colorbar()
    plt.title('Picking Filter Panel')    
    plt.xlabel('Offset [m]')
    plt.ylabel('Time [ms]')
    fig.savefig('Filter.png', bbox_inches='tight')
    fig.clf()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(SectionFilt,extent=[Offset[0],Offset[Fold-1],int((ns-1)*dt),0], cmap='gray')
    ax.set_xlim(Offset[0], Offset[Fold-1])
    ax.set_aspect(0.5)
    #plt.colorbar()
    plt.title('Filtered CDP')    
    plt.xlabel('Offset [m]')
    plt.ylabel('Time [ms]')
    fig.savefig('Output.png', bbox_inches='tight')
    fig.clf()

    # Loading a PNG file as PIXBUF
    pixfsis = gtk.gdk.pixbuf_new_from_file("Input.png")
    pixfsis = pixfsis.scale_simple(300, 500, gtk.gdk.INTERP_BILINEAR)
    imageIn = gtk.Image()
    imageIn.set_from_pixbuf(pixfsis)
    imageIn.show()
    main.tableDis.attach(imageIn, 0, 1, 1, 2)

    main.drawing_area.connect("expose_event", expose_event)
    main.drawing_area.connect("configure_event", configure_event)
    #main.drawing_area.connect("motion_notify_event", motion_notify_event)
    main.drawing_area.connect("button_press_event", button_press_event)

    
    main.drawing_area.set_events(gtk.gdk.EXPOSURE_MASK
                                 | gtk.gdk.LEAVE_NOTIFY_MASK
                                 | gtk.gdk.BUTTON_PRESS_MASK
                                 | gtk.gdk.POINTER_MOTION_MASK
                                 | gtk.gdk.POINTER_MOTION_HINT_MASK)

    main.tableDis.attach(main.drawing_area, 1, 2, 1, 2)


    pixfsis = gtk.gdk.pixbuf_new_from_file("Output.png")
    pixfsis = pixfsis.scale_simple(300, 500, gtk.gdk.INTERP_BILINEAR)
    imageIn = gtk.Image()
    imageIn.set_from_pixbuf(pixfsis)
    imageIn.show()
    main.tableDis.attach(imageIn, 2, 3, 1, 2)

    main.drawing_area.show()    

#CALLBACK FUNCTION del Button on_loadSegy
def on_loadSegy_clicked(widget):
    global Imagehbox, Section, Record, Nrecord, Fold,nt,ns,dt, Offset, dt_s, tmax_ms
    global FileIn, SectionTauPi, SectionFilt
    variables.xpick = [0]
    variables.ypick = [0]
    FileIn = main.entryFileIn.get_text()       #SEGY file name
    Nrecord = 1901                             #Number of CDP-Gathers
    Record = int(main.entryRecord.get_text())
    Fold = int(main.entryFold.get_text())      #Fold of the CDP-Record
    nt=read_segy.ntraces(FileIn)               #Number of traces in SEGY file
    ns=read_segy.nsamp_segy(FileIn)            #Number of samples per trace
    dt=int(read_segy.dt_segy(FileIn))/1000     #Sample rate (ms)
    dt_s = dt/1000.0                           #Sample rate (s) heavily used

    
    Section=read_segy.read_segy_record(FileIn,Record,Fold)
    Section=Section.T  # Section es la Matriz que contiene las trazas del CDP
   

    Offset=read_segy.read_segy_offset(FileIn,Record,Fold)  #List containing the     
    #buttonFilter.clicked()
    SectionTauPi = Section
    SectionFilt = Section
    on_redisplay(widget)



def on_buttonNext_clicked(widget):
    
    Incr = int(main.entryIncrement.get_text())                   
    Record = int(main.entryRecord.get_text())
    main.entryRecord.set_text(str(Record+Incr))
    #pdb.set_trace()
    
    loadSegy.clicked()

def on_buttonSlantStack_clicked(widget):
    global Section, Offset, SectionTauPi, ns, Fold, nt, dt
    SectionTauPi = Section 
    # En esta funcion se recogeran los parametros suministrados por el usuario
    # para calcular el SlantStack y se desplegara el mismo en el area dibujable
    # (picking panel)
    
    # Te suministro a Section que es una numpy-matrix cuyas columnas son las trazas 
    # del CDP-Gather arregladas por offset. Tambien te suministro la lista   Offset
    # que contiene los valores de offset de las trazas en Section

    Section = Section
    Offset = Offset

    # Aqui empiezas a programar la transformacion del CDP(tiempo, offset) a
    # CDP(tau,pi) --slantstack--. La NumpyMatrix que contiene el CDP(tau,pi)
    # se llamara SectionTauPi

    on_redisplay(widget)


def on_buttonFilter_clicked(widget):
    global Section, Offset, SectionTauPi, SectionFilt, ns, Fold, nt, dt
    SectionFilt = Section
    # En esta funcion se recogera el el poligono de enmudecimineto interpretado
    # por el usuario,  se enmudecera  el   CDP(tau,pi) y este   se   desplegara
    # actualizado y el CDP filtrado. La NumpyMatrix que contiene al CDPFiltrado
    # se llamara SectionFilt

    on_redisplay(widget)


def on_buttonExport_clicked(widget):
    print "Comencemos a programar la funcion que exporta SEGY file"



def main():
    global loadSegy, buttonFilter

    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_name ("Test Input")

    main.hbox = gtk.HBox(False, 0)
    window.add(main.hbox)
    main.hbox.show()

##### CREATING LEFT MENU   ##########

    main.tablePar = gtk.Table(15,4,False)
    main.tablePar.show()
    main.hbox.pack_start(main.tablePar)

    labelfile = gtk.Label("Input File: ")
    labelfile.show()
    main.tablePar.attach(labelfile, 0, 4, 1, 2)
    main.entryFileIn = gtk.Entry()
    main.entryFileIn.set_text("CDP_501m_66fold_Iln305_Xln101_2001_dt4ms.sgy")
    main.entryFileIn.show()
    main.tablePar.attach(main.entryFileIn, 0, 4, 2, 3)

    labelfold = gtk.Label("Fold: ")
    labelfold.show()
    main.entryFold = gtk.Entry()
    main.entryFold.set_text("66")
    main.entryFold.show()
    main.tablePar.attach(labelfold, 0, 2, 3, 4)
    main.tablePar.attach(main.entryFold, 2, 4, 3, 4)

    labelrecord = gtk.Label("CDP: ")
    labelrecord.show()
    main.entryRecord = gtk.Entry()
    main.entryRecord.set_text("200")
    main.entryRecord.show()
    main.tablePar.attach(labelrecord, 0, 2, 4, 5)
    main.tablePar.attach(main.entryRecord, 2, 4, 4, 5)    

    loadSegy = gtk.Button(label="Load CDP")
    loadSegy.show()
    main.tablePar.attach(loadSegy, 0, 4, 5, 6)
    loadSegy.connect("clicked", on_loadSegy_clicked)

    labelIncrement = gtk.Label("CDP Increment: ")
    labelIncrement.show()
    main.entryIncrement = gtk.Entry()
    main.entryIncrement.set_text("200")
    main.entryIncrement.show()
    main.tablePar.attach(labelIncrement, 0, 3, 6, 7)
    main.tablePar.attach(main.entryIncrement, 3, 4, 6, 7)

    buttonNext = gtk.Button(label="Next CDP")
    buttonNext.show()
    main.tablePar.attach(buttonNext, 0, 4, 7, 8)
    buttonNext.connect("clicked", on_buttonNext_clicked)

    buttonSlantStack = gtk.Button(label="Show Slant Stack")
    buttonSlantStack.show()
    main.tablePar.attach(buttonSlantStack, 0, 4, 9, 10)
    buttonSlantStack.connect("clicked", on_buttonSlantStack_clicked)


    buttonFilter = gtk.Button(label="Apply Filter")
    buttonFilter.show()
    main.tablePar.attach(buttonFilter, 0, 4, 10, 11)
    buttonFilter.connect("clicked", on_buttonFilter_clicked)


    buttonExport = gtk.Button(label="Export Filtered SEGY")
    buttonExport.show()
    main.tablePar.attach(buttonExport, 0, 4, 11, 12)
    buttonExport.connect("clicked", on_buttonExport_clicked)
    

    window.connect("destroy", lambda w: gtk.main_quit())

###### CREATING RIGHT DISPLAY   ########
    main.tableDis = gtk.Table(2,3,False)
    main.tableDis.show()
    main.hbox.pack_start(main.tableDis)


    # Create the drawing area
    main.drawing_area = gtk.DrawingArea()
    main.drawing_area.set_size_request(300, 500)

    window.show()

    gtk.main()

    return 0

if __name__ == "__main__":
    main()
