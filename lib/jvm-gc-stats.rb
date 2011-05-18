require 'jvm-gc-stats/tailer'
require 'jvm-gc-stats/parser'

module JvmGcStats

  # If you wish to change the report method, simply open this class, make your changes, and
  # instantiate it. You may also extend it if that's your jam.
  #
  class StatsCollector
    def initialize(filename, report, prefix, tail, debug)
      @filename = filename
      @report = report
      @prefix = prefix
      @debug = debug
      @tail = tail
    end

    def run
      Tailer.new(@filename, @tail).tail do |line|
        p Parser.parse(line)
      end
    end
  end

end
