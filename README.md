# llm-assistive-reading-tool

Ferramenta de leitura assistiva utilizando LLMs.

## Executar

Na raiz do repositório, execute:

```powershell
python main\index.py
```

O LM Studio deve estar iniciado com um modelo carregado e o servidor local
disponível em `http://localhost:1234/v1`.

## Organização do código

- `main\index.py`: ponto de entrada, interface e integração dos componentes.
- `main\app_config.py`: modos de adaptação e configurações gerais.
- `main\text_processing.py`: validação do texto e integração com o LM Studio.
- `main\markdown_renderer.py`: interpretação e formatação do Markdown.
- `main\speech_service.py`: leitura em voz alta e ciclo do pyttsx3.
- `main\processing_overlay.py`: sobreposição visual de processamento.
