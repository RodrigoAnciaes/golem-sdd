# Referência: escrever `validation.md`

A parte que mais se faz mal. Este arquivo é o contrato de merge: se tudo aqui passa, a fase
acabou; se não, ela continua.

## Regra de ouro

**Escreva antes de implementar.** Critério redigido depois vira descrição do que o código já faz,
e não valida nada.

## Anatomia

| Bloco | Conteúdo |
|---|---|
| Verificações automatizadas | comando literal + resultado esperado, um bloco por comando |
| Verificações manuais | passo a passo que uma pessoa executa: abrir X, fazer Y, ver Z |
| Casos de borda | entrada vazia, valor limite, falha de dependência externa |
| Requisitos da constituição | nenhuma dependência fora da stack, convenções seguidas, RNF da fase |
| Registro | changelog, roadmap marcado, perguntas em aberto resolvidas |
| Não exigido nesta fase | o que ficou de fora de propósito |

## Traduzindo vago em verificável

| Vago | Verificável |
|---|---|
| "os testes devem passar" | `npm test`: 14 testes, 0 falhas, incluindo os 3 novos de validação de CPF |
| "a página deve funcionar" | `curl -s localhost:3000/agentes` retorna 200 e contém `<h1>Agentes</h1>` |
| "tratar erros" | campo vazio → HTTP 400 com `{"erro":"campo obrigatório"}` e nada gravado no banco |
| "deve estar rápido" | resposta abaixo de 300 ms com 1000 registros semeados |
| "interface consistente" | usa o componente `Layout`; textos em pt-BR; termos conforme glossário |

## Falhas comuns

- **Critério que só o autor sabe conferir.** Escreva para quem chega depois.
- **Nenhum caso de borda.** Toda fase tem pelo menos entrada inválida e dependência indisponível.
- **"Não exigido" vazio.** Sem essa seção, a revisão cobra o que nunca foi combinado.
- **Verificação manual sem passo a passo.** "Testar no navegador" não é instrução.
- **Marcar item como pronto sem evidência.** A saída real do comando é a prova; opinião não é.
- **Teste que passaria com o defeito.** Para correção de defeito, peça o teste que falha na `main`
  e passa na branch.
