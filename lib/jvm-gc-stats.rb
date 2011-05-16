require 'jvm-gc-stats/tailer'

module JvmGcStats

  # If you wish to change the report method, simply open this class, make your changes, and
  # instantiate it. You may also extend it if that's your jam.
  #
  class JvmGcStats
    def initialize(filename, report, prefix, report_timeout, tail_sleep_secs, tail, debug)
      @filename = filename
      @report = report
      @prefix = prefix
      @report_timeout = report_timeout
      @tail_sleep_secs = tail_sleep_secs
      @debug = debug
      @tail = tail
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

    def run
      Tailer.new(@filename, @tail_sleep_secs, @tail).tail do |line|
        ingest(line)
        stat_reported = true
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

end
