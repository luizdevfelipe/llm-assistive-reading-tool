LIMITE_TEXTO = 10000

MODOS = {
    "Simplificação": (
        "Reescreva o conteúdo usando linguagem simples e cotidiana. "
        "Prefira frases curtas, com uma ideia principal por frase. "
        "Substitua palavras difíceis por termos mais comuns sempre que "
        "isso não alterar o significado. Explique termos técnicos apenas "
        "quando necessário. Preserve as informações relevantes do original. "
        "Não transforme o texto em um resumo: mantenha seu conteúdo essencial."
    ),

    "Resumo": (
        "Produza um resumo do conteúdo, reduzindo seu tamanho e eliminando "
        "repetições, exemplos secundários e detalhes pouco relevantes. "
        "Preserve as ideias centrais, os argumentos, as conclusões e os dados "
        "importantes, como nomes, datas e números. O resultado deve ser "
        "consideravelmente mais curto que o original, sem perder seu sentido."
    ),

    "Organização em tópicos": (
        "Reorganize o conteúdo em tópicos e subtópicos. Agrupe informações "
        "relacionadas e utilize títulos curtos quando isso facilitar a leitura. "
        "Apresente os tópicos com marcadores. Preserve as informações "
        "relevantes do texto original, sem criar informações novas."
    ),

    "Organização em etapas": (
        "Reorganize o conteúdo em etapas numeradas, com uma ordem lógica e "
        "fácil de acompanhar. Utilize frases claras e objetivas. Preserve a "
        "sequência indicada no texto original. Caso não exista uma sequência "
        "explícita, organize as informações de maneira lógica, sem inventar "
        "ações ou procedimentos que não estejam presentes no conteúdo."
    )
}
