
from pynput import mouse, keyboard

class Recorder():

    def __init__(self):
        #Init keyboard and mouse listeners
        self.m_listener = mouse.Listener(on_click = self.on_click)
        self.kb_listener = keyboard.Listener(on_press = self.on_press, 
                             on_release = self.on_release)

        self.recorded_moves = []

    def on_click(self, x, y, button, pressed):
        '''Performed on mouse click during recording'''
        press_type  = 'pressed' if pressed else 'released'
        print(f'{button} mouse {press_type} at ({x},{y})')

    def on_press(self, key):
        '''Performed on key press during recording'''
        print(f'Key {key} pressed')
    
    def on_release(self, key):
        '''Performed on key press during recording'''
        print(f'Key {key} released')

        


    def record(self):
        with self.m_listener as m_listener, self.kb_listener as kb_listener:
            m_listener.join()
            kb_listener.join()
        #self.m_listener.start()

    #Load
    #Save



if __name__ == '__main__':
    recorder = Recorder()
    recorder.record()
    
    
