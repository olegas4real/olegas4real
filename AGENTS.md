# AGENTS.md

> **Fonte única deste repositório para agentes de código** (Claude Code, Codex, Cursor, Copilot).
> O `CLAUDE.md` só importa este arquivo. Regra nova entra aqui, nunca em dois lugares.

## O que é isto

O README do perfil do Gabriel no GitHub. Repositório com o mesmo nome do usuário, que é o que
o GitHub renderiza em [github.com/olegas4real](https://github.com/olegas4real).

A abertura é um painel estilo `neofetch`: um retrato em ASCII à esquerda e uma coluna de
informações à direita, **na mesma linha física, dentro de um único bloco de código**. Embaixo,
prosa em português sobre os projetos.

## Stack

Python 3 da biblioteca padrão e um workflow do Actions. Sem dependências, sem build, sem testes.

## Comandos

```bash
# regerar o painel à mão (precisa de um PAT seu, não do token do Actions)
GH_PANEL_TOKEN="$(gh auth token)" python3 scripts/painel.py

# conferir que nenhuma linha passou de ~100 colunas
awk '{ if (length($0) > 100) print FILENAME":"NR": "length($0)" colunas" }' README.md
```

## Estrutura

```
README.md                      o perfil; o painel fica entre os marcadores
assets/retrato.txt             o retrato em ASCII, 36 linhas, arquivo fixo
scripts/painel.py              gera o painel e reescreve o bloco
.github/workflows/painel.yml   roda o script toda segunda e commita se mudou
```

## Regras que não se negociam

1. **Não edite o painel direto no README.** O bloco entre `<!-- painel:inicio -->` e
   `<!-- painel:fim -->` é gerado. Qualquer coisa escrita ali é apagada na segunda seguinte.
   Texto fixo muda em `montar()`, dentro do `scripts/painel.py`.
2. **Não apague uma linha do painel na mão.** Retrato e infos dividem a mesma linha física:
   tirar uma linha solta desloca metade do desenho. Mexeu, rode o script.
3. **Número no painel precisa vir de uma chamada de API.** Se não dá para rastrear até uma
   resposta, não entra. Foi por isso que "stars dadas" saiu: a API devolve 36, a aba do perfil
   mostra 32, e nenhuma chamada devolve 32 — o script ficaria revertendo o valor toda semana.
4. **O `GITHUB_TOKEN` padrão do Actions não serve.** Ele autentica como o bot, então o `viewer`
   da consulta GraphQL viria da conta errada e os commits privados sairiam como zero, sem erro
   nenhum. O script confere `viewer.login` e aborta. Use `GH_PANEL_TOKEN`, um PAT clássico com
   escopo `read:user` **e só ele** — o token não precisa escrever nada em lugar nenhum.
5. **O script falha alto, nunca em silêncio.** Erro de rede, erro da API, token errado, mais de
   100 repositórios: tudo sai por `morrer()` com código 1. README desatualizado é melhor que
   README mentindo.
6. **O perfil é público.** Nada de endereço, telefone, documento ou qualquer coisa que o Gabriel
   não tenha publicado por conta própria. Os contatos de hoje (e-mail, Instagram, labepi.com)
   já são públicos no perfil dele.
7. **Projeto encerrado sai do README.** O Gume foi descontinuado em out/2026 e saiu em
   `3736c82`. Não o traga de volta, nem como "trabalho anterior".

## Antes de dizer que terminou

- [ ] `python3 scripts/painel.py` rodou com um PAT de verdade e o diff saiu como esperado
- [ ] nenhuma linha do README passou de ~100 colunas (vira rolagem horizontal no desktop)
- [ ] o retrato continua alinhado: confira umas 5 linhas do meio do bloco, não só as pontas
- [ ] se mexeu no retrato, `assets/retrato.txt` foi atualizado, não o README
- [ ] nenhum valor de token no diff

## Pontas soltas

- **O retrato é o limite de largura.** Saiu do avatar do GitHub, que é muito escuro: 76% dos
  pixels caem entre 16 e 32 de luminância, então cabelo, camiseta e fundo se confundem e não há
  como desenhar o busto. Por isso o enquadramento é fechado no rosto. Com uma foto de fundo
  claro dá para refazer bem melhor.
- **No celular o painel não cabe.** São 97 colunas e num telefone cabem ~43: o visitante vê o
  retrato e precisa arrastar para o lado. Decisão consciente, em 05/11/2026, para manter o
  formato lado a lado no desktop. A alternativa é empilhar retrato e infos.
- **Linhas fixas envelhecem calladas.** Versão do macOS, cargo, editores: nada disso é checado
  por ninguém. Revise `montar()` de vez em quando.

## Onde ler mais

`scripts/painel.py` tem o porquê de cada decisão nos comentários. O retrato foi gerado com
Pillow a partir do avatar, com corte no rosto e ponto de preto em 0.165.
