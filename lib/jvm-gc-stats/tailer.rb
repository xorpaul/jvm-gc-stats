require 'strscan'

module JvmGcStats
  class Tailer
    TAIL_BLOCK_SIZE = 2048

    def initialize(filename, tail_sleep_secs=60, tail=true)
      @filename = filename
      @tail_sleep_secs = tail_sleep_secs
      @tail = tail
    end

    def open_file(file=@filename)
      File.new(file, "r")
    end

    # Read a file, optionally just the tail of the file (based on the @tail variable)
    # and for each logline, report it's stats.
    def tail
      # There are 4 scenarios this code has to handle
      #  empty read
      #  partial read (no full record)
      #  full record (ending on a \n)
      #  full record with partial record
      f = open_file(@filename)
      f.seek(0, IO::SEEK_END) if @tail
      stat = f.stat
      current_inode, current_dev, current_size = stat.ino, stat.dev, stat.size
      buffer = ""

      # Loop forever, reading every @tail_sleep_secs
      loop do
        # Loop reading until there's nothing more to read
        loop do
          # Limit reads to prevent loading entire file into memory if not seeking to end
          block = begin
            f.read_nonblock(TAIL_BLOCK_SIZE) 
          rescue =>e
            p e
            nil
          end
          stat = f.stat
          if block
            current_size = stat.size
            buffer += block
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

          scanner = StringScanner.new(buffer)
          while line = scanner.scan_until(/\n/)
            yield line
          end
          buffer = scanner.rest
        end

        sleep @tail_sleep_secs
      end
    end
  end
end