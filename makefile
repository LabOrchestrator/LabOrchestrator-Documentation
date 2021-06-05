doc_files=common/config.md common/pre.md \
		  introduction/introduction.md \
		  basics/basics.md \
		  installation/installation.md \
		  prototype/prototype.md \
		  common/post.md

pandoc_filters=--filter pandoc-citeproc --lua-filter=common/meta-vars.lua --filter pandoc-include-code
pandoc_params=--pdf-engine=lualatex ${pandoc_filters}

docs:
	pandoc ${doc_files} ${pandoc_params} -o documentation.pdf
