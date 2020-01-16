#!/usr/bin/env python3
# coding: utf-8

import threading

from tkinter import *
from tkinter.ttk import *

from PIL import ImageTk

from . import comics



class App(Frame):
    '''
    no offense but if you use global variables for tkinter 
    you're kind of a DUMMKOPF.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
        self.picture_frame = Frame(self)
        self.picture_frame.pack(fill=BOTH, expand=True)
        
        f = Frame(self)
        f.pack(fill=X)
        f.grid_columnconfigure(0, weight=1)
        self.button = Button(f, text="Start!", command=self.get_comic)
        self.button.grid(row=0, column=0)
        self.url_button = Label(f, text='url')
        self.url_button.grid(row=0, column=1, padx=5)
        self.url_button.bind('<Button-1>', self.toggle_url)
        
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
        print('canvas mode not enabled');return
        
    
    def _set_viewport(self) -> bool:
        '''
        helper function that toggles between the handy dandy
        auto-resizing tkinter smart window, and a scrollbar-
        based view for images beyond the screen's dimentions.
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
        # start by clearing the widgets from the picture area.
        for w in self.picture_frame.winfo_children():
            w.pack_forget()
        
        # next, if the comic fits on the screen, simply render in a frame.
        if self._set_viewport():
            Label(self.picture_frame, image=self._tk_img).pack() # WOW I LOVE IT

        # otherwise we need to do some annoying-ass canvas magic
        else:
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
    
        
    def _render_error(self, err: str):
        # boilerplate unpacking
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
        App(self).pack(fill=BOTH, expand=True)


def run():
    Root().mainloop()


if __name__ == '__main__':
    run()
