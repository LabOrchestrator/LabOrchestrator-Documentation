doc_files=common/config.md \
		  introduction/introduction.md \
		  basics/basics.md \
		  installation/installation.md \
		  poc/poc.md \
		  prototype/prototype.md \
		  common/post.md

pandoc_filters=--filter pandoc-crossref --filter pandoc-citeproc --lua-filter=common/meta-vars.lua --filter pandoc-include-code

default: fast

docs:
	pandoc ${doc_files} --pdf-engine=lualatex ${pandoc_filters} -o documentation.pdf

fast:
	pandoc ${doc_files} ${pandoc_filters} -o documentation.tex --standalone
	latexmk -lualatex -pdf documentation.tex
