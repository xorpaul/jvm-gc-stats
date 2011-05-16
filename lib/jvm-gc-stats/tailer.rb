module JvmGcStats
  class Tailer
    TAIL_BLOCK_SIZE = 2048

    def initialize(filename, tail_sleep_secs, tail)
      @filename = filename
      @tail_sleep_secs = tail_sleep_secs
      @tail = tail
    end

    # Returns a File object in read-mode for a given file. defaults to @filename
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
      lines = ""

      # Loop forever, reading every @tail_sleep_secs
      loop do
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
              yield line
            end
          end
        end

        sleep @tail_sleep_secs
      end
    end
  end
end