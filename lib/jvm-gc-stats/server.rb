require 'rack'
require 'jvm-gc-stats/tailer'
require 'jvm-gc-stats/parser'
require 'json'
require 'thread'

module JvmGcStats
  class Server
    def initialize(file_config)
      @data = new_data
      @tailers = {}
      file_config.each_pair do |k,v|
        @tailers[k] = Tailer.new(v)
      end

      @mutex = Mutex.new

      @tailer_threads = []
      @tailers.each_pair do |k,v|
        @tailer_threads << Thread.new do
          v.tail do |line|
            begin
              report(k, JvmGcStats::Parser.parse(line.strip))
            rescue => e
              p e
              puts e.backtrace.join("\n")
            end
          end
        end
      end
    end

    def new_data
      Hash.new {|h1, k1| h1[k1] = Hash.new {|h2, k2| h2[k2] = Hash.new {|h3, k3| h3[k3] = 0}}}
    end

    def call(env)
      @mutex.synchronize do
        json = JSON.dump(@data)
        if Rack::Request.new(env).params["reset"] == "1"
          @data = new_data
        end
        [200, {"Content-Type" => "text/json"}, [json]]
      end
    end

    def report(service, datum)
      # synchronize here
      # assert we know about data[:type]
      @mutex.synchronize do 
        if ['par_new'].include?(type = underscore(datum[:type]))
          [:real_time, :user_time, :sys_time].each do |t|
            @data[service][type][t] += datum[t]
          end

          @data[service][type][:newgen_kb_colllected] += datum[:newgen_kb_before] - datum[:newgen_kb_after]
          @data[service][type][:total_kb_colllected]  += datum[:total_kb_before] - datum[:total_kb_after]
          @data[service][type][:count] += 1
        elsif datum[:type] == "promotion failure"
          type = "promotion_failure"
          [:real_time, :user_time, :sys_time].each do |t|
            @data[service][type][t] += datum[t]
          end

          @data[service][type][:newgen_kb_colllected]  += datum[:newgen_kb_before]  - datum[:newgen_kb_after]
          @data[service][type][:oldgen_kb_colllected]  += datum[:oldgen_kb_before]  - datum[:oldgen_kb_after]
          @data[service][type][:permgen_kb_colllected] += datum[:permgen_kb_before] - datum[:permgen_kb_after]
          @data[service][type][:total_kb_colllected]   += datum[:total_kb_before]   - datum[:total_kb_after]
          @data[service][type][:count] += 1
        elsif %w[CMS-initial-mark CMS-concurrent-mark CMS-concurrent-abortable-preclean
                  CMS-remark CMS-concurrent-sweep CMS-concurrent-reset].include?(datum[:type])
          type = datum[:type].gsub('CMS', 'cms').gsub('-', '_')
          [:real_time, :user_time, :sys_time].each do |t|
            @data[service][type][t] += datum[t]
          end
        elsif %w[ CMS-concurrent-abortable-preclean-start CMS-concurrent-sweep-start
                  CMS-concurrent-reset-start CMS-concurrent-mark-start
                  CMS-concurrent-preclean-start CMS-concurrent-preclean].include?(datum[:type])

          # "CMS-initial-mark", :real_time=>0.01, :user_time=>0.01, :sys_time=>0.0, :timestamp=>"2011-05-26T17:25:21.133-0700"}
          # "CMS-concurrent-mark", :real_time=>0.16, :user_time=>0.61, :sys_time=>0.09, :timestamp=>"2011-05-26T17:25:21.302-0700"}
          # "CMS-concurrent-abortable-preclean", :real_time=>0.72, :user_time=>1.39, :sys_time=>0.55, :timestamp=>"2011-05-26T17:25:22.025-0700"}
          # "CMS-remark", :real_time=>0.05, :user_time=>0.24, :sys_time=>0.01, :timestamp=>"2011-05-26T17:25:22.027-0700"}
          # "CMS-concurrent-sweep", :real_time=>2.47, :user_time=>7.26, :sys_time=>1.63, :timestamp=>"2011-05-26T17:25:24.544-0700"}
          # "CMS-concurrent-reset", :real_time=>0.0, :user_time=>0.01, :sys_time=>0.0, :timestamp=>"2011-05-26T17:25:24.546-0700"}

          # "CMS-concurrent-abortable-preclean-start", :timestamp=>"2011-05-26T17:25:21.306-0700"}
          # "CMS-concurrent-sweep-start", :timestamp=>"2011-05-26T17:25:22.076-0700"}
          # "CMS-concurrent-reset-start", :timestamp=>"2011-05-26T17:25:24.544-0700"}
          # {:type=>"CMS-concurrent-preclean-start", :timestamp=>"2011-05-26T17:29:15.667-0700"}

          #ignore
        else
          puts :ignoring
          p datum
        end
      end
    end

    # File activesupport/lib/active_support/inflector/methods.rb, line 48
    def underscore(camel_cased_word)
      word = camel_cased_word.to_s.dup
      word.gsub!(/::/, '/')
      word.gsub!(/([A-Z]+)([A-Z][a-z])/,'\1_\2')
      word.gsub!(/([a-z\d])([A-Z])/,'\1_\2')
      word.tr!("-", "_")
      word.downcase!
      word
    end
  end
end