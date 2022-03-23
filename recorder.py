'''
Class to record and play back mouse clicks and keyboard presses using pynput.

Compatible with Windows 10. Other OS's not tested.

TODO:
DPI awareness testing
'''

from pynput import mouse, keyboard
import time
import pandas as pd
import ctypes
import textwrap

class Recorder():
    '''Class to handle recording and playback of mouse clicks and key presses'''

    def __init__(self):

        #Init keyboard and mouse listeners
        self.m_listener = mouse.Listener(on_click = self.on_click)
        self.kb_listener = keyboard.Listener(on_press = self.on_press, 
                             on_release = self.on_release)

        #Init keyboard and mouse controllers
        self.m_controller = mouse.Controller()
        self.kb_controller = keyboard.Controller()

        self.recording = False                 
        self.recorded_moves = []                
        self.start_time = time.time()           
        self.stop_key = keyboard.Key.esc        

        self.timeout = 120        #Default timeout (s) for playback
        self.wait_time = 0.01     #Minimum time between executing playback steps


    def on_click(self, x, y, button, pressed):
        '''Performed on mouse click during recording'''
        self.print_click(x, y, button, pressed)
        self.append_click(x, y, button, pressed)


    @staticmethod
    def print_click(x, y, button, pressed):
        '''Print details of mouse click'''
        press_type  = 'pressed' if pressed else 'released'
        print(f'{button} mouse {press_type} at ({x},{y})')


    def append_click(self, x, y, button, pressed):
        '''Extract and append click data'''
        click_data = {
                        'time': self.time_elapsed(),
                        'mouse_bool': True,
                        'mouse_x': x, 
                        'mouse_y': y, 
                        'mouse_button': button, 
                        'mouse_pressed': pressed, 
                        'key': None, 
                        'key_pressed': None
                    }

        self.recorded_moves.append(click_data)


    def on_press(self, key):
        '''Performed on key press during recording'''
        if key == self.stop_key:
            print(f'Stop key {self.stop_key} pressed - stopping recording')
            self.recording = False
        else:
            self.print_key(key, True)
            self.append_press(key, True)


    def on_release(self, key):
        '''Performed on key press during recording'''
        self.print_key(key, False)
        self.append_press(key, False)


    @staticmethod
    def print_key(key, pressed):
        '''Print details of key pressed'''
        press_type  = 'pressed' if pressed else 'released'
        print(f'Key {key} {press_type}')

    
    def append_press(self, key, pressed):
        '''
        Extract and append key press data. 
        pressed True indicates pressed key, False indicates released
        '''
        press_data = {
                        'time': self.time_elapsed(),
                        'mouse_bool': False,
                        'mouse_x': None, 
                        'mouse_y': None, 
                        'mouse_button': None, 
                        'mouse_pressed': None, 
                        'key': key, 
                        'key_pressed': pressed
                    }

        self.recorded_moves.append(press_data)


    def record(self):
        '''Begin recording mouse and keyboard clicks'''
        self.on_record()
        while self.recording:
            continue
        self.on_stop()
    
    
    def on_record(self):
        '''Set up recording of kbm presses'''
        print('Begin recording keyboard and mouse inputs.\n'\
                 +'Press Esc key to exit.\n')
        self.recorded_moves = []
        self.start_time = time.time()
        self.recording = True

        #Start the listeners
        self.m_listener.start()
        self.kb_listener.start()


    def on_stop(self):
        '''Stop recording of kbm presses'''
        #Stop the listeners
        self.m_listener.stop()
        self.kb_listener.stop()


    def write(self, filepath):
        '''Write recorded moves to csv file'''
        df = pd.DataFrame(self.recorded_moves)
        df.to_csv(filepath)
        print(f'Recorded moves written to {filepath}')


    def time_elapsed(self):
        '''Returns time elapsed since start of recording'''
        return time.time() - self.start_time


    def play(self):
        '''Play back recorded mouse clicks and key presses'''
        self.on_play()

        #Iterate through stored moves
        for move in self.recorded_moves:
            move_time = move['time']
            self.wait(move_time)                    #Wait to execute next move
            self.execute_move(move)
        
        self.on_play_finish()

    def on_play(self):
        '''Set up for playback of recording'''
        self.start_time = time.time()
        print('Begin playback of recorded clicks/key presses')

    
    def wait(self, target_time):
        '''
        Wait until specified target_time has elapsed from self.start_time
        
        Raises TimeoutError if wait time exceeds self.timout
        '''
        while self.time_elapsed() < target_time:
            time.sleep(self.wait_time)
            if self.time_elapsed() >= self.timeout:
                raise TimeoutError('Timeout while waiting for next playback '+\
                                     'command')


    def execute_move(self, move, print_move = True):
        '''Execute a mouse/keyboard move'''
        mouse_bool = move['mouse_bool']

        #Mouse presses
        if mouse_bool:
            x, y, button, m_pressed = move['mouse_x'], move['mouse_y'], \
                                    move['mouse_button'], move['mouse_pressed']
            self.click_mouse(x, y, button, m_pressed)

            if print_move:
                self.print_click(x, y, button, m_pressed)

        #Keyboard presses
        else:
            key, k_pressed = move['key'], move['key_pressed']
            self.press_key(key, k_pressed)

            if print_move:
                self.print_key(key, k_pressed)


    def click_mouse(self, x, y, button, pressed):
        '''Execute a mouse click or release at desired (x, y) position'''
        self.m_controller.position = (x, y)

        if pressed:
            self.m_controller.press(button)
        else:
            self.m_controller.release(button)


    def press_key(self, key, pressed):
        '''Execute a key press or release'''
        if pressed:
            self.kb_controller.press(key)
        else:
            self.kb_controller.release(key)

    
    def on_play_finish(self):
        '''After finishing playback of record clicks/key presses'''
        print('Completed playback of clicks/key presses')


    def configure_display_compatibility(self, dpi_awareness = 2):
        '''
        Configure Windows 10 display settings for compatibility with different
        monitor DPIs (allows different resolutions and scaling to be used)
        '''
        dpi_awareness = 2
        print('\nConfiguring Windows 10 display settings')
        self.set_dpi_awareness(dpi_awareness)
        print(f'DPI awareness set to {dpi_awareness}\n')


    @staticmethod
    def get_dpi_awareness():
        '''
        Query display DPI awareness of the app - whether monitor resolution
        and scaling factors are accounted for. This affects the mouse position 
        of the recorder/controller.

        More info here:
        https://tinyurl.com/mu45xfp3
        '''
        dpi_awareness = ctypes.c_int()
        ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(dpi_awareness))
        print(f'DPI dpi_awareness value: {dpi_awareness.value}')
        if dpi_awareness.value == 0:
            print(textwrap.dedent(
                    '''
                    DPI unaware. This app does not scale for DPI changes and is 
                    always assumed to have a scale factor of 100% (96 DPI). It 
                    will be automatically scaled by the system on any other DPI 
                    setting.
                    '''
                    )
                )
        elif dpi_awareness.value == 1:
            print(textwrap.dedent(
                    '''
                    System DPI aware. This app does not scale for DPI changes. 
                    It will query for the DPI once and use that value for the 
                    lifetime of the app. If the DPI changes, the app will not 
                    adjust to the new DPI value. It will be automatically scaled
                    up or down by the system when the DPI changes from the 
                    system value.
                    '''
                    )
                )
        
        elif dpi_awareness.value == 2:
            print(textwrap.dedent(
                    '''
                    Per monitor DPI aware. This app checks for the DPI when it
                    is created and adjusts the scale factor whenever the DPI 
                    changes. These applications are not automatically scaled 
                    by the system.
                    '''
                    )
                )
        
        else:
            raise ValueError(f'DPI awareness value {dpi_awareness.value} not '+ \
                                'recognised')

        return dpi_awareness.value


    @staticmethod
    def set_dpi_awareness(dpi_awareness):
        '''
        Set display DPI awareness of the app - whether monitor resolution
        and scaling factors are accounted for. This affects the mouse position 
        of the recorder/controller.

        See self.query_dpi_awareness for levels.

        More info here:
        https://tinyurl.com/mu45xfp3
        '''
        error_code = ctypes.windll.shcore.SetProcessDpiAwareness(dpi_awareness)
        return error_code


if __name__ == '__main__':
    recorder = Recorder()
    recorder.configure_display_compatibility()
    recorder.record()
    recorder.write('recordings/test.csv')
    recorder.play()
    
