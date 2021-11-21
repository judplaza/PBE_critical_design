
from Read import Leer
from Connection import Connection
import I2C_LCD_driver

import drivers
from time import sleep
#display = drivers.Lcd()

import gi, threading, time, sys, json
import threading

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, GObject



class MyWindow(Gtk.Window):
    def __init__(self):
        '''inicialitzem els constructors i l'accés al css'''
        super().__init__(title="PBE Telematica CDR")
        css_provider = Gtk.CssProvider()        
        css_provider.load_from_path("style/interface_style.css")
        context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                
        self.preparat_lectura = True
        #self.t = threading.Timer(10, self.logout)
        self.my_lcd = I2C_LCD_driver.lcd()
        self.login_page()
        self.state = 1
        self.read = Leer()
        self.create_thread()  
        self.server_connection = Connection()
        
        self.first_time=True
    
    def login_page(self):
        '''funció que inicialitza la pantalla de login'''
        self.box_login= Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)     
        
        self.label = Gtk.Label(label= "Please, login with your university card")
        self.label.get_style_context().add_class("welcome")
        self.label.set_size_request(500,350)
        self.box_login.pack_start(self.label, True, True, 8)
        
        self.label_error = Gtk.Label(label="")        
        self.label_error.get_style_context().add_class("welcome_error")
        self.label_error.set_text("")
        self.label_error.set_size_request(0,0)        
        self.box_login.pack_start(self.label_error, True, True, 8)
                
        self.add(self.box_login)
        
        #display.lcd_display_string("Please, login",1)
        #display.lcd_display_string("with your card",2)
        #sleep(2)
        text = [""," Please, login with","your university card"]    
        self.my_lcd.write_text_multiline(text)

        
    def menu_page(self):
        '''inicialitzem la pantalla de menu'''
        self.box_menu1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.box_menu1.get_style_context().add_class("label")
        self.add(self.box_menu1)
        self.box_menu11 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.box_menu11.get_style_context().add_class("label")
        self.label = Gtk.Label()        
        self.label.set_text(str(" Welcome "+self.username+" "))        
        self.box_menu11.add(self.label)
        
        
        self.button = Gtk.Button(label="logout")
        self.button.connect("clicked", self.logout)
        self.button.get_style_context().add_class("button")
        self.box_menu11.add(self.button)
        self.box_menu1.add(self.box_menu11)
        
        self.entry = Gtk.Entry()
        self.entry.set_text("")
        
        
        self.box_menu1.pack_start(self.entry, False, True, 15)
        self.entry.set_editable(True)
        self.entry.set_visibility(True)
        
        self.entry.connect("activate", self.get_tabla)
        
        self.label_error_menu= Gtk.Label()
        self.label_error_menu.set_text("")
        self.label_error_menu.get_style_context().add_class("label")
        self.box_menu11.pack_start(self.label_error_menu, True, True, 0)

        #display.lcd_display_string("Welcome",1)
        #display.lcd_display_string(self.username,2)
        #sleep(2)
        text = ["","Welcome",self.username]
        self.my_lcd.lcd_clear()
        self.my_lcd.write_text_multiline(text)
    
    def lecture_uid(self):
        '''funció de lectura de uid al rfid, connecta amb la funció de login'''
        self.uid = self.read.hacer_una_lectura()
        self.login_function()
    
    def login_function(self):
        '''s'encarrega de donar accés a al server i executar les funcions de login'''
        self.server_connection.set_uid(self.uid)        
        self.thread_login = threading.Thread(target=self.server_connection.login_connection)
        
        self.thread_login.daemon = True
        self.ready_lecture = False
        self.thread_login.start()        
        self.ready_lecture = True
                
        self.username = self.server_connection.login_connection() 
        print(self.username)
        if self.username ==  "error_in_login_instrucction":
            #print("error")
            GLib.idle_add(self.error_gen())
        
        else:
            self.username = json.loads(self.username)[0]
        
            if self.username == "NONE":  
                print("help")
                GLib.idle_add(self.error_username())
            else:
                self.crono()
                self.t.start()
                GLib.idle_add(self.change_page)            
            
            
    def change_page(self):
        '''canvi de pàgina, s'accedeix de manera no bloquejant'''
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
            
    def error_gen(self):
        self.label_error.set_text("ERROR general")
        self.label_error.set_size_request(30,30)
        text = ["", "ERROR general"]
        self.my_lcd.lcd_clear()
        self.my_lcd.write_text_multiline(text)
        self.create_thread()
        
    def error_username(self):
        self.label_error.set_text("uid not registred")
        self.label_error.set_size_request(30,30)
        text = ["", "ERROR","uid not registred"]
        self.my_lcd.lcd_clear()
        self.my_lcd.write_text_multiline(text)
        self.create_thread()

    def read_entry(self):
        return self.entry.get_text()
    
    def get_tabla(self, entry):
        '''accés al servidor per recuperar la taula'''
        self.t.cancel()
        self.crono()
        self.t.start()        
        query = self.read_entry()        
        
        self.instruccion=query    
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
            #print(tabla)
            self.show_table(tabla)
        
        
    def show_table(self,tabla):        
        '''mostra la taula'''    
        query = list(tabla.keys())[0] #accedeixo al nom de la instrucció
        #print(query)
        
        if self.first_time is False: #en cas que no sigui la primera instrucció a demanar, netejo la finestra abans de mostrar-se alguna altra
            self.treeview.destroy()
            self.scrollable_treelist.destroy()            
        background_1 ="#dee2ea"
        background_2 ="#acb7ca"
        try:     
            if query == 'timetables': #si vull mostrar els horaris necessito 4 columnes
                
                self.timetable_list= Gtk.ListStore(str, str, str, str, str) #n'hi afegeixo 5 atributs per poder posar un background color
                
                
                i=0
                columnas = list(tabla[query][0].keys())
            
                for row in tabla[query]: #omplim amb les dades del json                                       
                    #colorejo les files alternativament
                    if i%2==0:
                        self.timetable_list.append([row[columnas[0]],row[columnas[1]],row[columnas[2]],row[columnas[3]], background_1])
                    else:
                        self.timetable_list.append([row[columnas[0]],row[columnas[1]],row[columnas[2]],row[columnas[3]], background_2])
                    i=i+1
                    #print(row[columnas[0]])
            
                self.treeview = Gtk.TreeView.new_with_model(self.timetable_list) #creem un treeview associat al model (conté ja les dades)                
                for i, titles in enumerate([columnas[0],columnas[1],columnas[2],columnas[3]]):  #formatejem el tree view per poder-lo visualitzar                 
                    renderer = Gtk.CellRendererText()                    
                    renderer.set_fixed_size(100,40)
                    renderer.set_property("xalign",0.5)                                        
                    #renderer.set_property('foreground','#00FF00') -->color lletra
                    #renderer.set_property('foreground','#00FF00') -->color fons
                                        
                    column = Gtk.TreeViewColumn(titles,renderer,text=i)                    
                    column.set_alignment(0.5)
                    column.add_attribute(renderer, "background", 4)
                    #self.treeview.append_column(column)
                    self.treeview.append_column(column)
                                        
            
            elif query == 'tasks' or query == 'marks':
                self.task_marks_list = Gtk.ListStore(str, str, str, str)
                i=0
                columnas = list(tabla[query][0].keys())
            
                for row in tabla[query]:         
                    if i%2==0:
                        self.task_marks_list.append([row[columnas[0]],row[columnas[1]],row[columnas[2]], background_1])
                    else:
                        self.task_marks_list.append([row[columnas[0]],row[columnas[1]],row[columnas[2]], background_2])
                    i=i+1
                self.treeview = Gtk.TreeView.new_with_model(self.task_marks_list)
            
                for i, titles in enumerate([columnas[0],columnas[1],columnas[2]]):
                    renderer = Gtk.CellRendererText()
                    renderer.set_fixed_size(100,40)                    
                    renderer.set_property("xalign",0.5)
                    column = Gtk.TreeViewColumn(titles,renderer,text=i)
                    column.set_alignment(0.5)
                    column.add_attribute(renderer, "background", 3)
                    self.treeview.append_column(column)
                
            #utilitzem un ScrolledWindow() per tenir accés al desplaçament si fos necessari
            self.scrollable_treelist = Gtk.ScrolledWindow()        
            self.scrollable_treelist.set_vexpand(True)
            
            self.box_menu1.pack_start(self.scrollable_treelist,True, True, 0)      
            self.scrollable_treelist.add(self.treeview)            
            window.show_all()
            self.first_time=False
        except IndexError as err:
            self.label_error_menu.set_text("Taula buida")

    def logout(self, widget):    
        '''logout des del botó'''
        GLib.idle_add(self.change_page)
    
    def logout_automatic(self):
        '''logout per temporitzador expirat'''
        GLib.idle_add(self.change_page)                   
            
    def create_thread(self):
        thread = threading.Thread(target=self.lecture_uid)
        thread.setDaemon(True)
        thread.start()
        
    def crono(self):
        self.t = threading.Timer(120, self.logout_automatic)
        
        
        
window = MyWindow()
window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()
