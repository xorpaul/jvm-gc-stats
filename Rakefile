require 'bundler'
Bundler::GemHelper.install_tasks

require 'rake/testtask'

task :default => [:test]

desc "Run basic tests"
Rake::TestTask.new("test") { |t|
  t.pattern = 'test/*_test.rb'
  t.verbose = true
  t.warning = true
}