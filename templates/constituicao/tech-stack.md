# Stack técnica

> Modelo. Descreve o que **está** instalado e em uso, não o que se gostaria de usar. Cada seção
> traz um exemplo de uma linha.

## Visão geral

A forma do sistema em uma frase: onde roda, o que renderiza, quantos processos.

> Ex.: Uma API em Python e um banco PostgreSQL, em dois contêineres; o front é servido pela API.

## Núcleo

| Camada | Escolha | Versão fixa | Por quê |
|---|---|---|---|
| Linguagem | Python | 3.12 | a equipe já domina |

## Dados

O banco, a estratégia de migração, o que é dado sensível.

> Ex.: PostgreSQL 16, migrações com Alembic; telefone e nome do paciente são sensíveis e não vão a
> log.

## Testes e qualidade

A ferramenta de cada verificação e o porquê. O **comando literal** mora no `AGENTS.md`, seção
"Comandos reais", e só lá: duas cópias do mesmo comando desencontram.

> Ex.: pytest (unitários e integração) e ruff (lint); os comandos em `AGENTS.md`, "Comandos reais".

## Execução

Subir local, build, deploy, onde ficam os segredos. Os comandos, no `AGENTS.md`.

> Ex.: dois contêineres pelo Docker Compose; segredos no `.env`, fora do Git, com o modelo em
> `.env.example`.

## Convenções

A estrutura de pastas, os nomes, o tratamento de erro, o padrão de commit, com um arquivo do
repositório como exemplo canônico.

> Ex.: Uma pasta por domínio em `src/`; o padrão está em `src/agenda/`.

## Requisitos não-funcionais

Desempenho, compatibilidade, acessibilidade, conformidade.

> Ex.: A busca de horários responde em menos de 300 ms com 10 mil consultas no banco.

## O que não usamos

A tecnologia descartada, com o motivo.

> Ex.: ORM assíncrono: o ganho não paga a complexidade no volume de hoje.
