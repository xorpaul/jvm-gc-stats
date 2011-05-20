module JvmGcStats
  class Parser
    def self.parse(line)
      case line
      when /(.*): \d+\.\d+: \[GC \d+\.\d+: \[ParNew: (\d+)K\->(\d+)K\(\d+K\), \d+\.\d+ secs\] (\d+)K\->(\d+)K\(\d+K\), \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]/
        m = $~
        {
          :type             => 'ParNew',
          :user_time        => m[6].to_f,
          :sys_time         => m[7].to_f,
          :real_time        => m[8].to_f,
          :timestamp        => m[1],
          :newgen_kb_before => m[2].to_i,
          :newgen_kb_after  => m[3].to_i,
          :total_kb_before  => m[4].to_i,
          :total_kb_after   => m[5].to_i
        }
      when /(.*): \d+\.\d+: \[GC \[1 CMS\-initial\-mark: \d+K\(\d+K\)\] \d+K\(\d+K\), \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]/
        m = $~
        {
          :type      => 'CMS-initial-mark',
          :timestamp => m[1],
          :user_time => m[2].to_f,
          :sys_time  => m[3].to_f,
          :real_time => m[4].to_f
        }
      when /(.*): \d+\.\d+: \[(CMS-concurrent-abortable-preclean|CMS-concurrent-preclean|CMS-concurrent-mark): \d+\.\d+\/\d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]/
        m = $~
        {
          :timestamp => m[1],
          :type => m[2],
          :user_time => m[3].to_f,
          :sys_time => m[4].to_f,
          :real_time => m[5].to_f
        }
      when /(.*): \d+\.\d+: \[Full GC \d+\.\d+: \[CMS: (\d+)K->(\d+)K\(\d+K\), \d+\.\d+ secs\] (\d+)K->(\d+)K\(\d+K\), \[CMS Perm : (\d+)K->(\d+)K\(\d+K\)\], \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]/
        m = $~
        {
          :type => "Full",
          :blocking => true,
          :timestamp => m[1],
          :oldgen_kb_before => m[2].to_i,
          :oldgen_kb_after => m[3].to_i,
          :total_kb_before => m[4].to_i,
          :total_kb_after => m[5].to_i,
          :permgen_kb_before => m[6].to_i,
          :permgen_kb_after => m[7].to_i,
          :user_time => m[8].to_f,
          :sys_time => m[9].to_f,
          :real_time => m[10].to_f
        }
      when /(.*): \d+\.\d+: \[(CMS-concurrent-mark-start|CMS-concurrent-preclean-start|CMS-concurrent-abortable-preclean-start|CMS-concurrent-sweep-start|CMS-concurrent-reset-start)\]/
        m = $~
        {
          :type => m[2],
          :timestamp => m[1]
        }
      when /(.*): \d+\.\d+: \[GC\[YG occupancy: \d+ K \(\d+ K\)\]\d+\.\d+: \[Rescan \(parallel\) , \d+\.\d+ secs\]\d+\.\d+: \[weak refs processing, \d+\.\d+ secs\] \[1 CMS-remark: \d+K\(\d+K\)\] \d+K\(\d+K\), \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]/
        m = $~
        {
          :type => "CMS-remark",
          :timestamp => m[1],
          :user_time => m[2].to_f,
          :sys_time  => m[3].to_f,
          :real_time => m[4].to_f
        }
      when /(.*): \d+\.\d+: \[(CMS-concurrent-reset|CMS-concurrent-sweep): \d+\.\d+\/\d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]/
        m = $~
        {
          :timestamp => m[1],
          :type => m[2],
          :user_time => m[3].to_f,
          :sys_time  => m[4].to_f,
          :real_time => m[5].to_f
        }
      when /(.*): \d+\.\d+: \[GC \d+\.\d+: \[ParNew \(promotion failed\): (\d+)K->(\d+)K\(\d+K\), \d+\.\d+ secs\]\d+\.\d+: \[CMS: (\d+)K->(\d+)K\(\d+K\), \d+\.\d+ secs\] (\d+)K->(\d+)K\(\d+K\), \[CMS Perm : (\d+)K->(\d+)K\(\d+K\)\], \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]/
        m = $~
        {
          :timestamp => m[1],
          :type => "promotion failure",
          :newgen_kb_before => m[2].to_i,
          :newgen_kb_after => m[3].to_i,
          :oldgen_kb_before => m[4].to_i,
          :oldgen_kb_after => m[5].to_i,
          :total_kb_before => m[6].to_i,
          :total_kb_after => m[7].to_i,
          :permgen_kb_before => m[8].to_i,
          :permgen_kb_after => m[9].to_i,
          :user_time => m[10].to_f,
          :sys_time => m[11].to_f,
          :real_time => m[12].to_f
        }
      when /Heap/, /\w*(par|eden|from|to|concurrent)/
        {:ignore => true}
      when /(.*): \d+\.\d+: \[GC \[PSYoungGen: (\d+)K->(\d+)K\(\d+K\)\] (\d+)K->(\d+)K\(\d+K\), \d+\.\d+ secs\] \[Times: user=(\d+\.\d+) sys=(\d+\.\d+), real=(\d+\.\d+) secs\]/
        m = $~
        {
          :type             => 'PSYoungGen',
          :timestamp        => m[1],
          :newgen_kb_before => m[2].to_i,
          :newgen_kb_after  => m[3].to_i,
          :total_kb_before  => m[4].to_i,
          :total_kb_after   => m[5].to_i,
          :user_time        => m[6].to_f,
          :sys_time         => m[7].to_f,
          :real_time        => m[8].to_f,
        }
      else
        raise "couldn't parse #{line}"
      end
    end
  end
end