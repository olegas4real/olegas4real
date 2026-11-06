#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reescreve o painel neofetch do README entre os marcadores.

O retrato é fixo (assets/retrato.txt). As linhas de texto são fixas e moram
aqui embaixo. Só os números vêm da API do GitHub, numa única consulta.

Rode à mão com um token em GH_PANEL_TOKEN, ou deixe o workflow semanal rodar.
Nunca edite o bloco direto no README: o script sobrescreve.
"""

import calendar
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

LOGIN = "olegas4real"
NASCIMENTO = date(1999, 1, 24)

RAIZ = Path(__file__).resolve().parent.parent
RETRATO = RAIZ / "assets" / "retrato.txt"
README = RAIZ / "README.md"

INICIO = "<!-- painel:inicio -->"
FIM = "<!-- painel:fim -->"

LARGURA = 52   # largura da coluna de infos
GUTTER = 4     # espaço entre o retrato e o painel


def morrer(msg):
    print("painel.py: %s" % msg, file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------- API

CONSULTA = """
query($de: DateTime!, $ate: DateTime!) {
  viewer {
    login
    followers { totalCount }
    following { totalCount }
    repositories(first: 100, ownerAffiliations: [OWNER]) {
      totalCount
      nodes { isPrivate stargazerCount }
    }
    contributionsCollection(from: $de, to: $ate) {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
    }
  }
}
"""


def consultar():
    token = os.environ.get("GH_PANEL_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        morrer("falta GH_PANEL_TOKEN (PAT clássico, escopo read:user e só ele).")

    ate = datetime.now(timezone.utc)
    de = ate - timedelta(days=365)
    corpo = json.dumps({
        "query": CONSULTA,
        "variables": {
            "de": de.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "ate": ate.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    }).encode()

    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=corpo,
        headers={
            "Authorization": "bearer %s" % token,
            "Content-Type": "application/json",
            "User-Agent": "painel-olegas4real",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            dados = json.load(r)
    except urllib.error.HTTPError as e:
        morrer("a API respondeu %s: %s" % (e.code, e.read().decode()[:300]))
    except Exception as e:  # rede, DNS, timeout
        morrer("não consegui falar com a API: %s" % e)

    if "errors" in dados:
        morrer("a API devolveu erro: %s" % json.dumps(dados["errors"])[:300])

    v = dados["data"]["viewer"]

    # O GITHUB_TOKEN padrão do Actions autentica como o bot: 'viewer' viraria
    # a conta errada e os números sairiam zerados sem ninguém perceber.
    if v["login"] != LOGIN:
        morrer("o token é de '%s', não de '%s'. Use um PAT seu em GH_PANEL_TOKEN."
               % (v["login"], LOGIN))

    repos = v["repositories"]
    if repos["totalCount"] > len(repos["nodes"]):
        morrer("passou de 100 repositórios: o script precisa paginar antes de contar.")

    return v


# ---------------------------------------------------------------- texto

def idade(nasc, hoje):
    anos = hoje.year - nasc.year
    meses = hoje.month - nasc.month
    dias = hoje.day - nasc.day
    if dias < 0:
        meses -= 1
        mes = hoje.month - 1 or 12
        ano = hoje.year if hoje.month > 1 else hoje.year - 1
        dias += calendar.monthrange(ano, mes)[1]
    if meses < 0:
        anos -= 1
        meses += 12
    return anos, meses, dias


def plural(n, palavra):
    return "%d %s%s" % (n, palavra, "" if n == 1 else "s")


def linha(rotulo, valor):
    rotulo += ":"
    pontos = max(LARGURA - len(rotulo) - len(valor) - 2, 1)
    return "%s %s %s" % (rotulo, "." * pontos, valor)


def titulo(texto):
    return texto + " " + "-" * (LARGURA - len(texto) - 1)


def montar(v):
    anos, meses, dias = idade(NASCIMENTO, date.today())
    c = v["contributionsCollection"]
    publicos = c["totalCommitContributions"]
    privados = c["restrictedContributionsCount"]
    repos = v["repositories"]
    abertos = sum(1 for r in repos["nodes"] if not r["isPrivate"])
    estrelas = sum(r["stargazerCount"] for r in repos["nodes"])

    return [
        "gabriel@olegario",
        "-" * LARGURA,
        linha("OS", "macOS 26.6.2"),
        linha("Uptime", "%s, %s, %s" % (plural(anos, "year"),
                                        plural(meses, "month"),
                                        plural(dias, "day"))),
        linha("Host", "Smart Social (iGaming media hub)"),
        linha("Kernel", "Head of Strategy & Data"),
        linha("Shell", "zsh"),
        linha("Editor", "VS Code, Claude Code, Obsidian"),
        "",
        titulo("- Languages"),
        linha("Programming", "TypeScript, Python, JS, Shell"),
        linha("Markup", "HTML, CSS, SQL, Markdown, YAML"),
        linha("Spoken", "Portuguese (native), English"),
        "",
        titulo("- Building"),
        linha("LabEpi", "epidemiology education"),
        linha("Altman", "applied statistics for research"),
        "",
        titulo("- Contact"),
        linha("Email", "gabriel.oligar@gmail.com"),
        linha("Instagram", "@olegas4real"),
        linha("Web", "labepi.com"),
        "",
        titulo("- GitHub Stats"),
        linha("Repos", "%d (%d public)" % (repos["totalCount"], abertos)),
        linha("Stars", "%d earned" % estrelas),
        linha("Commits", "{:,} last 12mo ({:,} private)".format(publicos + privados, privados)),
        linha("PRs", "{:,} last 12mo".format(c["totalPullRequestContributions"])),
        linha("Social", "%d followers | %d following" % (v["followers"]["totalCount"],
                                                         v["following"]["totalCount"])),
    ]


def colar(arte, info):
    arte = arte.rstrip("\n").split("\n")
    largura = max(len(l) for l in arte)
    alt = max(len(arte), len(info))
    arte += [""] * (alt - len(arte))
    info += [""] * (alt - len(info))
    return [(a.ljust(largura) + " " * GUTTER + b).rstrip()
            for a, b in zip(arte, info)]


# ---------------------------------------------------------------- README

def main():
    if not RETRATO.exists():
        morrer("não achei %s" % RETRATO)

    bloco = colar(RETRATO.read_text(encoding="utf-8"), montar(consultar()))
    novo = "%s\n```\n%s\n```\n%s" % (INICIO, "\n".join(bloco), FIM)

    texto = README.read_text(encoding="utf-8")
    i, f = texto.find(INICIO), texto.find(FIM)
    if i < 0 or f < 0 or f < i:
        morrer("não achei os marcadores %s / %s no README." % (INICIO, FIM))

    saida = texto[:i] + novo + texto[f + len(FIM):]
    if saida == texto:
        print("painel sem mudança")
        return
    README.write_text(saida, encoding="utf-8")
    print("painel atualizado")


if __name__ == "__main__":
    main()
