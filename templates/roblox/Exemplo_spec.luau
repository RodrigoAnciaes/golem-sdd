--[[
	Um exemplo de teste para o executor do Golem (templates/roblox/Executor.luau).

	No place, ele é um ModuleScript chamado `Exemplo_spec`. O sufixo `_spec` é o que faz o executor
	achá-lo. Cada chave é o nome de um teste, e cada valor é a função que o roda.
]]

return {
	["soma de dois números"] = function()
		assert(1 + 1 == 2, "1 + 1 deveria dar 2")
	end,

	-- Começa com "pular: ", então não roda e conta como pulado.
	["pular: um teste deixado para depois"] = function()
		error("este teste não deveria rodar")
	end,
}
