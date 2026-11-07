# <Nome da fase> — Requisitos

> Modelo. Mora em `specs/AAAA-MM-DD-nome/requirements.md`, escrito pela skill `spec-de-fase`
> depois da entrevista. Cada seção traz um exemplo de uma linha.

## Objetivo

O que passa a existir, em uma frase, copiado do roadmap.

> Ex.: O paciente vê os horários livres de um médico numa data.

## Escopo

Os requisitos numerados, cada um verificável.

> Ex.: R1. `GET /horarios?medico=&data=` devolve os horários livres, em ordem, de 30 em 30 minutos.

## Fora de escopo

O que alguém vai supor que entra e não entra, com o porquê.

> Ex.: Marcar a consulta: é a fase seguinte; aqui só se lê.

## Decisões

Cada decisão com a justificativa e a alternativa descartada. Decisão do usuário vai com as
palavras dele e a data.

> Ex.: Horários calculados na hora, sem tabela própria; descartada a tabela pré-gerada (mais uma
> peça para manter em dia).

## Contexto

Os fatos que sustentam a spec, cada um com a fonte (`arquivo:linha` ou a saída do comando).

> Ex.: A agenda do médico já existe em `src/agenda/modelos.py:12`, com início e fim do expediente.

## Padrões a seguir

O arquivo do repositório cujo padrão a implementação copia.

> Ex.: As rotas seguem `src/pacientes/rotas.py`: validação na entrada, erro com `{"erro": "..."}`.

## Notas do usuário

O que o usuário disse na entrevista e que orienta a fase, com as palavras dele e a data.

> Ex.: "O médico precisa ver o encaixe destacado na lista" (o usuário, AAAA-MM-DD).

## Teto de gasto (se houver)

Só quando a fase gasta dinheiro (API paga, serviço por uso): o teto, em valor, aprovado junto com a
spec. Passar dele é decisão do usuário, antes da chamada.

> Ex.: Até US$ 5 em chamadas à API de mensagens, para os testes de envio do lembrete.

## Perguntas em aberto

O que ainda não se sabe; cada uma se responde até o fim da fase ou vai para o roadmap.

> Ex.: Feriado bloqueia a agenda inteira? (a conferir com o usuário)
