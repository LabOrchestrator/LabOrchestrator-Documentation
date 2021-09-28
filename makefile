doc_files=common/config.md \
		  introduction/introduction.md \
		  basics/basics.md \
		  installation/installation.md \
		  poc/poc.md \
		  prototype/prototype.md \
		  other/other.md \
		  common/post.md

pandoc_filters=--lua-filter=common/meta-vars.lua --filter pandoc-include-code --filter pandoc-crossref --citeproc

docs:
	pandoc ${doc_files} --pdf-engine=latexmk --pdf-engine-opt=-outdir=.latex_cache --pdf-engine-opt=-lualatex ${pandoc_filters} -o documentation.pdf
