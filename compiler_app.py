import flet as ft
from m_token import CompilerError
from paser import Parser
from lexer import Lexer

class CompilerGUI:
    def __init__(self):
        self.current_file = None
        ft.app(target=self.main)

    def main(self, page: ft.Page):
        # Configuración de la página
        page.title = "Compilador Olga y Brayan"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 20

        # Editor de código
        self.code_editor = ft.TextField(
            multiline=True,
            min_lines=20,
            max_lines=20,
            text_style=ft.TextStyle(family="Consolas", size=14),
            border_color=ft.colors.PURPLE_400,
            bgcolor=ft.colors.SURFACE_VARIANT,
        )

        # Área de resultados
        self.results_tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="Tokens",
                    content=ft.TextField(
                        multiline=True,
                        read_only=True,
                        min_lines=10,
                        max_lines=10,
                        text_style=ft.TextStyle(family="Consolas", size=12),
                    ),
                ),
                ft.Tab(
                    text="Estatus de Compilación",
                    content=ft.TextField(
                        multiline=True,
                        read_only=True,
                        min_lines=10,
                        max_lines=10,
                        text_style=ft.TextStyle(
                            family="Consolas",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ),
                ),
            ],
        )

        # Barra de herramientas
        toolbar = ft.Row(
            controls=[
                ft.ElevatedButton("Nuevo", on_click=self.new_file),
                ft.ElevatedButton("Abrir", on_click=self.open_file),
                ft.ElevatedButton("Guardar", on_click=self.save_file),
                ft.VerticalDivider(),
                ft.ElevatedButton("Compilar", on_click=self.analyze_code),
            ],
            alignment=ft.MainAxisAlignment.START,
        )

        # Barra de estado
        self.status_bar = ft.Row(
            controls=[
                ft.Text("Listo", size=12),
            ],
            alignment=ft.MainAxisAlignment.START,
        )

        # Layout principal
        page.add(
            toolbar,
            self.code_editor,
            self.results_tabs,
            self.status_bar,
        )

    def new_file(self, e):
        self.code_editor.value = ""
        self.current_file = None
        self.status_bar.controls[0].value = "Nuevo archivo"
        self.clear_results()
        self.code_editor.update()
        self.status_bar.update()

    def open_file(self, e):
        def on_dialog_result(e: ft.FilePickerResultEvent):
            if e.files:
                file_path = e.files[0].path
                try:
                    with open(file_path, 'r') as file:
                        self.code_editor.value = file.read()
                        self.current_file = file_path
                        self.status_bar.controls[0].value = f"Archivo abierto: {file_path}"
                        self.code_editor.update()
                        self.status_bar.update()
                except Exception as ex:
                    print(f"Error al abrir el archivo: {str(ex)}")

        file_picker = ft.FilePicker(
            on_result=on_dialog_result
        )
        self.page.overlay.append(file_picker)
        file_picker.pick_files(
            allowed_extensions=["py"],
            allow_multiple=False
        )

    def save_file(self, e):
        def on_dialog_result(e: ft.FilePickerResultEvent):
            if e.path:
                try:
                    with open(e.path, 'w') as file:
                        file.write(self.code_editor.value)
                    self.current_file = e.path
                    self.status_bar.controls[0].value = f"Archivo guardado: {e.path}"
                    self.status_bar.update()
                except Exception as ex:
                    print(f"Error al guardar el archivo: {str(ex)}")

        if not self.current_file:
            save_file_dialog = ft.FilePicker(
                on_result=on_dialog_result
            )
            self.page.overlay.append(save_file_dialog)
            save_file_dialog.save_file(
                allowed_extensions=["py"],
                file_name="nuevo_archivo.py"
            )
        else:
            try:
                with open(self.current_file, 'w') as file:
                    file.write(self.code_editor.value)
                self.status_bar.controls[0].value = f"Archivo guardado: {self.current_file}"
                self.status_bar.update()
            except Exception as ex:
                print(f"Error al guardar el archivo: {str(ex)}")

    def analyze_code(self, e):
        self.clear_results()
        code = self.code_editor.value

        try:
            # Análisis léxico
            lexer = Lexer()
            tokens = lexer.tokenize(code)
            
            # Mostrar tokens
            tokens_text = "=== Tokens Encontrados ===\n\n"
            for token in tokens:
                tokens_text += f"{token}\n"
            
            self.results_tabs.tabs[0].content.value = tokens_text
            
            # Análisis sintáctico y semántico
            parser = Parser(tokens)
            parser.parse()
            
            self.results_tabs.tabs[1].content.value = "¡Compilación exitosa!"
            self.results_tabs.tabs[1].content.color = ft.colors.GREEN
            self.status_bar.controls[0].value = "Compilación completada"
            
        except CompilerError as e:
            self.results_tabs.tabs[1].content.value = str(e)
            self.results_tabs.tabs[1].content.color = ft.colors.RED
            self.status_bar.controls[0].value = "Error de compilación"
        except Exception as e:
            self.results_tabs.tabs[1].content.value = f"Error inesperado: {str(e)}"
            self.status_bar.controls[0].value = "Error inesperado"

        self.results_tabs.update()
        self.status_bar.update()

    def clear_results(self):
        self.results_tabs.tabs[0].content.value = ""
        self.results_tabs.tabs[1].content.value = ""
        self.results_tabs.update()

if __name__ == "__main__":
    CompilerGUI()
