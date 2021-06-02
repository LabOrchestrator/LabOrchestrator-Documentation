doc_files=common/config.md common/pre.md \
		  tools/tools.md \
		  installation/installation.md \
		  common/post.md

pandoc_filters=--filter pandoc-citeproc --lua-filter=common/meta-vars.lua
pandoc_params=--pdf-engine=lualatex ${pandoc_filters}

docs:
	pandoc ${doc_files} ${pandoc_params} -o documentation.pdf
