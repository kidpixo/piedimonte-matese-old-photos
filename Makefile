.PHONY: help serve serve_old build up down logs clean
.DEFAULT_GOAL := help

process_photos : ## Process raw_data photos with script/process_photos.sh
	python ./scripts/process_research.py

build-site: ## Build the Jekyll site (generates _site/ folder)
	podman run --rm --name jekyll-lanyon-build -v "$$(pwd):/usr/src/app" -w /usr/src/app jekyll-lanyon:latest bundle exec jekyll build --unpublished --future

rsync-site: build-site ## Build and rsync the site to remote server
	rsync -aP --info=,progress2 --update _site brapi-bamberga:/srv/container/cotonificio/data/

build: ## Build the Docker image
	podman-compose build

up: ## Start Jekyll server in Docker (detached)
	podman-compose up

serve: up ## Alias for 'up' - Start Jekyll server in Docker

down: ## Stop and remove Docker containers
	podman-compose down

logs: ## View Docker container logs (follow mode)
	podman-compose logs -f jekyll

clean: ## Stop containers and remove volumes
	podman-compose down -v

rebuild: ## Rebuild Docker image from scratch
	podman-compose build --no-cache

#################################################################################
# Self Documenting Commands                                                     #

help: ## Show help. Only lines with ": ##" will show up!
	@awk -F':[[:space:]]*.*## ' '/^[a-zA-Z0-9_.-]+ *:.*## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
