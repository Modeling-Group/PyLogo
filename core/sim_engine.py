
import os

from PyLogo.core.core_elements import Patch, Turtle
import PyLogo.core.static_values as static

import pygame as pg
from pygame.time import Clock

import PySimpleGUI as sg

import tkinter as tk


"""
    Demo of integrating PyGame with PySimpleGUI.
    A similar technique may be possible with WxPython.
    To make it work on Linux, set SDL_VIDEODRIVER as
    specified in http://www.pygame.org/docs/ref/display.html, in the
    pygame.display.init() section.
"""


class SimpleGUI:

    def __init__(self, model_gui_elements, caption="Basic Model"):

        # Constants for the main loop in start() below.
        self.CTRL_D = 'D:68'
        self.CTRL_d = 'd:68'
        self.ESCAPE = 'Escape:27'
        self.EXIT = 'Exit'
        self.FPS = 'FPS'
        self.GO = 'go'
        self.GO_ONCE = 'go once'
        self.NORMAL = 'normal'
        self.Q = 'Q'
        self.q = 'q'
        self.SETUP = 'setup'
        self.STOP = 'Stop'

        self.clock = Clock()
        self.default_fps = 60
        self.fps = self.default_fps
        self.idle_fps = 10

        self.lower_left_pixel = (static.SCREEN_PIXEL_HEIGHT - 1, 0)
        self.upper_right_pixel = (0, static.SCREEN_PIXEL_WIDTH - 1)
        self.screen_color = pg.Color(sg.RGB(50, 60, 60))
        self.screen_pixel_shape = (static.SCREEN_PIXEL_WIDTH, static.SCREEN_PIXEL_HEIGHT)

        self.window: sg.PySimpleGUI.Window = self.make_window(caption, model_gui_elements)

        pg.init()
        # Everything is drawn to static.SCREEN
        static.SCREEN = pg.display.set_mode(self.screen_pixel_shape)

    def draw(self):
        # Fill the screen with the background color, then: draw patches, draw turtles on top, update the display.
        static.SCREEN.fill(self.screen_color)
        static.WORLD.draw( )
        pg.display.update( )

    def make_window(self, caption, model_gui_elements):
        """
        Create the window, including sg.Graph, the drawing surface.
        """
        # --------------------- PySimpleGUI window layout and creation --------------------
        layout = \
            [  # sg.Graph(SHAPE, lower-left, upper-right,
                [sg.Graph(self.screen_pixel_shape, self.lower_left_pixel, self.upper_right_pixel,
                          background_color='black', key='-GRAPH-')],

                model_gui_elements,

                [sg.Button(self.SETUP), sg.Button(self.GO_ONCE),
                 sg.Button(self.GO, pad=((0, 50), (0, 0))),

                 sg.Button(self.STOP, button_color=('white', 'darkblue')),
                 sg.Exit(button_color=('white', 'firebrick4'), key=self.EXIT),

                 sg.Text(self.FPS, pad=((100, 10), (0, 0)), tooltip='Frames per second'),
                 sg.Slider(key=self.FPS, range=(1, 100), orientation='horizontal', tooltip='Frames per second',
                           default_value=self.default_fps, pad=((0, 0), (0, 20)))]
            ]
        window: sg.PySimpleGUI.Window = sg.Window(caption, layout, finalize=True, return_keyboard_events=True)
        # print(type(window))
        graph: sg.PySimpleGUI.Graph = window['-GRAPH-']
        # print(type(graph))
        # -------------- Magic code to integrate PyGame with tkinter -------
        embed: tk.Canvas = graph.TKCanvas
        # print(type(embed))
        os.environ['SDL_WINDOWID'] = str(embed.winfo_id( ))
        os.environ['SDL_VIDEODRIVER'] = 'windib'  # change this to 'x11' to make it work on Linux

        return window

    def run_model(self):
        while True:
            (event, values) = self.window.read(timeout=10)
            # Allow the user to change the FPS dynamically.
            self.fps = values[self.FPS]

            if event in (None, self.EXIT):
                return self.EXIT
            if event == self.STOP or static.WORLD.done():
                break

            # static.TICKS are our local counter for the number of times we have gone around this loop.
            static.TICKS += 1
            static.WORLD.step(event, values)
            self.draw()

            # The next line controls how fast the simulation runs
            # and is not really a counter for our purposes.
            self.clock.tick(self.fps)

        static.WORLD.final_thoughts()
        return self.NORMAL

    def start(self, world_class, patch_class=Patch, turtle_class=Turtle):

        world_class(patch_class=patch_class, turtle_class=turtle_class)

        # Let events come through pygame to this level.
        pg.event.set_grab(False)
        # Give event a value so that the while loop can look at it the first time through.
        event = None
        while event not in [self.ESCAPE, self.q, self.Q, self.CTRL_D, self.CTRL_d]:
            (event, values) = self.window.read(timeout=10)

            self.fps = values[self.FPS]

            if event in (None, self.EXIT):
                self.window.close()
                break

            if event == self.SETUP:
                static.WORLD.setup(values)
                self.draw()

            if event == self.GO_ONCE:
                static.WORLD.step(event, values)
                self.draw()

            if event == self.GO:
                returned_value = self.run_model()
                if returned_value == self.EXIT:
                    self.window.close()
                    break

            self.clock.tick(self.idle_fps)