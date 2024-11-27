import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from m_token import CompilerError
from paser import Parser
from lexer import Lexer

class TokenTree:
    def __init__(self, parent):
        self.tree = ttk.Treeview(parent, height=10)
        self.setup_tree()
        
    def setup_tree(self):
        self.tree['columns'] = ('value', 'line')
        self.tree.column('#0', width=200)
        self.tree.column('value', width=150)
        self.tree.column('line', width=70)
        
        self.tree.heading('#0', text='Token')
        self.tree.heading('value', text='Value')
        self.tree.heading('line', text='Line')

class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Compilador Olga y Brayan")
        self.setup_styles()
        self.setup_gui()
        self.setup_bindings()
        self.current_file = None

    def setup_styles(self):
        # Configurar estilos personalizados para tema Dracula
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores del tema Dracula
        self.dracula = {
            'background': '#282a36',
            'current_line': '#44475a',
            'foreground': '#BF00E6',
            'comment': '#6272a4',
            'cyan': '#8be9fd',
            'green': '#50fa7b',
            'orange': '#ffb86c',
            'pink': '#ff79c6',
            'purple': '#bd93f9',
            'red': '#ff5555',
            'yellow': '#f1fa8c'
        }
        
        # Aplicar estilos Dracula
        style.configure('Editor.TFrame', background=self.dracula['background'])
        style.configure('Results.TFrame', background=self.dracula['background'])
        style.configure('Custom.TButton', 
                       padding=5, 
                       background=self.dracula['purple'], 
                       foreground=self.dracula['background'])
        style.configure('TLabel', 
                       background=self.dracula['background'], 
                       foreground=self.dracula['foreground'])
        style.configure('TEntry', 
                       background=self.dracula['current_line'], 
                       foreground=self.dracula['foreground'])
        style.configure('TText', 
                       background=self.dracula['background'], 
                       foreground=self.dracula['foreground'])
        style.configure('TNotebook', 
                       background=self.dracula['background'])
        style.configure('TNotebook.Tab', 
                       background=self.dracula['current_line'], 
                       foreground=self.dracula['foreground'])
        style.configure('TMenu',
                        background=self.dracula['background'],
                        foreground=self.dracula['foreground'])

    def setup_gui(self):
        # Configurar el layout principal
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        # Panel izquierdo - Editor
        self.editor_frame = ttk.Frame(self.main_paned, style='Editor.TFrame')
        self.main_paned.add(self.editor_frame, weight=3)

        # Panel derecho - Resultados
        self.results_paned = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
        self.main_paned.add(self.results_paned, weight=2)

        self.setup_toolbar()
        self.setup_editor()
        self.setup_results()
        self.setup_menu()
        self.setup_status_bar()

    def setup_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=2)

        # Botones con mejor espaciado y estilo
        ttk.Button(toolbar, text="Nuevo", style='Custom.TButton', 
                  command=self.new_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Abrir", style='Custom.TButton',
                  command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Guardar", style='Custom.TButton',
                  command=self.save_file).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        ttk.Button(toolbar, text="Compilar", style='Custom.TButton',
                  command=self.analyze_code).pack(side=tk.LEFT, padx=2)


    def setup_editor(self):
        # Frame para el editor con números de línea
        editor_container = ttk.Frame(self.editor_frame)
        editor_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Números de línea
        self.line_numbers = tk.Text(editor_container, width=4, padx=3, takefocus=0,
                                  background=self.dracula['current_line'], 
                                  foreground=self.dracula['comment'],
                                  state='disabled')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Editor principal
        self.code_text = scrolledtext.ScrolledText(editor_container, wrap=tk.NONE,
                                                 font=('Consolas', 11), 
                                                 background=self.dracula['background'], 
                                                 foreground=self.dracula['foreground'])
        self.code_text.pack(fill=tk.BOTH, expand=True)

        # Configurar tags para resaltado de sintaxis
        self.setup_syntax_highlighting()

    def setup_results(self):
        # Notebook para resultados
        self.notebook = ttk.Notebook(self.results_paned)
        self.results_paned.add(self.notebook, weight=1)

        # Pestañas de resultados
        self.tokens_text = scrolledtext.ScrolledText(self.notebook, height=10,
                                                   font=('Consolas', 12), 
                                                   background=self.dracula['background'], 
                                                   foreground=self.dracula['foreground'])
        
        self.errors_text = scrolledtext.ScrolledText(self.notebook, height=10,
                                                   font=('Consolas', 15, 'bold'), 
                                                   background=self.dracula['background'], 
                                                   foreground=self.dracula['red'])
        
        self.tokens_tree = ttk.Treeview(self.notebook, height=10)
        self.tokens_tree.heading('#0', text='Tokens', anchor='w')
        style = ttk.Style()
        style.configure('Treeview', 
                    background=self.dracula['background'],
                    foreground=self.dracula['foreground'],
                    fieldbackground=self.dracula['background'])
        style.configure('Treeview.Heading',
                    background=self.dracula['current_line'],
                    foreground=self.dracula['foreground'])
    
        self.console = scrolledtext.ScrolledText(self.notebook, height=10,
                                               font=('Consolas', 15, 'bold'), 
                                               background=self.dracula['background'], 
                                               foreground=self.dracula['green'])

        self.notebook.add(self.tokens_text, text='Tokens')
        self.notebook.add(self.tokens_tree, text='Tokens Tree')
        #self.notebook.add(self.console, text='Consola')
        self.notebook.add(self.errors_text, text='Estatus de Compilacion')

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Guardar", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)

       
        # Menú Compilador
        compiler_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Compilador", menu=compiler_menu)
        compiler_menu.add_command(label="Compilar", command=self.analyze_code, accelerator="F5")
        compiler_menu.add_command(label="Limpiar resultados", command=self.clear_results)

    def setup_status_bar(self):
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_bar, text="Listo")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.position_label = ttk.Label(self.status_bar, text="Ln 1, Col 1")
        self.position_label.pack(side=tk.RIGHT, padx=5)

    def setup_syntax_highlighting(self):
        self.code_text.tag_configure("keyword", foreground=self.dracula['pink'])
        self.code_text.tag_configure("string", foreground=self.dracula['yellow'])
        self.code_text.tag_configure("comment", foreground=self.dracula['comment'])
        self.code_text.tag_configure("number", foreground=self.dracula['purple'])
        self.code_text.tag_configure("error", background=self.dracula['red'], 
                                   foreground=self.dracula['foreground'])


    def setup_bindings(self):
        self.code_text.bind('<KeyRelease>', self.update_line_numbers)
        self.code_text.bind('<KeyRelease>', self.highlight_syntax, add='+')
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<F5>', lambda e: self.analyze_code())

    def highlight_syntax(self, event=None):
        # Eliminar resaltado existente
        for tag in ["keyword", "string", "comment", "number"]:
            self.code_text.tag_remove(tag, "1.0", "end")
        
        content = self.code_text.get("1.0", "end-1c")
        
        # Keywords
        keywords = ['if', 'else', 'while', 'for', 'int', 'float', 'string', 
                   'boolean', 'print', 'input', 'return', 'void', 'class',
                   'public', 'private', 'true', 'false']
        
        for keyword in keywords:
            start = "1.0"
            while True:
                start = self.code_text.search(r'\y' + keyword + r'\y', start, "end", regexp=True)
                if not start:
                    break
                end = f"{start}+{len(keyword)}c"
                self.code_text.tag_add("keyword", start, end)
                start = end

        # Strings
        start = "1.0"
        while True:
            start = self.code_text.search(r'["\'](.*?)["\']', start, "end", regexp=True)
            if not start:
                break
            end = self.code_text.search(r'["\']', self.code_text.index(f"{start}+1c"), "end")
            if not end:
                break
            end = self.code_text.index(f"{end}+1c")
            self.code_text.tag_add("string", start, end)
            start = end

        # Comments
        start = "1.0"
        while True:
            start = self.code_text.search("//", start, "end")
            if not start:
                break
            line = start.split('.')[0]
            end = f"{line}.end"
            self.code_text.tag_add("comment", start, end)
            start = self.code_text.index(f"{line}.end+1c")

    def update_line_numbers(self, event=None):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete("1.0", "end")
        
        text_content = self.code_text.get("1.0", "end-1c")
        lines = text_content.count('\n') + 1
        line_numbers = '\n'.join(str(i) for i in range(1, lines + 1))
        
        self.line_numbers.insert("1.0", line_numbers)
        self.line_numbers.config(state='disabled')
        
        # Actualizar posición del cursor
        cursor_pos = self.code_text.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        self.position_label.config(text=f"Ln {line}, Col {int(col)+1}")

    def new_file(self):
        self.code_text.delete(1.0, tk.END)
        self.current_file = None
        self.status_label.config(text="Nuevo archivo")
        self.clear_results()

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos Python", "*.py"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    self.code_text.delete(1.0, tk.END)
                    self.code_text.insert(1.0, content)
                    self.current_file = file_path
                    self.status_label.config(text=f"Archivo abierto: {file_path}")
                    self.update_line_numbers()
                    self.highlight_syntax()
            except Exception as e:
                messagebox.showerror("Error", f"Error al abrir el archivo: {str(e)}")

    def save_file(self):
        if not self.current_file:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[("Archivos Python", "*.py"), ("Todos los archivos", "*.*")]
            )
            if not file_path:
                return
            self.current_file = file_path
        
        try:
            content = self.code_text.get(1.0, tk.END)
            with open(self.current_file, 'w') as file:
                file.write(content)
            self.status_label.config(text=f"Archivo guardado: {self.current_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el archivo: {str(e)}")

    def analyze_code(self):
        self.clear_results()
        code = self.code_text.get("1.0", tk.END)
        
        try:
            # Análisis léxico
            lexer = Lexer()
            tokens = lexer.tokenize(code)
            
            # Mostrar tokens
            self.tokens_text.insert(tk.END, "=== Tokens Encontrados ===\n\n")
            for token in tokens:
                self.tokens_text.insert(tk.END, f"{token}\n")
            
            # Limpiar árbol
            self.tokens_tree.delete(*self.tokens_tree.get_children())
            
            # Variables para tracking del scope
            scope_stack = ['global']
            current_parent = ''
            scope_level = 0
            
            for token in tokens:
                token_str = str(token)
                token_parts = token_str.split()
                token_type = token_parts[0]
                token_value = ' '.join(token_parts[1:]) if len(token_parts) > 1 else ''
                
                # Manejar cambios de scope
                if token_type == 'DELIMITER':
                    if token_value == '{':
                        scope_level += 1
                        parent_id = self.tokens_tree.insert(current_parent, 'end', 
                                                        text=f"Scope Level {scope_level}",
                                                        open=True)
                        current_parent = parent_id
                        scope_stack.append(parent_id)
                    elif token_value == '}':
                        scope_level -= 1
                        scope_stack.pop()
                        current_parent = scope_stack[-1] if scope_stack else ''
                        
                # Insertar token en el árbol
                item_id = self.tokens_tree.insert(current_parent, 'end',
                                                text=token_type,
                                                values=(token_value, ''),
                                                tags=('token',))
                
                # Si es inicio de función o clase, crear nuevo scope
                if token_type == 'KEYWORD' and token_value in ('class', 'def'):
                    current_parent = item_id
                    scope_stack.append(item_id)
        
        
            # Análisis sintáctico y semántico
            parser = Parser(tokens)
            parser.parse()
            
            self.console.insert(tk.END, "¡Compilación exitosa!\n", "success")
            self.errors_text.insert(tk.END, "¡Compilación exitosa!\n", "success")
            self.console.tag_configure("success", foreground=self.dracula['green'])
            self.errors_text.tag_configure("success", foreground=self.dracula['green'])
            self.status_label.config(text="Compilación completada")
            self.notebook.select(1)

            
            
        except CompilerError as e:
            self.errors_text.insert(tk.END, str(e))
            self.highlight_error(e.line, e.position)
            self.status_label.config(text="Error de compilación")
            self.console.insert(tk.END, "Compilación fallida\n")
            self.notebook.select(1)  # Mostrar pestaña de errores
        except Exception as e:
            self.errors_text.insert(tk.END, f"Error inesperado: {str(e)}")
            self.console.insert(tk.END, "Compilación fallida\n")
            self.status_label.config(text="Error inesperado")

    def highlight_error(self, line, position):
        self.code_text.tag_remove("error", "1.0", tk.END)
        start_index = f"{line}.{position}"
        end_index = f"{line}.{position + 1}"
        self.code_text.tag_add("error", start_index, end_index)
        self.code_text.see(start_index)

    def clear_results(self):
        self.tokens_text.delete("1.0", tk.END)
        self.errors_text.delete("1.0", tk.END)
        self.console.delete("1.0", tk.END)
        self.code_text.tag_remove("error", "1.0", tk.END)
