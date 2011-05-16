#!/usr/bin/ruby
# jvm-gc-stats: gather stats from jvm garbage collection trace and publish ganglia graphs

require 'getoptlong'


# If you wish to change the report method, simply open this class, make your changes, and
# instantiate it. You may also extend it if that's your jam.
#
class JvmGcStats
  def usage
    puts "jvm-gc-stats.rb: Tails a jvm logfile and reports its entries "
    puts
    puts "usage: jvm-gc-stats.rb [options]"
    puts "options:"
    puts "    -n              say what I would report, but don't report it"
    puts "    -P <prefix>     optional prefix for ganglia names"
    puts "    -f <file>       gc logfile to use. defaults to a file named stdout"
    puts "    -s seconds      sleep time in seconds waiting for new log lines"
    puts "    -d              turn on verbose debug output"
    puts "    -w              read the whole file from the beginning rather than tail"
    puts
  end

  # Initializing the class will process stdin for command-line args and start processing.
  def initialize(filename="stdout", report=true, prefix='', report_timeout=86400, tail_sleep_secs=60, tail=true, debug=false)
    @filename = filename
    @report = report
    @prefix = prefix
    @report_timeout = report_timeout
    @tail_sleep_secs = tail_sleep_secs
    @debug = debug
    @tail = tail

    opts = GetoptLong.new(
      [ '--help', GetoptLong::NO_ARGUMENT ],
      [ '-h', GetoptLong::NO_ARGUMENT ],
      [ '-n', GetoptLong::NO_ARGUMENT ],
      [ '-P', GetoptLong::OPTIONAL_ARGUMENT ],
      [ '-f', GetoptLong::OPTIONAL_ARGUMENT ],
      [ '-s', GetoptLong::OPTIONAL_ARGUMENT ],
      [ '-d', GetoptLong::OPTIONAL_ARGUMENT ],
      [ '-w', GetoptLong::OPTIONAL_ARGUMENT ]
    )

    opts.each do |opt, arg|
      case opt
      when '--help'
        usage
        exit 0
      when '-h'
        usage
        exit 0
      when '-n'
        @report = false
      when '-P'
        @prefix = arg
      when '-f'
        @filename = arg
      when '-s'
        @tail_sleep_secs = arg.to_i
      when '-d'
        @debug = true
      when '-w'
        @tail = false
      end
    end

  end


  # Inserts metrics with the name and value into the reporting system
  # By default, this is ganglia via gmetric. This is the method to
  # override if you want your own reporting.
  def report(name, value, units="items")
    key = "#{@prefix}jvm.gc.#{name}"

    if @report
      system("gmetric -t float -n \"#{key}\" -v \"#{value}\" -u \"#{units}\" -d #{@report_timeout}")
    end

    if @debug
      puts "#{key}=#{value} #{units}"
    end
  end

  # Returns a File object in read-mode for a given file. defaults to @filename
  def open_file(file=@filename)
    File.new(file, "r")
  end

  TAIL_BLOCK_SIZE = 2048
  ALL_MEASUREMENTS = %w[promoFail.realSec major.concur.userSec major.concur.realSec major.block.userSec] +
                     %w[%s.survivalRatio %s.kbytesPerSec %s.userSec %s.realSec].collect{|m| %w[minor full].collect{|s| m % s}}.flatten

  # Read a file, optionally just the tail of the file (based on the @tail variable)
  # and for each logline, report it's stats.
  def tail(file=@filename)
    # There are 4 scenarios this code has to handle
    #  empty read
    #  partial read (no full record)
    #  full record (ending on a \n)
    #  full record with partial record
    f = open_file(file)
    f.seek(0, IO::SEEK_END) if @tail
    stat = f.stat
    current_inode, current_dev, current_size = stat.ino, stat.dev, stat.size
    lines = ""

    # Loop forever, reading every @tail_sleep_secs
    loop do
      stat_reported = false

      # Loop reading until there's nothing more to read
      loop do
        # Limit reads to prevent loading entire file into memory if not seeking to end
        part = f.read_nonblock(TAIL_BLOCK_SIZE) rescue nil
        stat = f.stat
        if part
          current_size = stat.size
          if part =~ /\A\0+\Z/
            # Skip past blobs of NUL bytes in corrupted log files.  This happens
            # sometimes, probably due to bad log rotation.
            next
          end
          lines += part
        elsif stat.ino != current_inode || stat.dev != current_dev ||
          stat.size < current_size
          # File rotated/truncated, reopen
          f = open(file)
          stat = File.stat(file)
          current_inode, current_dev = stat.ino, stat.dev
        else
          # nothing more to read: break and sleep
          break
        end

        if lines.include?("\n")
          # If there isn't a null trailing field, last string isn't newline terminated
          split = lines.split("\n", TAIL_BLOCK_SIZE)
          if split[-1] == ""
            # Remove null trailing field
            split.pop
            lines = "" # reset lines
          else
            # Save partial line for next round
            lines = split.pop
          end

          split.each do |line|
            ingest(line)
            stat_reported = true
          end
        end

        # If no stat was reported through this loop, then report zeros as
        # sentinels.
        if !stat_reported
          ALL_MEASUREMENTS.each { |m| report(m, 0) }
        end
      end

      sleep @tail_sleep_secs
    end
  end

  USER_REAL        = '.*?user=(\d+.\d+).*?real=(\d+.\d+)'
  MINOR_PAR        = Regexp.new('PSYoungGen: (\d+)K->(\d+)' + USER_REAL)
  MINOR            = Regexp.new('ParNew: (\d+)K->(\d+)' + USER_REAL)
  FULL             = Regexp.new('Full GC \[CMS: (\d+)K->(\d+)' + USER_REAL)
  FULL_PAR         = Regexp.new('Full GC \[PSYoungGen: (\d+)K->(\d+)' + USER_REAL)
  PROMOTION_FAILED = Regexp.new('promotion failed' + USER_REAL)
  SCAVANGE         = Regexp.new('Trying a full collection because scavenge failed')
  CMS_START        = Regexp.new('\[CMS-concurrent.*start\]')
  CMS_CONCURRENT   = Regexp.new('CMS-concurrent' + USER_REAL)
  CMS_BLOCK        = Regexp.new('CMS-(initial-|re)mark' + USER_REAL)
  STARTUP          = Regexp.new('^Heap$|^ par new generation|^  eden space|^  from space|^  to   space|^ concurrent mark-sweep generation|^ concurrent-mark-sweep perm')

  def denominator(val)
    rv = val.to_f
    # Assume that collections under a millisecond took half a millisecond
    rv = 0.05 if rv == 0
    rv
  end

  def minorAndFull(match, collection, str)
    fromK       = match[1].to_i
    toK         = match[2].to_i
    deltaK      = fromK - toK
    ratio       = toK.to_f / fromK.to_f
    userSec     = denominator(match[3])
    realSec     = denominator(match[4])
    kPerRealSec = deltaK / realSec
    kPerUserSec = deltaK / userSec

    if @debug
      printf("%-15s user %5.2f real %5.2f ratio %1.3f kPerUserSec %10d kPerRealSec %10d \n",
             collection, userSec, realSec, ratio, kPerUserSec, kPerRealSec)
    end

    report("#{collection}.survivalRatio", ratio)
    report("#{collection}.kbytesPerSec", kPerRealSec)
    report("#{collection}.userSec", userSec)
    report("#{collection}.realSec", realSec)
  end

  # Parses a GC logline and report the metrics it contains.
  def ingest(str)
    case str
    when FULL
      minorAndFull($~, "full", str)
    when FULL_PAR
      minorAndFull($~, "full", str)
    when MINOR
      minorAndFull($~, "minor", str)
    when MINOR_PAR
      minorAndFull($~, "minor", str)
    when PROMOTION_FAILED
      userSec = $~[1].to_f
      realSec = $~[2].to_f
      printf "%-15s user %5.2f real %5.2f\n", "promoFail", userSec, realSec if @debug
      # Reporting userSec for promotion failures is redundant
      report("promoFail.realSec", realSec)
    when CMS_CONCURRENT
      userSec = $~[1].to_f
      realSec = $~[2].to_f
      printf "%-15s user %5.2f real %5.2f\n", "major concur", userSec, realSec if @debug
      report("major.concur.userSec", userSec)
      report("major.concur.realSec", realSec)
    when CMS_BLOCK
      userSec = $~[2].to_f
      realSec = $~[3].to_f
      printf "%-15s user %5.2f real %5.2f\n", "major block", userSec, realSec if @debug
      report("major.block.userSec", userSec)
      report("major.block.realSec", realSec)
    when CMS_START
      puts "ignore cms start #{str}" if @debug
    when STARTUP
      puts "ignore startup #{str}" if @debug
    when SCAVANGE
      puts "ignore scavange #{str}" if @debug
    else
      puts "UNMATCHED #{str}" if @debug
    end
  end
end


# If we're being run from the command-line, treat as a script.
if __FILE__ == $0
  gcstats = JvmGcStats.new
  gcstats.tail
end

