from kivy.app import App
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.properties import (ListProperty,
                             ObjectProperty,
                             StringProperty)

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.popup import Popup

import os
import subprocess

import logging
_logger = logging.getLogger(__name__)

class IconButton(ButtonBehavior, Image):
    def on_press(self):
        self.color = [0.5, 0.5, 0.5, 1]

    def on_release(self):
        self.color = [1, 1, 1, 1]


class LoadDialog(BoxLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    init_directory = StringProperty(os.path.expanduser('~'))


class SaveDialog(BoxLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    init_directory = StringProperty(os.path.expanduser('~'))


class StatusMessage(BoxLayout):
    text = StringProperty()


class MainWindow(BoxLayout):
    ifiles = ListProperty()
    ofile = StringProperty()
    text_input = ObjectProperty()
    init_directory = StringProperty(os.path.expanduser('~'))

    def build(self):
        self.ifiles = []

    def merge(self):
        command = ["confluence-merge",
                   "-o", self.ofile,
                   "--index-col=0"] + \
                  [x["abspath"] for x in self.ifiles]
        commandString = ' '.join(command)
        _logger.info(f"Executing {commandString}")
        try:
            job = subprocess.run(command, check=True)
        except subprocess.CalledProcessError:
            _logger.error(f"Command {commandString} failed.")
        # report on success/failure
        if job.returncode == 0:
            self.show_status("Merge completed successfully.")
        else:
            msg = '\n'.join(['Merge failed. Please send files:'] + \
                            [("\t" + x["abspath"]) for x in self.ifiles] + \
                            ["to bkappes@mines.edu."])
            self.show_status(msg)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_status(self, msg):
        content = StatusMessage(text=msg)
        self._popup = Popup(title="Merge status",
                            content=content,
                            size_hint=(0.8, 0.8),
                            pos_hint={'right': 0.9, 'top': 0.8})
        self._popup.open()

    def show_load(self):
        content = LoadDialog(load=self.load,
                             cancel=self.dismiss_popup,
                             init_directory=self.init_directory)
        self._popup = Popup(title="Add inputs",
                            content=content,
                            size_hint=(0.9, 0.9),
                            pos_hint={'right': 0.95, 'top': 0.95})
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save,
                             cancel=self.dismiss_popup,
                             init_directory=self.init_directory)
        self._popup = Popup(title="Set output",
                            content=content,
                            size_hint=(0.9, 0.9),
                            pos_hint={'right': 0.95, 'top': 0.95})
        self._popup.open()

    def load(self, path, filename):
        # ensure filenames and paths are lists
        if not isinstance(filename, str):
            filenames = sorted(filename)
            paths = [os.path.join(path, fname) for fname in filenames]
        else:
            filenames = [filename]
            pathes = [os.path.join(path, filename)]
        # extend ifiles
        self.ifiles.extend(
            [{'index': i,
              'filename': fname,
              'path': path,
              'abspath': os.path.abspath(path),
              'unique': os.path.abspath(path)}
             for i, (fname, path) in enumerate(zip(filenames, paths))])
        self.init_directory = path
        self._update_ifiles()
        self.dismiss_popup()

    def save(self, path, filename):
        self.ofile = os.path.join(path, filename)
        self.init_directory = path
        # if the output file already exists, we will add to it by default.
        if os.path.isfile(self.ofile):
            self.ifiles.append({
                'index': 0,
                'filename': filename,
                'path': path,
                'abspath': os.path.abspath(self.ofile),
                'unique': os.path.abspath(self.ofile)}
            )
            self._update_ifiles()
        self.dismiss_popup()

    def move(self, index, loc):
        if loc is None:
            # loc is None--move to the end
            loc = len(self.ifiles)
        else:
            # do not move past the top or below the bottom
            try:
                loc = min(max(int(loc), 0), len(self.ifiles))
            except ValueError:
                loc = index
        item = self.ifiles.pop(index)
        self.ifiles.insert(loc, item)
        # update the data
        self._update_ifiles()

    def remove(self, index):
        self.ifiles.pop(index)
        if len(self.ifiles) > 0:
            self._update_ifiles()

    def exit(self, *args):
        App.get_running_app().stop()
        Window.close()

    def _update_ifiles(self):
        def find_unique(paths):
            matrix = [[entry for entry in p.split(os.path.sep)
                       if entry != ''] for p in paths]
            minlevel = min([len(vec) for vec in matrix])
            for level in range(-1, -minlevel-1, -1):
                # (|level| - 1) + basename --> name
                names = [os.path.sep.join(vec[level:]) for vec in matrix]
                duplicates = any([(names[i] == names[j])
                                  for i in range(len(names)-1)
                                  for j in range(i+1, len(names))])
                if not duplicates:
                    return names
            raise ValueError('No unique paths found.')

        def remove_duplicates(lod, key):
            result = []
            for entry in lod:
                if not any([(entry[key] == r[key]) for r in result]):
                    result.append(entry)
            return result

        self.ifiles = [{
            'index': i,
            'filename': d['filename'],
            'path': d['path'],
            'abspath': d['abspath'],
            'unique': d['unique']
            } for i, d in enumerate(self.ifiles)]
        self.ifiles = remove_duplicates(self.ifiles, 'abspath')
        unique = find_unique([x['abspath'] for x in self.ifiles])
        for u, d in zip(unique, self.ifiles):
            d['unique'] = u


class MergeApp(App):
    pass


Factory.register('MainWindow', cls=MainWindow)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)
Factory.register('IconButton', cls=IconButton)
Factory.register('StatusMessage', cls=StatusMessage)

        
if __name__ == '__main__':
    MergeApp().run()
