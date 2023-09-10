from tkinter import *
from tkinter import ttk
import tkinter
import sv_ttk
from tkinter.messagebox import showinfo
from PIL import ImageTk, Image
import os
import torch
from tokenizer import Tokenizer
import torchvision

MODEL_SAVE_DIR = "C:\\Users\\vadhy\\Documents\\SceneUnderstanding\\models\\Foundation.pt"
IMG_SIZE = 256

class Loader:
    def __init__(self):
        self.parent_path = ''
        self.file_list = []
        self.caption = ''
        self.image_name = ''
        image = Image.open("test.png")
        image.thumbnail((500, 500))
        self.image = image
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.tokenizer = Tokenizer()
        self.tokenizer.load("tokenizer2.pkl")
        self.model = torch.load(MODEL_SAVE_DIR)
        self.modelloc = MODEL_SAVE_DIR
        self.img_processor = torchvision.transforms.Compose([
            torchvision.transforms.Resize((IMG_SIZE, IMG_SIZE)),
            torchvision.transforms.ToTensor(),
        ])


    def add_tk_path(self, path):
        self.tk_path = path
    
    def run_model(self):
        device = selected_device.get()
        if self.modelloc != model_location.get():
            self.modelloc = model_location.get()
            self.model = torch.load(self.modelloc)
        self.model = self.model.to(device)
        img = Image.open(os.path.join(self.parent_path, self.image_name))
        if img.mode != 'RGB':
                img = img.convert('RGB')
        img = self.img_processor(img)
        img = img.unsqueeze(0)
        img = img.to(device)
        text = [self.tokenizer.char_to_idx["[START]"]]
        text = torch.tensor(text).to(torch.int64).to(device)

        self.model.eval()
        with torch.no_grad():
            i = 0
            while True:
                output = self.model((text.unsqueeze(0), img))
                output = output.argmax(dim = -1)
                text = torch.concat([text, output[-1][-1].unsqueeze(0)], dim = -1)
                if output[0][-1] == self.tokenizer.char_to_idx["[END]"]:
                    break
                i += 1
                if i > 100:
                    break
        string = self.tokenizer.decode(text[1:-1].tolist())
        self.caption = string
        caption_label.configure(text = self.caption)

    def load(self, treeview):
        path = self.tk_path.get()
        if path == 'Enter path to folder' or path == '':
            return
        if os.path.isdir(path):
            self.parent_path = path
            self.file_list = os.listdir(path)
            self.file_list = [file for file in self.file_list if file.endswith('.jpg') or file.endswith('.png')]
            self.image_name = self.file_list[0]
            self.image = Image.open(os.path.join(path, self.image_name))
            self.image.thumbnail((500, 500))
            self.caption = 'A brirf caption generated by model'
            caption_label.configure(text = self.caption)
            self.update_treeview(treeview)
        else:
            showinfo(title = 'Invalid Path', message = 'Please enter a valid path to a folder')
            
    def update_treeview(self, treeview):
        treeview.delete(*treeview.get_children())
        for file in self.file_list:
            treeview.insert('', tkinter.END, values=file)
            
    def item_selected_treeview(self, treeview):
        for selected_item in treeview.selection():
            item = treeview.item(selected_item)
            name = item['values'][0]
            self.image_name = name
            self.image = Image.open(os.path.join(self.parent_path, name))
            self.image.thumbnail((500, 500))
            self.image = ImageTk.PhotoImage(self.image)
            self.tk_image = self.image
            label.configure(image=self.tk_image)
            text_label.configure(text = name)
            self.caption = 'A brief caption generated by model'
            caption_label.configure(text = self.caption)

#configure the root window and set the ttk style
root = tkinter.Tk()
root.title('Scene Understanding')
root.geometry('1200x900')
loader = Loader()
window = ttk.Frame(root)
sv_ttk.use_dark_theme()
style = ttk.Style(root)
style.configure('lefttab.TNotebook', tabposition='w', padding = [10, 0, 0, 0])


#create a notebook(tabs interface)
notebook = ttk.Notebook(window)
# notebook = ttk.Notebook(root)

#Tab 1: Generator Tab---------------------------------------------------------------

#create a paned window(split screen)
paned_window = ttk.PanedWindow(notebook, orient=tkinter.HORIZONTAL)


#file explorer on left, generator on right
file_explorer = ttk.Frame(paned_window)
generator = ttk.Frame(paned_window)


#File Explorer

text_frame = ttk.Frame(file_explorer)
#A text box to enter the path to the folder
path = tkinter.StringVar()
loader.add_tk_path(path)

path_box = ttk.Entry(text_frame, textvariable=path)
path_box.insert(0, 'Enter path to folder')
path_box.config(foreground = 'gray', font = 'italic')
def on_entry_click(event):
    if path_box.get() == 'Enter path to folder':
        path_box.delete(0, "end") # delete all the text in the entry
        path_box.insert(0, '') #Insert blank for user input
        path_box.config(foreground = 'white')

def on_focusout(event):
    if path_box.get() == '':
        path_box.insert(0, 'Enter path to folder')
        path_box.config(foreground = 'gray', font = 'italic')
path_box.bind('<FocusIn>', on_entry_click)
path_box.bind('<FocusOut>', on_focusout)
path_box.pack(expand = True, fill = 'x', side = 'left', anchor = 'n', pady=5, padx=5)


tree = ttk.Treeview(file_explorer, columns=['path'], show='')
def load():
    loader.load(tree)
load_button = ttk.Button(text_frame, text = 'Load', command = load)

load_button.pack(expand = False,side = 'right', anchor = 'n', pady=5, padx=5)
text_frame.pack(expand = False, fill = 'x', side = 'top', anchor = 'n', pady=5, padx=5)

#the treeview to display the files in the folder
def item_selected(event):
    loader.item_selected_treeview(tree)

tree.bind('<<TreeviewSelect>>', item_selected)
scrollbar = ttk.Scrollbar(file_explorer, orient=tkinter.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
tree.pack(expand=True, fill = 'both', side = 'left', anchor = 'sw', pady=5, padx=5)
scrollbar.pack(expand = False, fill = 'y', side = 'right', anchor = 'se', padx = 2, pady = 5)
file_explorer.pack(expand=True, padx=10, pady=10)
paned_window.add(file_explorer, weight=1)

#generator
text_label = ttk.Label(generator, text = 'Image name here', font= ('Arial', 20))
text_label.pack(expand = False, anchor = 'n', padx=10, pady=10)

#the image to display the generated image

label = ttk.Label(generator, image=None)
label.pack(expand = False, anchor = 'n')


generate_button = ttk.Button(generator, text = 'Generate Description', command = loader.run_model)
generate_button.pack(expand = False, anchor = 's', pady=10, padx=5)

caption_label = ttk.Label(generator, text = 'A brief caption generated by model', font= ('Arial', 20))
caption_label.pack(expand = False, anchor = 's', padx=10, pady=10)

generator.pack(expand = True, pady=5)
paned_window.add(generator, weight=2)

#paned window settings
paned_window.pack(fill = tkinter.BOTH, expand=True, padx=10, pady=10)

#Tab 2: Settings Tab--------------------------------------------------------
settings_frame = ttk.Frame(notebook)

settings_label = ttk.Label(settings_frame, text = 'Settings', font= ('Arial', 40))
settings_label.pack(padx=10, pady=10, anchor = 'w')

#theme
theme_frame = ttk.Frame(settings_frame)
theme_label = ttk.Label(theme_frame, text = 'Theme', font= ('Arial', 20))
theme_label.pack(padx=10, pady=10, anchor = 'w')

change_theme_button = ttk.Button(theme_frame, text = 'Change Theme', command = sv_ttk.toggle_theme)
change_theme_button.pack(padx=10, pady=10, anchor = 'w')
theme_frame.pack(padx=10, pady=10, anchor = 'w')

#device
device_frame = ttk.Frame(settings_frame)
device_label = ttk.Label(device_frame, text = 'Device', font= ('Arial', 20))
device_label.pack(padx=10, pady=10, anchor = 'w')

device_choices = (('CPU', 'cpu'),
                ('GPU', 'cuda'))
selected_device = tkinter.StringVar()
selected_device.set('cuda')

for text, mode in device_choices:
    ttk.Radiobutton(device_frame, text=text, value=mode, variable=selected_device).pack(anchor=tkinter.W, padx=10)

device_frame.pack(padx=10, pady=10, anchor = 'w')

#model location
model_location_frame = ttk.Frame(settings_frame)
model_location_label = ttk.Label(model_location_frame, text = 'Model Location', font= ('Arial', 20))
model_location_label.pack(padx=10, pady=10, anchor = 'w')

model_location = tkinter.StringVar()
model_location.set(MODEL_SAVE_DIR)

model_location_box = ttk.Entry(model_location_frame, textvariable=model_location)
model_location_box.pack(expand = True, side = 'left', anchor = 'nw', pady=5, padx=5)
model_location_frame.pack(padx=10, pady=10, anchor = 'w')

notebook.add(paned_window, text = 'Generator')
notebook.add(settings_frame, text = 'Settings')
notebook.pack(expand = True, fill = 'both')
window.pack(expand = True, fill = 'both')
root.mainloop()