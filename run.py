import tkinter as tk
import tkinter.ttk as ttk


from gui import CompilerGUI


def main():
    root = tk.Tk()
    
    # Maximize window
    if root.tk.call('tk', 'windowingsystem') == 'win32':
        root.state('zoomed')  # Windows
    else:
        root.attributes('-zoomed', True)  # Linux and other platforms
        
    # Configurar estilo
    style = ttk.Style()
    style.theme_use('classic')  
    
    app = CompilerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()