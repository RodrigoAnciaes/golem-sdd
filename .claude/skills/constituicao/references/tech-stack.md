# Referência: `tech-stack.md`

Carregue este arquivo ao escrever ou revisar a stack.

## Regra que governa a página

Esta página é a **fronteira de autonomia do agente**: tudo que está aqui pode ser usado sem
perguntar; tudo que não está exige aprovação humana antes de entrar no gerenciador de pacotes.

## Seções obrigatórias

| Seção | O que precisa estar lá |
|---|---|
| Visão geral | a forma do sistema em uma frase (onde roda, o que renderiza, quantos processos) |
| Núcleo | tabela camada / escolha / **versão fixa** / justificativa |
| Dados | banco, estratégia de migração, o que é dado sensível |
| Testes e qualidade | a ferramenta de cada verificação e o porquê; o **comando literal** mora no `AGENTS.md`, "Comandos reais", e esta seção aponta para lá |
| Execução | subir local, build, deploy, onde ficam segredos (os comandos, também no `AGENTS.md`) |
| Convenções | estrutura de diretórios, nomenclatura, tratamento de erro, padrão de commit |
| Requisitos não-funcionais | desempenho, compatibilidade, acessibilidade, conformidade |
| O que não usamos | tecnologia descartada **com o motivo** |

## O que separa uma stack boa de uma lista de tecnologias

- **Versão fixa, sempre.** "React" não é decisão; `react 18.3.1` é. Faixa (`^`) transforma
  atualização em surpresa no meio de uma fase.
- **Justificativa comparativa.** Diga contra o quê você escolheu: "Hono em vez de Express porque
  TypeScript sem configuração e JSX no servidor".
- **Comando literal, num lugar só.** `npm test` e `pytest -q` são o que a validação de cada fase
  vai executar; se estiver descrito em prosa, ninguém roda. Ele vai para a seção "Comandos reais"
  do `AGENTS.md`, que todo agente lê; duas cópias do mesmo comando desencontram em silêncio.
- **"O que não usamos" evita reincidência.** Sem essa seção, o agente reintroduz o ORM que você
  descartou três fases atrás, com toda a educação do mundo.

## Falhas comuns

| Sintoma | Correção |
|---|---|
| Escolhas sem versão | leia o arquivo de dependências e registre a versão real em uso |
| Stack aspiracional (o que você gostaria de usar) | descreva o que está de fato instalado; o resto é roadmap |
| Sem seção de dados sensíveis | declare o que não pode ser logado, exportado ou mandado para fora |
| Testes citados sem comando | pegue os scripts do `package.json` / `Makefile` / `pyproject.toml` e ponha no `AGENTS.md`, "Comandos reais" |
| Convenções só na cabeça de alguém | aponte um arquivo do repositório como exemplo canônico |

## Perguntas de entrevista

1. O que já está decidido e não se discute mais?
2. O que é proibido aqui, por política, licença, contrato ou trauma?
3. Como se roda, se testa e se sobe isso hoje? Me dá os comandos.
4. Que dado passa por aqui que não pode vazar em log nem ir para serviço de terceiro?
5. O que existe no projeto que você considera dívida e quer registrar como tal?
