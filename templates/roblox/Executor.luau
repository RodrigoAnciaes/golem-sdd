-- Golem SDD · © 2026 Rodrigo Anciães Patelli · licença MIT (.claude/LICENSE) · https://github.com/RodrigoAnciaes/golem-sdd
--[[
	O executor mínimo de testes do Golem, para um place sem Rojo.

	Onde fica: um ModuleScript `Executor` dentro de uma pasta `GolemTestes` em `ServerStorage`
	(o caminho `game.ServerStorage.GolemTestes.Executor`).

	Um teste é uma função num ModuleScript cujo nome termina em `_spec`. O módulo devolve uma
	tabela `{ ["nome do teste"] = função }`. O teste passa se a função termina sem erro e falha se
	ela dá erro (use `assert` ou `error`). Um teste cujo nome começa com `pular: ` não roda e conta
	como pulado.

	Como rodar: em modo de jogo, porque em modo de edição o `require` devolve a versão guardada
	de um módulo, mesmo depois de editado. Com o jogo ligado, no servidor:

		require(game.ServerStorage.GolemTestes.Executor).rodar()

	No fim, ele imprime a linha de resumo `N passed, N failed, N skipped`, o formato do TestEZ.
	Sem nenhum teste, ele imprime também "nenhum teste encontrado": zero testes não é verde.
]]

local Executor = {}

-- Os serviços em que o executor procura os testes. Um `_spec` posto em
-- `StarterPlayer.StarterCharacterScripts` é copiado para o personagem, no `Workspace`, e roda
-- duas vezes com o jogo ligado: deixe os testes fora dele.
local SERVICOS = {
	"ServerScriptService",
	"ServerStorage",
	"ReplicatedStorage",
	"ReplicatedFirst",
	"StarterPlayer",
	"StarterGui",
	"Workspace",
}

local SUFIXO = "_spec"
local PULAR = "pular: "

local function ehTeste(instancia)
	return instancia:IsA("ModuleScript") and instancia.Name:sub(-#SUFIXO) == SUFIXO
end

local function acharTestes()
	local achados = {}
	for _, nome in ipairs(SERVICOS) do
		local ok, servico = pcall(function()
			return game:GetService(nome)
		end)
		if ok and servico then
			for _, instancia in ipairs(servico:GetDescendants()) do
				if ehTeste(instancia) then
					table.insert(achados, instancia)
				end
			end
		end
	end
	table.sort(achados, function(a, b)
		return a:GetFullName() < b:GetFullName()
	end)
	return achados
end

function Executor.rodar()
	local passou, falhou, pulou = 0, 0, 0
	local modulos = acharTestes()

	for _, modulo in ipairs(modulos) do
		local nomeDoModulo = modulo:GetFullName()
		local ok, testes = pcall(require, modulo)
		if not ok then
			falhou += 1
			print(("FALHOU %s: o módulo não carregou: %s"):format(nomeDoModulo, tostring(testes)))
		elseif type(testes) ~= "table" then
			falhou += 1
			print(("FALHOU %s: o módulo devolveu %s, e não uma tabela de testes"):format(
				nomeDoModulo,
				type(testes)
			))
		else
			local itens = {}
			for chave in pairs(testes) do
				table.insert(itens, { chave = chave, nome = tostring(chave) })
			end
			table.sort(itens, function(a, b)
				return a.nome < b.nome
			end)
			for _, item in ipairs(itens) do
				local nome = item.nome
				local teste = testes[item.chave]
				if nome:sub(1, #PULAR) == PULAR then
					pulou += 1
				elseif type(teste) ~= "function" then
					falhou += 1
					print(("FALHOU %s > %s: não é uma função"):format(nomeDoModulo, nome))
				else
					local certo, erro = pcall(teste)
					if certo then
						passou += 1
					else
						falhou += 1
						print(("FALHOU %s > %s: %s"):format(nomeDoModulo, nome, tostring(erro)))
					end
				end
			end
		end
	end

	if passou + falhou + pulou == 0 then
		print("nenhum teste encontrado")
	end
	local resumo = ("%d passed, %d failed, %d skipped"):format(passou, falhou, pulou)
	print(resumo)
	return resumo
end

return Executor
