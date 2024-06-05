import pathlib
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gio, GObject, Gtk, Gdk, GdkPixbuf, GLib
# from os import remove
from rdkit.Chem import MolFromMolFile, Descriptors, Lipinski
from rdkit.Chem.Draw import MolToImage
import sys

class Widget(GObject.Object):
    __gtype_name__ = 'Widget'

    def __init__(self, name):
        super().__init__()
        self._name = name

    @GObject.Property
    def name(self):
        return self._name

def on_quit_action(self, _action):
    quit()

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Box principal
        self.main_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 6)
        self.set_child(self.main_box)

        self.box_info = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 4)
        self.main_box.append(self.box_info)

        # Menu ---- cabecera ---- sobre escribe el main_box como un contenedor nuevo
        header_bar = Gtk.HeaderBar.new()
        self.set_titlebar(titlebar=header_bar)
        self.set_title("Visualizador de archivos mol")

        # Listado del menu - darle un nuevo espacio de interaccion a otro menú
        menu = Gio.Menu.new()

        # Create a popover - un contenedor dentro de otra interacción
        self.popover = Gtk.PopoverMenu()
        self.popover.set_menu_model(menu)

        # crea un menu
        self.menu_popover = Gtk.MenuButton()
        self.menu_popover.set_popover(self.popover)
        self.menu_popover.set_icon_name("open-menu-symbolic")

        # agrega headerbar el menu popover ----> se añade a la derecha
        header_bar.pack_end(self.menu_popover)

        # Add an about dialog
        about_menu = Gio.SimpleAction.new("about", None)
        about_menu.connect("activate", self.show_about_dialog)
        self.add_action(about_menu)
        #cuando creamos este tipo de acciones, debemos informar de donde gatilla esa accion (de donde) en este caso es ABOUT DIALOG
                        #win. te dice la interaccion se esta aplicando a traves de gtk.window
                        #app. te dice la interaccion se esta aplicando a traves de gtk.application
        menu.append("Acerca de", "win.about")

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", on_quit_action)
        self.add_action(action)
        #cuando creamos este tipo de acciones, debemos informar de donde gatilla esa accion (de donde) en este caso es ABOUT DIALOG
                        #win. te dice la interaccion se esta aplicando a traves de gtk.window
                        #app. te dice la interaccion se esta aplicando a traves de gtk.application
        menu.append("Salir", "win.quit")

        # boton para abrir archivo
        boton_abrir = Gtk.Button()
        boton_abrir.set_label("Abrir")
        boton_abrir.connect("clicked", self.on_button_clicked)
        #el boton este antes q el titulo ----> a la izquerda
        header_bar.pack_start(boton_abrir)


        #Ventana de guardado
        self._native = self.dialogo_save()
        self._native.connect("response", self.on_file_save_response)

#-------------------------------------------------------------------------
        #dropdown
        self.dropdown_model = Gio.ListStore(item_type = Widget)
        self.lista_dropdown = []
        self.add_data_to_model(self.lista_dropdown)
#-------------------------------------------------------------------------


        # Crear el factory del dropdown
        self.dropdown_factory = Gtk.SignalListItemFactory()
        self.dropdown_factory.connect("setup", self.dropdown_factory_setup)
        self.dropdown_factory.connect("bind", self.dropdown_factory_bind)


#-------------------------------------------------------------------------

        # Crear el dropdown
        self.dropdown = Gtk.DropDown(model=self.dropdown_model, factory=self.dropdown_factory)
        header_bar.pack_start(self.dropdown)
        self.dropdown.connect("notify::selected-item", self.on_change_item_dropdown)

#-------------------------------------------------------------------------


        #Image Gtk.? Image or Picture
        #self.imagen = Gtk.Picture()
        self.imagen = Gtk.Image.new()
        self.imagen.set_pixel_size(300)

        self.main_box.append(self.imagen)

        # #Cuadro relleno

        # self.label_extra = Gtk.Label()
        # self.box_info.append(self.label_extra)

        #Cuadro para informacion quimica

        grid = Gtk.Grid()
        self.label_quimica= Gtk.Label()
        self.label_quimica.set_hexpand(True)
        grid.attach(self.label_quimica, 0, 0, 1, 1)
        # self.label_quimica.set_markup('<span font_desc="Monospace 12" foreground="#00FF00" weight="bold" style="italic">nose q poner</span>')
        self.box_info.append(grid)

#-------------------------------------------------------------------------

    def add_data_to_model(self, list):
        for i in self.lista_dropdown:
            self.dropdown_model.append(Widget(name=i))
        # Agrega la lista al model del dropdown

        #self.add(self.dropdown)
#-------------------------------------------------------------------------

    def dropdown_factory_setup(self, dropdown_factory, list_item):
        box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        label = Gtk.Label()
        box.append(label)
        list_item.set_child(box)


    def dropdown_factory_bind(self, dropdown_factory, list_item):
        box = list_item.get_child()
        label = box.get_first_child()
        widget = list_item.get_item()
        label.set_text(widget.name)


    def show_about_dialog(self, action, param):

        self.about = Gtk.AboutDialog()
        self.about.set_transient_for(self)
        self.about.set_modal(self)

        self.about.set_authors(["Alex_5625"])
        self.about.set_copyright("Copyright 2024 Alexis")
        self.about.set_license_type(Gtk.License.GPL_3_0)
        self.about.set_website("https://www.instagram.com/mrm00ns?igsh=dWFkZnk2Y3ZtdTVj")
        self.about.set_website_label("Mi instagram")
        self.about.set_version("2.0")
        self.about.set_logo_icon_name("example")
        self.about.set_visible(True)

    def on_button_clicked(self, button):
        self._native.show()


    def dialogo_save(self):
        return Gtk.FileChooserNative(title="Seleccionar Carpeta",
                                     action=Gtk.FileChooserAction.SELECT_FOLDER,
                                     transient_for=self.get_root(),
                                     accept_label="_Seleccionar",
                                     cancel_label="_Cancelar",
                                    )


    def on_file_save_response(self, native, response):
        if response == Gtk.ResponseType.ACCEPT:
            path = native.get_file().get_path()
            self.path_mol = path
            self.directorio = pathlib.Path(path)
            archivos_mol = [fichero.name[:-4] for fichero in self.directorio.iterdir() if self.directorio.glob(".mol")]
            self.lista_dropdown = archivos_mol
            self.add_data_to_model(self.lista_dropdown)


    def on_change_item_dropdown(self, dropdown, data):
        item_name = dropdown.get_selected_item()._name
        molfile = MolFromMolFile(f"{self.path_mol}/{item_name}.mol")
        img = MolToImage(molfile,
                         size=(600, 600))

        buffer = GLib.Bytes.new(img.tobytes())
        img_data = GdkPixbuf.Pixbuf.new_from_bytes(buffer,
                                                   GdkPixbuf.Colorspace.RGB,
                                                   False,
                                                   8,
                                                   img.width,
                                                   img.height,
                                                   len(img.getbands())*img.width)

        paintable = Gdk.Texture.new_for_pixbuf(img_data)
        #print(paintable)
        self.imagen.set_pixel_size(img.width)
        self.imagen.set_from_paintable(paintable)


        #Ingresar nuevos parametros al archivo .mol

        num_atomos = molfile.GetNumAtoms()
        enlaces = molfile.GetNumBonds()
        peso_molecular = Descriptors.MolWt(molfile)
        centros_quirales = Lipinski.NumSaturatedRings(molfile)

        string = f'<span font_desc="Monospace 12" foreground="#00FF00" weight="bold" style="italic" >El numero de atomos es: {num_atomos}\nCantidad de Enlaces: {enlaces}\nPeso Molecular: {peso_molecular:.2f}\nNumero de anillos saturados: {centros_quirales}</span>'
        self.label_quimica.set_markup(string)


    def dialogo_save(self):
            return Gtk.FileChooserNative(title="Seleccionar Carpeta",
                                         action=Gtk.FileChooserAction.SELECT_FOLDER,
                                         transient_for=self.get_root(),
                                         accept_label="_Seleccionar",
                                         cancel_label="_Cancelar",
                                        )


class MyApp(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def do_activate(self):
        active_window = self.props.active_window
        if active_window:
            active_window.present()
        else:
            self.win = MainWindow(application=self)
            self.win.present()

app = MyApp()
app.run(sys.argv)
