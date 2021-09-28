doc_files=common/config.md \
		  finalreport.md

pandoc_filters=--lua-filter=common/meta-vars.lua --filter pandoc-include-code --filter pandoc-crossref --citeproc

docs:
	pandoc ${doc_files} --pdf-engine=latexmk --pdf-engine-opt=-outdir=.latex_cache --pdf-engine-opt=-lualatex ${pandoc_filters} -o finalreport.pdf
