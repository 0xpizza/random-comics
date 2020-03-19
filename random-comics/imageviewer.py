#!/usr/bin/env python3
# coding: utf-8

import threading

from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import asksaveasfilename

from PIL import ImageTk

from . import comics


FILE_TYPES = [
    ('Image Files', '*.png *.jpg'), 
    ('All Files', '*.*'),  
] 


class App(Frame):
    '''
    no offense but if you use global variables for tkinter 
    you're kind of a DUMMKOPF.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.picture_frame = Frame(self)
        self.picture_frame.pack(fill=BOTH, expand=True)
        
        # controls at bottom
        f = Frame(self)
        f.pack(fill=X, pady=4 )
        
        #   button
        f.grid_columnconfigure(1, weight=1)
        self.button = Button(f, text="Start!", command=self.get_comic)
        self.button.grid(row=0, column=1)
        
        #   url button
        self.url_button = Label(f, text='url', style='Hyper.TLabel')
        self.url_button.grid(row=0, column=2, padx=5)
        self.url_button.bind('<Button-1>', self.toggle_url)
        
        #   save file dialog button
        self.url_button = Label(f, text='Save')
        self.url_button.grid(row=0, column=0, padx=5)
        self.url_button.bind('<Button-1>', self.save_image)
        
        self._img = None
        self.picture_url = StringVar(self)
        self.url_entry = Entry(self, state='readonly', textvar=self.picture_url)        
        self._busy = threading.Lock()
        self.after(1, self.get_comic)
        
    def get_comic(self):
        threading.Thread(
            target=self._show_comic_nonblocking, 
            daemon=True,
        ).start()
    
    def _zzz_timer(self):
        t = self.button.configure('text')[4]
        # if job is running, constantly reschedule this method
        if self._busy.locked():
            t += 'z'
            self.button.configure(text=t)
            self.after(500, self._zzz_timer)
    
    def _show_comic_nonblocking(self, callback=None):
        if self._busy.locked(): 
            return
        else:
            self._busy.acquire(timeout=0)
        self.button.configure(text='zzz')
        self.after(1, self._zzz_timer)
        try:
            self._get_comic()
            self.button.configure(text='Another!')
        except Exception as e:  # :))))
            err = str(e)
            self._render_error(err)
            self.button.configure(text='X_X')
        self._busy.release()
        

    def toggle_url(self, *events):
        if self.url_entry.winfo_ismapped():
            self.url_entry.pack_forget()
        else:
            self.url_entry.pack(pady=5)
    
    
    def _canvas_mode(self):
        print(NotImplementedError('currently no canvas mode'))
        
    
    def _set_viewport(self) -> bool:
        '''
        helper function that toggles between the handy dandy
        auto-resizing tkinter smart window, and a scrollbar-
        based view for images beyond the screen's dimentions.
        
        TODO: Learn how canvas coordinates work with scrollbars :(
        '''
        # offset slightly to account for packed widgets and also to give window
        # some breathing room
        w = self.winfo_screenwidth() - 300
        h = self.winfo_screenheight() - 300
        
        activate_auto_resize = True
        
        if self._img.height > h:
            activate_auto_resize = False
            self._canvas_mode()
        
        if self._img.width > w:
            activate_auto_resize = False
            self._canvas_mode()
            
        if activate_auto_resize:
            self._root().geometry('')
            
        return activate_auto_resize
        
    def _render_comic(self):
        '''
        This method is in charge of drawing the comic to the GUI. If the image
        is larger than the dimentions of the screen, it's SUPPOSED to 
        draw the image to a canvas with scrollbars so the reader can still
        view the image, but I don't know how to do that!!!!!! So instead it
        just tells you to open it in an application that *does* have scrolling
        and zooming and all the other stuff I'm too dumb to know how to make.
        '''
        # start by clearing the widgets from the picture area.
        for w in self.picture_frame.winfo_children():
            w.pack_forget()
        
        # next, if the comic fits on the screen, simply render in a frame.
        if self._set_viewport():
            Label(self.picture_frame, image=self._tk_img).pack() # WOW I LOVE IT

        # otherwise we need to do some annoying-ass canvas magic
        else:
            # TODO: add magic...
            self._render_error(
                "Sorry, the image was too big and can't fit on "
                "the screen. Please use this button here to try to view "
                "it in your system's native image viewer, or use the "
                "url button to view it online. Or, simply cut your losses "
                "and move on the the next one :)"
            )
            Button(
                self.picture_frame,
                text="VIEW",
                command=self._system_render_image
            ).pack()
            
    def _system_render_image(self):
        self._img.show()
    
    
    def save_image(self, *events):
        if self._img is None:
            Label(self.picture_frame, text='Nothing to save...', wraplength=200).pack()
        else:
            name = self._root().title()
            name = ''.join([c for c in name if c.isalnum() or c in ' '])
            name = name.replace('  ', ' ')
            path = asksaveasfilename(
                initialfile=name,
                filetypes=FILE_TYPES,
                defaultextension=FILE_TYPES,
            )
            
            if path:
                self._img.save(path)
                
    
        
    def _render_error(self, err: str):
        for w in self.picture_frame.winfo_children():
            w.pack_forget()
        
        Label(self.picture_frame, text=err, wraplength=200).pack()
        
    def _get_comic(self):
        '''
        heart and soul of this class which asks xkcd for a comic, then
        shows it in our handy GUI. thanks to all the ways that this
        can go wrong, it's best not to call this directly.
        '''
        
        # this call can raise various errors. make sure to 
        # have upstream error handling...
        comic = comics.get_random_comic()
        
        self._root().title("{} ~ {}".format(
            comic.series.upper(), comic.title
        ))
        self.picture_url.set(comic.url)
        
        # comic.image is a PIL.Image.
        tk_img = ImageTk.PhotoImage(image=comic.image)
        self._tk_img = tk_img
        self._img = comic.image
        self._render_comic()
            
            

class Root(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = Style(self)
        self.configure(bg='white')
        self.style.configure('Hyper.TLabel',
            foreground='blue', font='arial 10 underline'
        )
        App(self).pack(fill=BOTH, expand=True)


def run():
    Root().mainloop()


if __name__ == '__main__':
    run()
