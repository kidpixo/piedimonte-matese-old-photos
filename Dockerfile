# from https://jogendra.dev/dockerize-your-jekyll-site-for-local-development
# Use a slim Ruby image as the base
# Ruby 3.2 - compatible with github-pages gem (Jekyll 3.9.x)
FROM docker.io/ruby:3.2-slim

# Set environment variables for UTF-8 encoding and non-interactive package installation
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive

# Install essential build tools and dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /usr/src/app

# Install Bundler to match Gemfile.lock
ENV BUNDLER_VERSION=2.3.26
RUN gem install bundler:$BUNDLER_VERSION

# Copy only dependency files for better layer caching
COPY Gemfile Gemfile.lock* ./

# Install project dependencies (image layer warm-up)
RUN bundle install

# Add entrypoint to ensure bundle install runs for mounted volumes
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Copy the rest of the source code (done at runtime via volume mount for dev)
# COPY . .

# Expose port 4000
EXPOSE 4000

# Start the Jekyll development server with live reloading
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["bundle", "exec", "jekyll", "serve", "--host", "0.0.0.0", "--livereload", "--force_polling"]
