# Offline bridge only: JSON input/output, no router API or config writes.
require 'json'
require 'digest'
require 'yaml'
begin
  abort 'official-source-hash-mismatch' unless ARGV.size == 1 &&
    Digest::SHA256.file(ARGV[0]).hexdigest == '1249abf411e1df9e8fe542fb3584f34a27e6e3a587942e5d9f759a32b1bd8261'
  require File.expand_path(ARGV[0])
  input = JSON.parse(STDIN.read)
  puts JSON.generate(YAML.overwrite(input.fetch('baseline'), input.fetch('patch')))
rescue StandardError
  warn 'official-merge-failed'
  exit 1
end
