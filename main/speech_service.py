import queue
import threading

import pyttsx3


class SpeechService:
    """Encapsula o mecanismo pyttsx3 e seu ciclo COM em uma thread própria."""

    def __init__(self):
        self._commands = queue.Queue()
        self.events = queue.Queue()
        self._thread = None

    def start(self):
        if self._thread is not None:
            raise RuntimeError("O serviço de leitura já foi iniciado.")

        self._thread = threading.Thread(
            target=self._run,
            daemon=True
        )
        self._thread.start()

    def read(self, texto):
        self._commands.put(("ler", texto))

    def stop(self):
        self._commands.put(("parar", None))

    def shutdown(self):
        self._commands.put(("encerrar", None))

    def is_alive(self):
        return self._thread is not None and self._thread.is_alive()

    @staticmethod
    def _configurar_voz_portuguesa(mecanismo):
        vozes = mecanismo.getProperty("voices")

        for voz in vozes:
            informacoes = [str(voz.id), str(voz.name)]

            if hasattr(voz, "languages"):
                for idioma in voz.languages:
                    if isinstance(idioma, bytes):
                        idioma = idioma.decode("utf-8", errors="ignore")
                    informacoes.append(str(idioma))

            dados = " ".join(informacoes).lower()
            if any(
                idioma in dados
                for idioma in ("brazil", "brasil", "pt-br", "pt_br")
            ):
                mecanismo.setProperty("voice", voz.id)
                return True

        for voz in vozes:
            informacoes = [str(voz.id), str(voz.name)]

            if hasattr(voz, "languages"):
                for idioma in voz.languages:
                    if isinstance(idioma, bytes):
                        idioma = idioma.decode("utf-8", errors="ignore")
                    informacoes.append(str(idioma))

            dados = " ".join(informacoes).lower()
            if "portuguese" in dados or "português" in dados:
                mecanismo.setProperty("voice", voz.id)
                return False

        return False

    def _run(self):
        mecanismo = None
        loop_iniciado = False
        estado = {
            "ativa": False,
            "interrompendo": False,
            "encerrar": False
        }

        try:
            mecanismo = pyttsx3.init()
            voz_encontrada = self._configurar_voz_portuguesa(mecanismo)
            mecanismo.setProperty("rate", 165)

            def ao_concluir_leitura(name=None, completed=None):
                estado["ativa"] = False
                estado["interrompendo"] = False
                self.events.put(("concluida", completed))

            def ao_ocorrer_erro_leitura(name=None, exception=None):
                estado["ativa"] = False
                estado["interrompendo"] = False
                self.events.put(("erro", str(exception)))

            mecanismo.connect("finished-utterance", ao_concluir_leitura)
            mecanismo.connect("error", ao_ocorrer_erro_leitura)
            mecanismo.startLoop(False)
            loop_iniciado = True
            self.events.put(("pronto", voz_encontrada))

            while True:
                try:
                    comando, conteudo = self._commands.get(timeout=0.01)
                except queue.Empty:
                    comando = None
                    conteudo = None

                if comando == "ler":
                    if estado["ativa"]:
                        self.events.put(
                            ("erro", "Já existe uma leitura em andamento.")
                        )
                    else:
                        try:
                            estado["ativa"] = True
                            mecanismo.say(conteudo)
                        except Exception as erro:
                            estado["ativa"] = False
                            self.events.put(("erro", str(erro)))

                elif comando == "parar":
                    if estado["ativa"] and not estado["interrompendo"]:
                        try:
                            mecanismo.stop()
                            estado["interrompendo"] = True
                        except Exception as erro:
                            self.events.put(
                                ("erro_interrupcao", str(erro))
                            )

                elif comando == "encerrar":
                    estado["encerrar"] = True
                    if estado["ativa"] and not estado["interrompendo"]:
                        try:
                            mecanismo.stop()
                            estado["interrompendo"] = True
                        except Exception as erro:
                            self.events.put(
                                ("erro_interrupcao", str(erro))
                            )

                if estado["encerrar"] and not estado["ativa"]:
                    break

                mecanismo.iterate()

        except Exception as erro:
            self.events.put(("falha", str(erro)))

        finally:
            if mecanismo is not None and loop_iniciado:
                try:
                    mecanismo.endLoop()
                except Exception as erro:
                    self.events.put(
                        ("falha", f"Não foi possível encerrar o mecanismo: {erro}")
                    )

            self.events.put(("encerrado", None))
