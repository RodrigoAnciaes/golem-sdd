---
id: o-studio-recusa-salvar-a-copia-com-a-sessao-antiga-aberta
data: 2026-11-21
area: processo
tipo: premissa-falsa
custo: "uma rodada do passo 10 da verificação manual 1 da fase 2, e a ordem do guia escrita ao contrário"
gatilho: "voltar um place do Roblox a uma versão anterior pela cópia local do histórico, seguindo o docs/guia-roblox.md da fase 2"
refs:
  - "docs/guia-roblox.md (seção 4, Voltar atrás)"
  - "specs/2026-11-13-fase-2-roblox/validation.md (verificação manual 1, passo 10)"
gatilhos:
  - '\bguia-roblox\.md$'
---

**O que se achava:** que, para voltar a uma versão, se abre a cópia local da versão, se salva a
cópia sobre o mesmo place (Arquivo ⟩ Salvar na Roblox como) e só depois se fecha a sessão antiga
sem salvar, como o guia mandava e o passo 10 da verificação repetia.

**O que é:** com a janela antiga do place aberta, o Studio recusa o salvamento da cópia. Ao
escolher Substituir, ele avisou que o local "possui uma sessão de Criação em equipe com outros
usuários no momento" e listou o próprio dono da conta. Depois, mostrou "Falha no salvamento". Com
a janela antiga fechada (ela fechou sem perguntar se devia salvar; a suposição é que seja pela
Criação em equipe), o mesmo Substituir deu "Salvo com sucesso!". O place reaberto pelo Roblox ficou
só com o que havia na versão (2026-11-21, Studio 0.748.0, lido na tela de abertura). O print do
aviso está em `fase-2-g6-pronto/passo10-recusa-com-sessao-aberta.jpg`, nas notas da conversa da
fase 2. O "Falha no salvamento" e o "Salvo com sucesso!" foram vistos nas capturas de tela da
sessão, sem arquivo guardado; a lista do place depois da volta está em `passo10-depois.txt`.

**Como perceber da próxima vez:**
1. "Falha no salvamento" no Salvar na Roblox como, logo depois de um aviso de sessão de Criação em
   equipe que lista o seu próprio usuário: há outra janela do Studio com o mesmo place aberta.
   Feche-a sem salvar e salve de novo.
2. Um passo a passo de interface escrito antes de ser seguido de ponta a ponta é hipótese: confira
   a ordem rodando-o uma vez, antes de pô-lo num guia.
