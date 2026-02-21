.PHONY: help serve
.DEFAULT_GOAL := help

serve: ## Serve the Jekyll site locally using a podman container
	podman run --rm -p 4000:4000 --name jekyll-lanyon -v "$$(pwd):/srv/jekyll" -it -w /srv/jekyll localhost/gh-pages:alpine jekyll serve --unpublished --future --host 0.0.0.0 --force_polling

#################################################################################
# Self Documenting Commands                                                     #

help: ## Show help. Only lines with ": ##" will show up!
	@awk -F':[[:space:]]*.*## ' '/^[a-zA-Z0-9_.-]+ *:.*## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)