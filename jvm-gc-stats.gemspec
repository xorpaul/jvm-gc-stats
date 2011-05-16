# -*- encoding: utf-8 -*-
$:.push File.expand_path("../lib", __FILE__)
require "jvm-gc-stats/version"

Gem::Specification.new do |s|
  s.name        = "jvm-gc-stats"
  s.version     = JvmGcStats::VERSION
  s.platform    = Gem::Platform::RUBY
  s.authors     = ["John Kalucki", "Steve Jensen", "Jonathan Reichold", "Ryan King"]
  s.email       = ["ryan@twitter.com"]
  s.homepage    = ""
  s.summary     = %q{Parse and record gc logs generated by the JVM}
  s.description = %q{TODO}

  s.rubyforge_project = "jvm-gc-stats"

  s.files         = `git ls-files`.split("\n")
  s.test_files    = `git ls-files -- {test,spec,features}/*`.split("\n")
  s.executables   = `git ls-files -- bin/*`.split("\n").map{ |f| File.basename(f) }
  s.require_paths = ["lib"]
end