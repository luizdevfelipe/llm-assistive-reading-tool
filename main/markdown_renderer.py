import re


class MarkdownRenderer:
    """Renderiza a versão simplificada de Markdown no campo de texto Tk."""

    def __init__(self, campo_saida):
        self.campo_saida = campo_saida

    def aplicar_formatacao(self, tamanho_fonte, familia_fonte="Arial"):
        def tamanho_escalado(tamanho_base):
            return round(tamanho_base * tamanho_fonte / 12)

        self.campo_saida.tag_configure(
            "h1",
            font=(familia_fonte, tamanho_escalado(19), "bold"),
            spacing1=12,
            spacing3=8
        )
        self.campo_saida.tag_configure(
            "h2",
            font=(familia_fonte, tamanho_escalado(15), "bold"),
            spacing1=10,
            spacing3=6
        )
        self.campo_saida.tag_configure(
            "h3",
            font=(familia_fonte, tamanho_escalado(13), "bold"),
            spacing1=8,
            spacing3=4
        )
        self.campo_saida.tag_configure(
            "bold",
            font=(familia_fonte, tamanho_fonte, "bold")
        )
        self.campo_saida.tag_configure(
            "italic",
            font=(familia_fonte, tamanho_fonte, "italic")
        )
        self.campo_saida.tag_configure(
            "code",
            font=(familia_fonte, tamanho_escalado(11)),
            background="#E8E8E8",
            foreground="#333333"
        )
        self.campo_saida.tag_configure(
            "quote",
            lmargin1=20,
            lmargin2=20,
            foreground="#555555",
            font=(familia_fonte, tamanho_fonte, "italic"),
            spacing1=4,
            spacing3=4
        )
        self.campo_saida.tag_configure(
            "bullet",
            lmargin1=20,
            lmargin2=35,
            spacing1=2
        )
        self.campo_saida.tag_configure(
            "numbered",
            lmargin1=20,
            lmargin2=35,
            spacing1=2
        )
        self.campo_saida.tag_configure(
            "separator",
            foreground="#999999"
        )

    def _inserir_texto(self, texto, tag=None):
        if tag:
            self.campo_saida.insert("end", texto, tag)
        else:
            self.campo_saida.insert("end", texto)

    def _renderizar_inline(self, texto, tag_base=None):
        padrao = re.compile(
            r"(\*\*.+?\*\*|__.+?__|\*.+?\*|_.+?_|`.+?`)"
        )

        for parte in padrao.split(texto):
            if not parte:
                continue

            if (
                (parte.startswith("**") and parte.endswith("**"))
                or (parte.startswith("__") and parte.endswith("__"))
            ):
                self._inserir_texto(parte[2:-2], "bold")
            elif (
                parte.startswith("*")
                and parte.endswith("*")
                and len(parte) > 2
            ):
                self._inserir_texto(parte[1:-1], "italic")
            elif (
                parte.startswith("_")
                and parte.endswith("_")
                and len(parte) > 2
            ):
                self._inserir_texto(parte[1:-1], "italic")
            elif parte.startswith("`") and parte.endswith("`"):
                self._inserir_texto(parte[1:-1], "code")
            else:
                self._inserir_texto(parte, tag_base)

    def renderizar(self, texto):
        self.campo_saida.delete("1.0", "end")

        for linha in texto.splitlines():
            conteudo = linha.strip()

            if not conteudo:
                self.campo_saida.insert("end", "\n")
                continue

            if re.match(r"^(-{3,}|\*{3,}|_{3,})$", conteudo):
                self._inserir_texto(
                    "────────────────────────────\n",
                    "separator"
                )
                continue

            titulo = re.match(r"^(#{1,3})\s+(.+)$", conteudo)
            if titulo:
                nivel = len(titulo.group(1))
                self._inserir_texto(
                    titulo.group(2) + "\n",
                    f"h{nivel}"
                )
                continue

            if conteudo.startswith(">"):
                self._renderizar_inline(conteudo[1:].strip(), "quote")
                self.campo_saida.insert("end", "\n")
                continue

            item_lista = re.match(r"^[-*+]\s+(.+)$", conteudo)
            if item_lista:
                self.campo_saida.insert("end", "• ", "bullet")
                self._renderizar_inline(item_lista.group(1), "bullet")
                self.campo_saida.insert("end", "\n")
                continue

            item_numerado = re.match(r"^(\d+)[.)]\s+(.+)$", conteudo)
            if item_numerado:
                self.campo_saida.insert(
                    "end",
                    f"{item_numerado.group(1)}. ",
                    "numbered"
                )
                self._renderizar_inline(item_numerado.group(2), "numbered")
                self.campo_saida.insert("end", "\n")
                continue

            self._renderizar_inline(conteudo)
            self.campo_saida.insert("end", "\n")

        self.campo_saida.see("1.0")
