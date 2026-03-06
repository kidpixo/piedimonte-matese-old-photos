# _plugins/cors.rb
require 'webrick'

Jekyll::Hooks.register :serving, :after_init do |server, _|
  server.mount_proc '/' do |req, res|
    res['Access-Control-Allow-Origin'] = '*'
    res['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    res['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept'
  end
end
