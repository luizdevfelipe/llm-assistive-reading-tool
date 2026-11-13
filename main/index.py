
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
from app_config import MODOS
from markdown_renderer import MarkdownRenderer
from processing_overlay import ProcessingOverlay
from speech_service import SpeechService
from text_processing import gerar_adaptacao, validar_texto


# ============================================================
# CONFIGURAÇÃO DA INTERFACE GRÁFICA
# ============================================================

janela = tk.Tk()

janela.title("Ferramenta de leitura assistiva - Assistente de Acessibilidade Textual")
janela.geometry("900x760")
janela.minsize(760, 650)

estilo = ttk.Style()
estilo.configure(
    "Titulo.TLabel",
    font=("Arial", 17, "bold")
)

estilo.configure(
    "Descricao.TLabel",
    font=("Arial", 10)
)

estilo.configure(
    "Subtitulo.TLabel",
    font=("Arial", 11, "bold")
)


# ============================================================
# ESTADO DO PROCESSAMENTO
# ============================================================

fila_resultados = queue.Queue()
em_processamento = False
overlay = ProcessingOverlay(janela)
FAMILIA_FONTE_DISLEXIA = "OpenDyslexic"


# ============================================================
# EXECUÇÃO DO PROCESSAMENTO EM THREAD SEPARADA
# ============================================================

def trabalhador_llm(texto, modo):
    """
    Executa a solicitação ao LLM fora da thread da interface.

    A comunicação com a janela ocorre exclusivamente pela fila.
    """

    try:
        resultado = gerar_adaptacao(texto, modo)

        fila_resultados.put(
            ("sucesso", resultado)
        )

    except Exception as erro:
        fila_resultados.put(
            ("erro", str(erro))
        )


def iniciar_processamento():
    """
    Valida o texto, apresenta a sobreposição e inicia a thread.
    """

    global em_processamento

    if em_processamento:
        return

    try:
        texto = validar_texto(
            campo_entrada.get("1.0", "end-1c")
        )

    except ValueError as erro:
        messagebox.showwarning(
            "Texto inválido",
            str(erro)
        )
        return

    modo = modo_var.get()

    if modo not in MODOS:
        messagebox.showwarning(
            "Modo inválido",
            "Selecione uma opção de processamento."
        )
        return

    em_processamento = True

    botao_processar.configure(
        state="disabled"
    )

    status_var.set(
        f"Processando: {modo}..."
    )

    overlay.mostrar()

    thread = threading.Thread(
        target=trabalhador_llm,
        args=(texto, modo),
        daemon=True
    )

    thread.start()



# ============================================================
# VERIFICAÇÃO DOS RESULTADOS
# ============================================================

def verificar_resultados():
    global em_processamento

    try:
        estado, conteudo = fila_resultados.get_nowait()

        overlay.esconder()

        em_processamento = False

        botao_processar.configure(
            state="normal"
        )

        if estado == "sucesso":

            renderizador_markdown.renderizar(conteudo)

            if leitura_ativa:
                status_var.set("Realizando leitura...")
            else:
                status_var.set("Processamento concluído.")

        else:

            if leitura_ativa:
                status_var.set("Realizando leitura...")
            else:
                status_var.set("Ocorreu um erro no processamento.")

            messagebox.showerror(
                "Erro no processamento",
                conteudo
            )

    except queue.Empty:
        pass

    try:
        if janela.winfo_exists():
            janela.after(
                100,
                verificar_resultados
            )

    except tk.TclError:
        pass


# ============================================================
# LEITURA EM VOZ ALTA - THREAD DEDICADA
# ============================================================

leitura_ativa = False
leitura_interrompendo = False
leitura_pronta = False
erro_leitura = None
voz_ptbr_encontrada = False
aviso_voz_exibido = False
fechamento_solicitado = False
servico_leitura = SpeechService()


def finalizar_leitura(erro=None):
    global leitura_ativa
    global leitura_interrompendo

    leitura_ativa = False
    leitura_interrompendo = False
    atualizar_status_leitura()

    if erro is not None:
        messagebox.showerror(
            "Erro de leitura",
            f"Não foi possível realizar a leitura.\n\n{erro}"
        )


def ler_resultado():
    global leitura_ativa
    global leitura_interrompendo
    global aviso_voz_exibido

    texto = campo_saida.get(
        "1.0",
        "end-1c"
    ).strip()

    if not texto:
        messagebox.showwarning(
            "Texto vazio",
            "Não existe conteúdo para realizar a leitura."
        )
        return

    if not leitura_pronta:
        detalhes = (
            f"\n\n{erro_leitura}"
            if erro_leitura
            else " Aguarde a inicialização e tente novamente."
        )
        messagebox.showerror(
            "Erro de leitura",
            "O mecanismo de leitura ainda não está disponível."
            + detalhes
        )
        return

    if leitura_ativa:
        return

    if not voz_ptbr_encontrada and not aviso_voz_exibido:
        messagebox.showwarning(
            "Voz em português",
            "Não foi encontrada uma voz identificada como "
            "português brasileiro no sistema.\n\n"
            "A leitura será realizada utilizando a voz padrão "
            "disponível. Para melhorar a pronúncia, instale uma "
            "voz pt-BR no Windows."
        )

        aviso_voz_exibido = True

    leitura_ativa = True
    leitura_interrompendo = False
    status_var.set("Realizando leitura...")
    servico_leitura.read(texto)


def parar_leitura():
    global leitura_interrompendo

    if not leitura_ativa:
        return

    leitura_interrompendo = True
    servico_leitura.stop()


def atualizar_status_leitura():
    if leitura_ativa:
        status_var.set(
            "Realizando leitura..."
        )
    elif em_processamento:
        status_var.set(
            f"Processando: {modo_var.get()}..."
        )
    else:
        status_var.set(
            "Pronto para utilizar."
        )


def verificar_eventos_leitura():
    global leitura_pronta
    global voz_ptbr_encontrada
    global erro_leitura
    global leitura_interrompendo

    while True:
        try:
            evento, detalhes = servico_leitura.events.get_nowait()
        except queue.Empty:
            break

        if evento == "pronto":
            leitura_pronta = True
            voz_ptbr_encontrada = detalhes
            erro_leitura = None
        elif evento == "concluida":
            finalizar_leitura()
        elif evento == "erro":
            finalizar_leitura(RuntimeError(detalhes))
        elif evento == "erro_interrupcao":
            leitura_interrompendo = False
            messagebox.showerror(
                "Erro de leitura",
                f"Não foi possível interromper a leitura.\n\n{detalhes}"
            )
        elif evento == "falha":
            leitura_pronta = False
            erro_leitura = detalhes
            if leitura_ativa:
                finalizar_leitura(RuntimeError(detalhes))

    if not fechamento_solicitado and janela.winfo_exists():
        janela.after(50, verificar_eventos_leitura)


def finalizar_fechamento():
    if servico_leitura.is_alive():
        janela.after(50, finalizar_fechamento)
    else:
        janela.destroy()


def fechar_janela():
    global fechamento_solicitado

    if fechamento_solicitado:
        return

    fechamento_solicitado = True
    overlay.esconder()
    servico_leitura.shutdown()
    janela.after(50, finalizar_fechamento)


# ============================================================
# PERSONALIZAÇÃO VISUAL
# ============================================================

def aplicar_configuracoes():
    """
    Aplica as configurações de fonte e contraste
    aos campos de entrada e saída.
    """

    try:
        tamanho_fonte = int(
            fonte_var.get()
        )
    except ValueError:
        tamanho_fonte = 12

    if contraste_var.get() == "Alto contraste":
        fundo = "#000000"
        texto = "#FFFFFF"
        cursor = "#FFFF00"
        selecao_fundo = "#FFFF00"
        selecao_texto = "#000000"

    else:
        fundo = "#FFFFFF"
        texto = "#222222"
        cursor = "#222222"
        selecao_fundo = "#B5D5FF"
        selecao_texto = "#000000"

    familia_fonte = (
        FAMILIA_FONTE_DISLEXIA
        if fonte_dislexia_var.get()
        else "Arial"
    )

    configuracoes = {
        "font": (familia_fonte, tamanho_fonte),
        "bg": fundo,
        "fg": texto,
        "insertbackground": cursor,
        "selectbackground": selecao_fundo,
        "selectforeground": selecao_texto
    }

    campo_entrada.configure(
        **configuracoes
    )

    campo_saida.configure(
        **configuracoes
    )

    renderizador_markdown.aplicar_formatacao(
        tamanho_fonte,
        familia_fonte
    )


def alterar_fonte_dislexia():
    if fonte_dislexia_var.get():
        familias_disponiveis = tkfont.families(root=janela)
        if FAMILIA_FONTE_DISLEXIA.casefold() not in {
            familia.casefold()
            for familia in familias_disponiveis
        }:
            fonte_dislexia_var.set(False)
            aplicar_configuracoes()
            messagebox.showwarning(
                "Fonte indisponível",
                "A fonte OpenDyslexic não está instalada ou disponível "
                "para o Tkinter. Instale os arquivos OTF da família "
                "OpenDyslexic no Windows e reinicie o aplicativo."
            )
            return

    aplicar_configuracoes()


def restaurar_padrao():
    fonte_var.set("12")
    contraste_var.set("Padrão")
    fonte_dislexia_var.set(False)

    aplicar_configuracoes()


# ============================================================
# CONSTRUÇÃO DA INTERFACE
# ============================================================

principal = ttk.Frame(
    janela,
    padding=18
)

principal.pack(
    fill="both",
    expand=True
)

principal.columnconfigure(
    0,
    weight=1
)

principal.rowconfigure(
    3,
    weight=1
)

principal.rowconfigure(
    6,
    weight=2
)


# Título e descrição.

ttk.Label(
    principal,
    text="Ferramenta de leitura assistiva",
    style="Titulo.TLabel"
).grid(
    row=0,
    column=0,
    sticky="w",
    pady=(0, 4)
)

ttk.Label(
    principal,
    text=(
        "Assistente de acessibilidade textual. "
        "Adapte conteúdos para facilitar sua compreensão."
    ),
    style="Descricao.TLabel"
).grid(
    row=1,
    column=0,
    sticky="w",
    pady=(0, 16)
)


# Campo de entrada.

ttk.Label(
    principal,
    text="Texto original",
    style="Subtitulo.TLabel"
).grid(
    row=2,
    column=0,
    sticky="w",
    pady=(0, 6)
)

campo_entrada = scrolledtext.ScrolledText(
    principal,
    height=9,
    wrap=tk.WORD,
    font=("Arial", 12)
)

campo_entrada.grid(
    row=3,
    column=0,
    sticky="nsew",
    pady=(0, 12)
)


# Opções de processamento.

frame_opcoes = ttk.Frame(principal)

frame_opcoes.grid(
    row=4,
    column=0,
    sticky="ew",
    pady=(0, 12)
)

ttk.Label(
    frame_opcoes,
    text="Tipo de adaptação:"
).pack(
    side="left",
    padx=(0, 8)
)

modo_var = tk.StringVar(
    value="Simplificação"
)

seletor_modo = ttk.Combobox(
    frame_opcoes,
    textvariable=modo_var,
    values=list(MODOS.keys()),
    state="readonly",
    width=27
)

seletor_modo.pack(
    side="left",
    padx=(0, 12)
)

botao_processar = ttk.Button(
    frame_opcoes,
    text="Processar texto",
    command=iniciar_processamento
)

botao_processar.pack(
    side="left"
)


# Campo de saída.

ttk.Label(
    principal,
    text="Texto adaptado",
    style="Subtitulo.TLabel"
).grid(
    row=5,
    column=0,
    sticky="w",
    pady=(0, 6)
)

campo_saida = scrolledtext.ScrolledText(
    principal,
    height=12,
    wrap=tk.WORD,
    font=("Arial", 12)
)

campo_saida.grid(
    row=6,
    column=0,
    sticky="nsew",
    pady=(0, 12)
)

renderizador_markdown = MarkdownRenderer(campo_saida)

# Botões de leitura.

frame_leitura = ttk.Frame(principal)

frame_leitura.grid(
    row=7,
    column=0,
    sticky="w",
    pady=(0, 14)
)

ttk.Button(
    frame_leitura,
    text="Ler resultado",
    command=ler_resultado
).pack(
    side="left",
    padx=(0, 8)
)

ttk.Button(
    frame_leitura,
    text="Parar leitura",
    command=parar_leitura
).pack(
    side="left"
)


# Configurações de acessibilidade.

frame_acessibilidade = ttk.LabelFrame(
    principal,
    text="Personalização visual",
    padding=10
)

frame_acessibilidade.grid(
    row=8,
    column=0,
    sticky="ew",
    pady=(0, 10)
)

fonte_var = tk.StringVar(
    value="12"
)

contraste_var = tk.StringVar(
    value="Padrão"
)

fonte_dislexia_var = tk.BooleanVar(
    value=False
)

ttk.Label(
    frame_acessibilidade,
    text="Tamanho da fonte:"
).pack(
    side="left",
    padx=(0, 6)
)

seletor_fonte = ttk.Combobox(
    frame_acessibilidade,
    textvariable=fonte_var,
    values=["12", "14", "16", "18", "20"],
    state="readonly",
    width=5
)

seletor_fonte.pack(
    side="left",
    padx=(0, 18)
)

ttk.Label(
    frame_acessibilidade,
    text="Contraste:"
).pack(
    side="left",
    padx=(0, 6)
)

seletor_contraste = ttk.Combobox(
    frame_acessibilidade,
    textvariable=contraste_var,
    values=["Padrão", "Alto contraste"],
    state="readonly",
    width=18
)

seletor_contraste.pack(
    side="left",
    padx=(0, 10)
)

ttk.Checkbutton(
    frame_acessibilidade,
    text="Usar fonte OpenDyslexic",
    variable=fonte_dislexia_var,
    command=alterar_fonte_dislexia
).pack(
    side="left",
    padx=(0, 12)
)

ttk.Button(
    frame_acessibilidade,
    text="Restaurar padrão",
    command=restaurar_padrao
).pack(
    side="left"
)


# Atualiza a aparência quando as opções são alteradas.

seletor_fonte.bind(
    "<<ComboboxSelected>>",
    lambda evento: aplicar_configuracoes()
)

seletor_contraste.bind(
    "<<ComboboxSelected>>",
    lambda evento: aplicar_configuracoes()
)


# Status da aplicação.

status_var = tk.StringVar(
    value="Pronto para utilizar."
)

ttk.Label(
    principal,
    textvariable=status_var,
    style="Descricao.TLabel"
).grid(
    row=9,
    column=0,
    sticky="w"
)


# Aplica a configuração visual inicial.

aplicar_configuracoes()


# ============================================================
# ENCERRAMENTO E INICIALIZAÇÃO
# ============================================================

janela.protocol(
    "WM_DELETE_WINDOW",
    fechar_janela
)

# Inicia a verificação dos resultados da thread.
janela.after(
    100,
    verificar_resultados
)

servico_leitura.start()
janela.after(50, verificar_eventos_leitura)

janela.mainloop()
