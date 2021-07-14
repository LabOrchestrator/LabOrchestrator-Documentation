---
# Infos
title: 'Lab Orchestrator'
author:
- Marco Schlicht
- Mohamed El Jemai
date: \today
tags: [markdown, tools]
abstract: |
  This document is the project documentation and is intended, among other things, to describe and explain all aspects, such as tools and required knowledge, that are necessary to successfully complete the project.

  The first chapter explains the motivation of the project and the goals we want to achive. There is also a division of the project into different project phases. In the second chapter the basics needed to understand this project are explained. There are different tools that are described and the key concepts of Kubernetes are explained. After that there are evaluations of which additional tools are required, for which further explanations are included. This contains a more detailed description of Kubernetes objects and KubeVirt, but also information about noVNC and ttyd, two tools which may be used to connect to the containers and VMs.

  The project documentation accompanies the project and is continuously supplemented and expanded and should always reflect the current status of the project.
lang: en-EN
numbersections: true

# Format
fontsize: 12pt
linestretch: 1
fontfamily: "libertine"
mainfont:
sansfont:
monofont: "Fira Mono Regular"
mathfont:
geometry: a4paper, left=30mm, right=30mm, top=30mm, bottom=30mm

# Bibliography
csl: common/style.csl
bibliography: sources.bib
suppress-bibliography: false
link-citations: true
color-links: true
linkcolor: purple
urlcolor: teal
citecolor: black
endnote: false

# Variables
#project_name: 'Lernmodul Controler'
#project_name: 'Lab Control Plane (LCP)'
project_name: 'Lab Orchestrator'

include-before: |
    \pagenumbering{gobble}
    \maketitle
    \pagebreak
    \tableofcontents
    \pagebreak
    \pagenumbering{arabic}

header-includes:
    - '\AtBeginDocument{\floatplacement{codelisting}{H}}' # this enforces the position of listings
    - '\usepackage{fvextra}' # break lines in listings
    - '\DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,commandchars=\\\{\}}' # break lines in listings
    - '\usepackage[htt]{hyphenat}'


...
