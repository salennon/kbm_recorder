
from pynput import mouse, keyboard
import time

class Recorder():

    def __init__(self):
        #Init keyboard and mouse listeners
        self.m_listener = mouse.Listener(on_click = self.on_click)
        self.kb_listener = keyboard.Listener(on_press = self.on_press, 
                             on_release = self.on_release)

        self.recording = False                  #Recording status
        self.recorded_moves = []                #Record of recorded moves
        self.start_time = time.time()           #Start time of recording
        self.stop_key = keyboard.Key.esc        #Key to stop recording


    def on_click(self, x, y, button, pressed):
        '''Performed on mouse click during recording'''
        press_type  = 'pressed' if pressed else 'released'
        print(f'{button} mouse {press_type} at ({x},{y})')
        self.append_click(x, y, button, pressed)


    def append_click(self, x, y, button, pressed):
        '''Extract and append click data. See save for format'''
        click_data = [
                        self.time_elapsed(),
                        True,
                        x, 
                        y, 
                        button, 
                        pressed, 
                        None, 
                        None
                    ]
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
        See save for format
        '''
        press_data = [
                        self.time_elapsed(),
                        False, 
                        None, 
                        None, 
                        None, 
                        None, 
                        key, 
                        pressed
                    ]
        self.recorded_moves.append(press_data)


    def record(self):
        '''Begin recording mouse and keyboard clicks'''
        self.on_record()
        while self.recording:
            continue
        self.on_stop()

        print(self.recorded_moves)
        

        # with self.m_listener as m_listener, self.kb_listener as kb_listener:
        #     m_listener.join()
        #     kb_listener.join()
    

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

    def time_elapsed(self):
        '''Returns time elapsed since start of recording'''
        return time.time() - self.start_time


    #Load
    #Save



if __name__ == '__main__':
    recorder = Recorder()
    recorder.record()
    
    
