---
# Infos
title: 'Lab Orchestrator Final Report'
author:
- Marco Schlicht
date: \today
tags: [lab, orchestrator, kubernetes, docker, finalreport, final, report, abschlussbericht, virtual, machines]
lang: en-EN
abstract: |
  The Lab Orchestrator is a tool that helps you to orchestrate labs. A Lab consists of multiple VMs which can be accessed by students for learning purposes. The Orchestrator allows to define such Labs by uploading VM images and instructions for the learning task. Students can then spin up the lab setup and access the VMs via NoVNC to accomplish the given task.
  This is the final report on the project which evaluates the workplan and the project results.

numbersections: false

# Format
fontsize: 10pt
linestretch: 1
fontfamily: "libertine"
mainfont:
sansfont:
monofont: "Fira Mono Regular"
mathfont:
geometry: a4paper, left=20mm, right=20mm, top=20mm, bottom=20mm

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
    - '\usepackage[dvipsnames]{xcolor}'


...
