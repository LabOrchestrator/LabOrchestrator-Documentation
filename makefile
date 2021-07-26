doc_files=common/config.md \
		  introduction/introduction.md \
		  basics/basics.md \
		  installation/installation.md \
		  poc/poc.md \
		  prototype/prototype.md \
		  common/post.md

pandoc_filters=--filter pandoc-crossref --filter pandoc-citeproc --lua-filter=common/meta-vars.lua --filter pandoc-include-code
pandoc_params=--pdf-engine=lualatex ${pandoc_filters}

docs:
	pandoc ${doc_files} ${pandoc_params} -o documentation.pdf
