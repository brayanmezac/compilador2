import flet as ft

def main(page: ft.Page):
    page.add(ft.Text("Web Compiler"))
    
    code_input = ft.TextField(
        multiline=True, 
        min_lines=10, 
        expand=True
    )
    
    def compile_action(e):
        page.add(ft.Text(f"Code length: {len(code_input.value)}"))
    
    compile_button = ft.ElevatedButton("Compile", on_click=compile_action)
    
    page.add(
        ft.Row([
            ft.Column([
                ft.Text("Code Editor"),
                code_input,
                compile_button
            ])
        ])
    )

ft.app(target=main, port=8550, view=ft.AppView.WEB_BROWSER)