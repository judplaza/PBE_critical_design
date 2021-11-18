
from Read import Leer
from Connection import Connection

import drivers
from time import sleep
display = drivers.Lcd()

import gi, threading, time, sys, json
import threading

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, GObject



class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="PBE Telematica CDR")
        css_provider = Gtk.CssProvider()        
        css_provider.load_from_path("style/interface_style.css")
        context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        '''inicialitzo variables i constructors'''
        
        self.preparat_lectura = True
        #self.t = threading.Timer(10, self.logout)
        
        self.login_page()
        self.state = 1
        self.read = Leer()
        self.create_thread()  
        self.server_connection = Connection()
        
        self.first_time=True
    
    def login_page(self):
        '''Definició de la pàgina de login'''
        self.box_login= Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)     
        
        self.label = Gtk.Label(label= "Please, login with your university card")
        self.label.get_style_context().add_class("welcome")
        self.label.set_size_request(500,350)
        self.box_login.pack_start(self.label, True, True, 0)
        
        self.label_error = Gtk.Label(label="")        
        self.label_error.get_style_context().add_class("welcome_error")
        self.label_error.set_text("")
        self.label_error.set_size_request(0,0)        
        self.box_login.pack_start(self.label_error, True, True, 0)
                
        self.add(self.box_login)
        
        '''LCD *NO* del puzzle2'''
        display.lcd_display_string("Please, login",1)
        display.lcd_display_string("with your card",2)
        sleep(2)

        
    def menu_page(self):
        '''Definició de la pàgina de menu'''
        self.box_menu1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)        
        self.add(self.box_menu1)
        self.box_menu11 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.box_menu11.get_style_context().add_class("label")
        self.label = Gtk.Label()
        self.label.set_text(str(" Welcome "+self.username+" "))
        self.label.get_style_context().add_class("label")
        self.box_menu11.add(self.label)
        
        
        self.button = Gtk.Button(label="logout")
        self.button.connect("clicked", self.logout)
        self.button.get_style_context().add_class("button")
        self.box_menu11.add(self.button)
        self.box_menu1.add(self.box_menu11)
        
        self.entry = Gtk.Entry()
        self.entry.set_text("intro")
        
        self.box_menu1.pack_start(self.entry, False, False, 0)
        self.entry.set_editable(True)
        self.entry.set_visibility(True)
        
        self.entry.connect("activate", self.get_tabla)
        
        self.label_error_menu= Gtk.Label()
        self.label_error_menu.set_text("")
        self.label_error_menu.get_style_context().add_class("label")
        self.box_menu11.pack_start(self.label_error_menu, True, True, 0)
        
        '''LCD *NO* del puzzle2'''
        display.lcd_display_string("Welcome",1)
        display.lcd_display_string(self.username,2)
        sleep(2)   
        
    def lecture_uid(self):        
        self.uid = self.read.hacer_una_lectura()
        self.login_function()
    
    def login_function(self):
        '''aquesta funció d'encarrega de dur a terme el login:
            * Un cop llegida una targeta 
            - Connecta al server
            - Controla l'error de no connexió
            - Controla l'error d'usuari no registrat
            - Si la uid sí és reconeguda: inicia un crono i passa a pantalla menu'''
        
        self.server_connection.set_uid(self.uid)        
        self.thread_login = threading.Thread(target=self.server_connection.login_connection)
        
        self.thread_login.daemon = True
        self.ready_lecture = False
        self.thread_login.start()        
        self.ready_lecture = True
                
        self.username = self.server_connection.login_connection() #TO-DO preguntar al profe????
        print(self.username)
        if self.username ==  "error_in_login_instrucction":
            print("error")
            self.error()
        
        else:
            self.username = json.loads(self.username)[0]
        
            if self.username == "NONE":  #TO-DO Nos lo tienen que pasar asi desde servidor
                print("help")
                self.error()        
            else:
                self.crono()
                self.t.start()
                GLib.idle_add(self.change_page)            
            
            
    def change_page(self):
        '''executa els canvis de pantalla/states'''
        if(self.state==1):
            self.remove(self.box_login)
            self.menu_page()                        
            self.show_all()
            self.state=2
            
        else:            
            self.remove(self.box_menu1)
            self.login_page()            
            self.show_all()
            self.create_thread()
            print("create thread")
            self.state=1
            
    def error(self):
        self.label_error.set_text("error")
        self.label_error.set_size_request(30,30)
        self.create_thread()

    def read_entry(self):
        return self.entry.get_text()
    
    def get_tabla(self, entry):
        '''
            - Llegeix la comanda de l'usuari
            - Accedeix al server
            - Control d'error d'escriptura
            *No hi ha control de connexió a internet perquè sí es controla al login
        '''
        self.t.cancel()
        self.crono()
        self.t.start()        
        query = self.read_entry()        
        
        self.instruccion=query
        #TO-DO problemas con los espacios?
        #print(query)       
        self.thread_query = threading.Thread(target=self.server_connection.menu_connection, args=(query,))
        self.thread_query.daemon = True        
        self.thread_query.start()
        self.ready_query = False
        json_tabla = self.server_connection.menu_connection(query)
        if json_tabla == "error_in_menu_instrucction":
            self.label_error_menu.set_text("Instrucció no reconeguda")
        else:
            self.label_error_menu.set_text("")
            self.ready_query = True
            print(json_tabla)
            tabla = json.loads(json_tabla)
            print(tabla)
            self.show_table(tabla)
        
        
    def show_table(self,tabla):
        '''Mostra la taula a la Window'''
        
        #self.box_menu1.set_row_spacing(30)
            
        query = list(tabla.keys())[0]
        print(query)
        
        if self.first_time is False: #eliminem la taula mostrada anterior si no és la primera taula demanada
            self.treeview.destroy()
            self.scrollable_treelist.destroy()
        
        try:     
            if query == 'timetables':            
                self.timetable_table= Gtk.ListStore(str, str, str, str)
            
            #columnas = list(tabla[query][0].keys())
                columnas = list(tabla[query][0].keys())
            
            #print(columnas)
                for row in tabla[query]:
                    print(columnas[0])
                    self.timetable_table.append([row[columnas[0]],row[columnas[1]],row[columnas[2]],row[columnas[3]]])
               
            
                self.treeview = Gtk.TreeView.new_with_model(self.timetable_table)

                for i, column_title in enumerate([columnas[0],columnas[1],columnas[2],columnas[3]]):
                    renderer = Gtk.CellRendererText()
                    renderer.set_fixed_size(100,40)
                    renderer.set_property("xalign",0.5)
                    column = Gtk.TreeViewColumn(column_title,renderer,text=i)
                    column.set_alignment(0.5)
                    self.treeview.append_column(column)
                                        
            
            elif query == 'tasks' or query == 'marks':
                self.task_marks_tabla = Gtk.ListStore(str, str, str)
            
                columnas = list(tabla[query][0].keys())
            
                for row in tabla[query]:         
                    self.task_marks_tabla.append([row[columnas[0]],row[columnas[1]],row[columnas[2]]])
            
                self.treeview = Gtk.TreeView.new_with_model(self.task_marks_tabla)
            
                for i, column_title in enumerate([columnas[0],columnas[1],columnas[2]]):
                    renderer = Gtk.CellRendererText()
                    renderer.set_fixed_size(100,40)
                    renderer.set_property("xalign",0.5)
                    column = Gtk.TreeViewColumn(column_title,renderer,text=i)
                    column.set_alignment(0.5)
                    self.treeview.append_column(column)
                
            
        
            self.scrollable_treelist = Gtk.ScrolledWindow()
        
            self.scrollable_treelist.set_vexpand(True)          
            self.box_menu1.pack_start(self.scrollable_treelist,True, True, 0)      
            self.scrollable_treelist.add(self.treeview)
            window.show_all()
            self.first_time=False
        except IndexError as err: #considerem que l'unic error possible serà taula buida
            self.label_error_menu.set_text("Taula buida")

    def logout(self, widget):    
        '''Tornem a la pagina d'inici per l'acció de botó'''
        GLib.idle_add(self.change_page)
    
    def logout_automatic(self):
        '''Tornem a la pagina d'inici per expiració de crono'''
        self.change_page()                   
            
    def create_thread(self):
        '''Thread de lectura de rfid'''
        thread = threading.Thread(target=self.lecture_uid)
        thread.setDaemon(True)
        thread.start()
        
    def crono(self):
        '''crea thread de crono'''
        self.t = threading.Timer(120, self.logout_automatic) #després de 2 min d'inactivitat executa el logout
        
        
        
window = MyWindow()
window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()
