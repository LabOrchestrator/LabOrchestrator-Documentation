---
# Infos
title: 'Lab Orchestrator Zwischenbericht'
author:
- Marco Schlicht
date: \today
tags: [lab, orchestrator, kubernetes, docker, zwischenbericht, virtual, machines]
lang: en-EN
numbersections: false

# Format
fontsize: 10pt
linestretch: 1
fontfamily: "libertine"
mainfont:
sansfont:
monofont: "Fira Mono Regular"
mathfont:
geometry: a4paper, left=10mm, right=10mm, top=10mm, bottom=10mm

# Bibliography
csl: common/style.csl
suppress-bibliography: true
link-citations: true
color-links: true
linkcolor: purple
urlcolor: teal
citecolor: black
endnote: false

# Variables
project_name: 'Lab Orchestrator'

include-before: |
    \pagenumbering{gobble}
    \maketitle
    \pagebreak
    \pagenumbering{arabic}

header-includes:
    - '\AtBeginDocument{\floatplacement{codelisting}{H}}' # this enforces the position of listings
    - '\usepackage{fvextra}' # break lines in listings
    - '\DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,commandchars=\\\{\}}' # break lines in listings
    - '\usepackage[htt]{hyphenat}'


...
