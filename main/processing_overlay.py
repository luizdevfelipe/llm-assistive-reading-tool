import tkinter as tk
from tkinter import ttk


class ProcessingOverlay:
    """Gerencia a sobreposição modal exibida durante o processamento do texto."""

    def __init__(self, janela):
        self.janela = janela
        self.janela_overlay = None
        self.barra_progresso = None
        self.janela.bind("<Configure>", self._sincronizar)

    def _sincronizar(self, event=None):
        if self.janela_overlay is None:
            return

        if event is not None and event.widget != self.janela:
            return

        try:
            x = self.janela.winfo_rootx()
            y = self.janela.winfo_rooty()
            largura = self.janela.winfo_width()
            altura = self.janela.winfo_height()
            self.janela_overlay.geometry(
                f"{largura}x{altura}+{x}+{y}"
            )
        except tk.TclError:
            pass

    def mostrar(self):
        self.janela.update_idletasks()

        self.janela_overlay = tk.Toplevel(self.janela)
        self.janela_overlay.overrideredirect(True)
        self.janela_overlay.transient(self.janela)
        self._sincronizar()
        self.janela_overlay.configure(bg="#E9EDF3")

        try:
            self.janela_overlay.attributes("-alpha", 0.94)
        except tk.TclError:
            pass

        self.janela_overlay.lift()

        cartao = tk.Frame(
            self.janela_overlay,
            bg="white",
            padx=35,
            pady=30,
            highlightbackground="#D0D7E2",
            highlightthickness=1
        )
        cartao.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            cartao,
            text="Pensando...",
            font=("Arial", 19, "bold"),
            bg="white",
            fg="#243247"
        ).pack(pady=(0, 10))

        tk.Label(
            cartao,
            text="O modelo está analisando o conteúdo.",
            font=("Arial", 11),
            bg="white",
            fg="#4B5563"
        ).pack(pady=(0, 20))

        self.barra_progresso = ttk.Progressbar(
            cartao,
            mode="indeterminate",
            length=260
        )
        self.barra_progresso.pack()
        self.barra_progresso.start(12)
        self.janela_overlay.update_idletasks()
        self.janela_overlay.grab_set()

    def esconder(self):
        if self.barra_progresso is not None:
            try:
                self.barra_progresso.stop()
            except tk.TclError:
                pass
            self.barra_progresso = None

        if self.janela_overlay is not None:
            try:
                self.janela_overlay.grab_release()
                self.janela_overlay.destroy()
            except tk.TclError:
                pass
            self.janela_overlay = None
