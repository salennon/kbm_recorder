'''
Class to record and play back mouse clicks and keyboard presses using pynput.

Note: May have compatibility issues with different OS and resolutions

TODO:
Add compatibility for Windows icon scaling
'''

from pynput import mouse, keyboard
import time
import pandas as pd

class Recorder():
    '''Class to handle recording and playback of mouse clicks'''

    def __init__(self):
        #Init keyboard and mouse listeners
        self.m_listener = mouse.Listener(on_click = self.on_click)
        self.kb_listener = keyboard.Listener(on_press = self.on_press, 
                             on_release = self.on_release)

        #Init keyboard and mouse controllers
        self.m_controller = mouse.Controller()
        self.kb_controller = keyboard.Controller()

        self.recording = False                  #Recording status
        self.recorded_moves = []                #Record of recorded moves
        self.start_time = time.time()           #Start time of recording
        self.stop_key = keyboard.Key.esc        #Key to stop recording

        self.timeout = 120        #Default timeout (s) for playback
        self.wait_time = 0.01     #Minimum time between executing playback steps


    def on_click(self, x, y, button, pressed):
        '''Performed on mouse click during recording'''
        press_type  = 'pressed' if pressed else 'released'
        print(f'{button} mouse {press_type} at ({x},{y})')
        self.append_click(x, y, button, pressed)


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
            print(f'Key {key} pressed')
            self.append_press(key, True)


    def on_release(self, key):
        '''Performed on key press during recording'''
        print(f'Key {key} released')
        self.append_press(key, False)

    
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


    def execute_move(self, move):
        '''Execute a mouse/keyboard move'''
        mouse_bool = move['mouse_bool']

        #Mouse presses
        if mouse_bool:
            x, y, button, m_pressed = move['mouse_x'], move['mouse_y'], \
                                    move['mouse_button'], move['mouse_pressed']
            self.click_mouse(x, y, button, m_pressed)

        #Keyboard presses
        else:
            key, k_pressed = move['key'], move['key_pressed']
            self.press_key(key, k_pressed)


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




if __name__ == '__main__':
    recorder = Recorder()
    recorder.record()
    recorder.write('recordings/test.csv')
    recorder.play()
    
