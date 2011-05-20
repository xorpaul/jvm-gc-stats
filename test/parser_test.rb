require 'test/unit'

require 'jvm-gc-stats/parser'

include JvmGcStats

# TODO newgen -> younggen

class TestParser < Test::Unit::TestCase

  def TODO_test_promotion_failure
    line = "2011-05-17T00:05:07.578+0000: 5476.117: [GC 5476.117: [ParNew (promotion failed): " +
      "921071K->910414K(943744K), 0.6016610 secs]5476.719: [CMS: 5709084K->1684721K(7340032K)," +
      " 6.7565140 secs] 6612511K->1684721K(8283776K), [CMS Perm : 46904K->46744K(78112K)], 7.3585570" +
      " secs] [Times: user=7.61 sys=0.15, real=7.35 secs]"
    data = {
      :user_time => 7.61,
      :sys_time  => 0.15,
      :real_time => 7.35,
      :timestamp => "2011-05-17T00:05:07.578+0000",
      :promotion_failure => true,
      :newgen_kb_before => 921071,
      :newgen_kb_after =>  910414,
      :cms_kb_before => 5709084,
      :cms_kb_after =>  1684721
    }
    assert_equal data, Parser.parse(line)
  end

  def assert_each(a, b)
    (a.keys + b.keys).uniq.each do |k|
      assert_equal a[k], b[k], k
    end
    assert_equal a.keys.map{|k| k.to_s}.sort, b.keys.map{|k| k.to_s}.sort
  end

  def assert_parsed(line, data)
    assert_each(data, Parser.parse(line))
  end

  def test_parnew
    line = "2011-05-16T19:01:54.600+0000: 12.340: [GC 12.340: [ParNew: 943744K->104832K(943744K)," +
    " 0.4265660 secs] 1133140K->463127K(8283776K), 0.4266400 secs] [Times: user=1.93 sys=0.21, real=0.43 secs]"
    data = {
      :type => 'ParNew',
      :user_time => 1.93,
      :sys_time  => 0.21,
      :real_time => 0.43,
      :timestamp => "2011-05-16T19:01:54.600+0000",
      :newgen_kb_before => 943744,
      :newgen_kb_after =>  104832,
      :total_kb_before => 1133140,
      :total_kb_after => 463127
    }
    assert_each data, Parser.parse(line)

    line = "2011-05-16T19:01:52.029+0000: 9.769: [GC 9.769: [ParNew: 838912K->104832K(943744K), 0.0638820 secs] 878352K->149649K(8283776K), 0.0639590 secs] [Times: user=0.59 sys=0.05, real=0.06 secs]"
    data = {
      :type => 'ParNew',
      :user_time => 0.59,
      :sys_time  => 0.05,
      :real_time => 0.06,
      :timestamp => "2011-05-16T19:01:52.029+0000",
      :newgen_kb_before => 838912,
      :newgen_kb_after =>  104832,
      :total_kb_before => 878352,
      :total_kb_after => 149649
    }
    assert_each data, Parser.parse(line)
  end

  def test_full
    assert_parsed(
      "2011-05-16T19:01:49.148+0000: 6.888: [Full GC 6.906: [CMS: 22065K->39440K(7340032K), 0.3012410 secs] 240184K->39440K(8283776K), [CMS Perm : 35150K->35025K(35236K)], 0.3014270 secs] [Times: user=0.30 sys=0.01, real=0.32 secs]",
      data = {
        :type            => "Full",
        :user_time       => 0.30,
        :sys_time        => 0.01,
        :real_time       => 0.32,
        :timestamp       => "2011-05-16T19:01:49.148+0000",
        :total_kb_before => 240184,
        :total_kb_after  => 39440,
        :blocking        => true,
        :permgen_kb_before => 35150,
        :permgen_kb_after => 35025,
        :oldgen_kb_before => 22065,
        :oldgen_kb_after => 39440
      }
    )
    assert_parsed(
      "2011-05-11T04:28:36.398+0000: 257.070: [Full GC [PSYoungGen: 3936K->0K(85760K)] [ParOldGen: 252218K->120734K(221056K)] 256154K->120734K(306816K) [PSPermGen: 12177K->12153K(24896K)], 0.3264320 secs] [Times: user=2.75 sys=0.21, real=0.33 secs]",
      {
        :type => "Full",
        :timestamp => "2011-05-11T04:28:36.398+0000",
        :newgen_kb_before => 3936,
        :newgen_kb_after => 0,
        :oldgen_kb_before => 252218,
        :oldgen_kb_after => 120734,
        :total_kb_before => 256154,
        :total_kb_after => 120734,
        :permgen_kb_before => 12177,
        :permgen_kb_after => 12153,
        :user_time => 2.75,
        :sys_time => 0.21,
        :real_time => 0.33,
      }
    )
  end

  def test_cms_initial_mark
    line = "2011-05-12T15:18:28.890+0000: 53120.012: [GC [1 CMS-initial-mark: 9230012K(12306048K)] 9230979K(12555264K), 0.0029720 secs] [Times: user=0.00 sys=0.00, real=0.00 secs]"
    data = {
      :type => "CMS-initial-mark",
      :timestamp => "2011-05-12T15:18:28.890+0000",
      :user_time => 0.0,
      :sys_time => 0.0,
      :real_time => 0.0
    }
    assert_each(data, Parser.parse(line))

    line = "2011-05-14T14:48:00.719+0000: 224091.840: [GC [1 CMS-initial-mark: 9230311K(12306048K)] 9232833K(12555264K), 0.0030280 secs] [Times: user=0.00 sys=0.00, real=0.01 secs]"
    data = {
      :type      => "CMS-initial-mark",
      :timestamp => "2011-05-14T14:48:00.719+0000",
      :user_time => 0.0,
      :sys_time  => 0.0,
      :real_time => 0.01
    }
    assert_each(data, Parser.parse(line))
  end

  def test_cms_concurrent_mark
    line = "2011-05-12T15:18:32.227+0000: 53123.348: [CMS-concurrent-mark: 3.332/3.333 secs] [Times: user=13.02 sys=0.31, real=3.33 secs]"
    data = {
      :type      => "CMS-concurrent-mark",
      :timestamp => "2011-05-12T15:18:32.227+0000",
      :user_time =>13.02,
      :sys_time  => 0.31,
      :real_time => 3.33
    }
    assert_each(data, Parser.parse(line))

    line = "2011-05-13T13:27:10.819+0000: 132841.940: [CMS-concurrent-mark: 3.415/3.415 secs] [Times: user=13.54 sys=0.20, real=3.42 secs]"
    data = {
      :type      => "CMS-concurrent-mark",
      :timestamp => "2011-05-13T13:27:10.819+0000",
      :user_time =>13.54,
      :sys_time  => 0.20,
      :real_time => 3.42
    }
    assert_each(data, Parser.parse(line))
  end

  def test_cms_concurrent_preclean
    line = "2011-05-12T15:18:32.265+0000: 53123.386: [CMS-concurrent-preclean: 0.038/0.039 secs] [Times: user=0.03 sys=0.00, real=0.04 secs]"
    data = {
      :type      => "CMS-concurrent-preclean",
      :timestamp => "2011-05-12T15:18:32.265+0000",
      :user_time => 0.03,
      :sys_time => 0.0,
      :real_time => 0.04
    }
    assert_each(data, Parser.parse(line))

    line = "2011-05-13T13:27:10.854+0000: 132841.975: [CMS-concurrent-preclean: 0.035/0.035 secs] [Times: user=0.03 sys=0.00, real=0.03 secs]"
    data = {
      :type => "CMS-concurrent-preclean",
      :timestamp => "2011-05-13T13:27:10.854+0000",
      :user_time => 0.03,
      :sys_time => 0.0,
      :real_time => 0.03
    }
    assert_each(data, Parser.parse(line))
  end

  def test_cms_concurrent_abortable_preclean
    line = "2011-05-13T13:27:15.423+0000: 132846.544: [CMS-concurrent-abortable-preclean: 1.964/4.569 secs] [Times: user=2.23 sys=0.22, real=4.57 secs]"
    data = {
      :type      => "CMS-concurrent-abortable-preclean",
      :timestamp => "2011-05-13T13:27:15.423+0000",
      :user_time => 2.23,
      :sys_time  => 0.22,
      :real_time => 4.57
    }
    assert_each(data, Parser.parse(line))

    line = "2011-05-15T17:41:55.914+0000: 320927.035: [CMS-concurrent-abortable-preclean: 2.039/5.044 secs] [Times: user=2.12 sys=0.07, real=5.04 secs]"
    data = {
      :type => "CMS-concurrent-abortable-preclean",
      :timestamp => "2011-05-15T17:41:55.914+0000",
      :user_time => 2.12,
      :sys_time => 0.07,
      :real_time => 5.04
    }
    assert_each(data, Parser.parse(line))
  end

  def test_cms_concurrent_mark_start
    assert_parsed(
      "2011-02-26T06:22:18.044+0000: 1387.343: [CMS-concurrent-mark-start]",
      {
        :timestamp => "2011-02-26T06:22:18.044+0000",
        :type => "CMS-concurrent-mark-start"
      }
    )

    assert_parsed(
      "2011-02-26T06:44:35.366+0000: 2724.665: [CMS-concurrent-mark-start]",
      {
        :timestamp => "2011-02-26T06:44:35.366+0000",
        :type => "CMS-concurrent-mark-start"
      }
    )
  end

  def test_cms_concurrent_preclean_start
    line = "2011-02-26T06:22:18.185+0000: 1387.484: [CMS-concurrent-preclean-start]"
    data = {
      :type => "CMS-concurrent-preclean-start",
      :timestamp => "2011-02-26T06:22:18.185+0000"
    }
    assert_parsed(line, data)

  end

  def test_concurrent_abortable_preclean_start
    assert_parsed(
      "2011-02-26T06:22:18.221+0000: 1387.520: [CMS-concurrent-abortable-preclean-start]",
      {
        :type => "CMS-concurrent-abortable-preclean-start",
        :timestamp => "2011-02-26T06:22:18.221+0000"
      }
    )

    assert_parsed(
      "2011-02-26T06:44:36.060+0000: 2725.359: [CMS-concurrent-abortable-preclean-start]",
      {
        :type => "CMS-concurrent-abortable-preclean-start",
        :timestamp => "2011-02-26T06:44:36.060+0000"
      }
    )
  end

  def test_remark
    assert_parsed(
      "2011-02-26T06:22:19.151+0000: 1388.450: [GC[YG occupancy: 1295191 K (2831168 K)]1388.451: [Rescan (parallel) , 0.1232920 secs]1388.574: [weak refs processing, 0.0194180 secs] [1 CMS-remark: 7082011K(9437184K)] 8377203K(12268352K), 0.1429890 secs] [Times: user=1.39 sys=0.00, real=0.14 secs]",
      {
        :timestamp => "2011-02-26T06:22:19.151+0000",
        :type => "CMS-remark",
        :user_time => 1.39,
        :sys_time => 0.00,
        :real_time => 0.14,
      }
    )

    assert_parsed(
      "2011-02-26T06:44:41.147+0000: 2730.446: [GC[YG occupancy: 499953 K (2831168 K)]2730.446: [Rescan (parallel) , 0.0627040 secs]2730.509: [weak refs processing, 0.0269890 secs] [1 CMS-remark: 7297991K(9437184K)] 7797944K(12268352K), 0.0899180 secs] [Times: user=0.82 sys=0.01, real=0.09 secs]",
      {
        :timestamp => "2011-02-26T06:44:41.147+0000",
        :type => "CMS-remark",
        :user_time => 0.82,
        :sys_time => 0.01,
        :real_time => 0.09,
      }
    )
  end

  def test_concurrent_sweep_start
    assert_parsed(
      "2011-02-26T06:22:19.295+0000: 1388.594: [CMS-concurrent-sweep-start]",
      {
        :type => "CMS-concurrent-sweep-start",
        :timestamp => "2011-02-26T06:22:19.295+0000"
      }
    )

    assert_parsed(
      "2011-02-26T06:44:41.237+0000: 2730.536: [CMS-concurrent-sweep-start]",
      {
        :type => "CMS-concurrent-sweep-start",
        :timestamp => "2011-02-26T06:44:41.237+0000"
      }
    )
  end

  def test_concurrent_sweep
    assert_parsed(
      "2011-02-26T06:22:39.421+0000: 1408.720: [CMS-concurrent-sweep: 20.008/20.126 secs] [Times: user=40.81 sys=7.39, real=20.13 secs]",
      {
        :type => "CMS-concurrent-sweep",
        :timestamp => "2011-02-26T06:22:39.421+0000",
        :user_time => 40.81,
        :sys_time => 7.39,
        :real_time => 20.13
      }
    )
    assert_parsed(
      "2011-02-26T06:45:01.542+0000: 2750.841: [CMS-concurrent-sweep: 20.177/20.305 secs] [Times: user=39.19 sys=6.75, real=20.30 secs]",
      {
        :type => "CMS-concurrent-sweep",
        :timestamp => "2011-02-26T06:45:01.542+0000",
        :user_time => 39.19,
        :sys_time => 6.75,
        :real_time => 20.30
      }
    )
  end

  def test_concurrent_reset_start
    assert_parsed(
      "2011-02-26T06:22:39.421+0000: 1408.720: [CMS-concurrent-reset-start]",
      {
        :type => "CMS-concurrent-reset-start",
        :timestamp => "2011-02-26T06:22:39.421+0000"
      }
    )
  end

  def test_concurrent_reset
    assert_parsed(
      "2011-02-26T06:22:39.440+0000: 1408.739: [CMS-concurrent-reset: 0.020/0.020 secs] [Times: user=0.03 sys=0.01, real=0.02 secs]",
      {
        :timestamp => "2011-02-26T06:22:39.440+0000",
        :type => "CMS-concurrent-reset",
        :user_time => 0.03,
        :sys_time => 0.01,
        :real_time => 0.02
      }
    )

    assert_parsed(
      "2011-02-26T06:45:01.565+0000: 2750.864: [CMS-concurrent-reset: 0.022/0.022 secs] [Times: user=0.05 sys=0.00, real=0.02 secs]",
      {
        :timestamp => "2011-02-26T06:45:01.565+0000",
        :type => "CMS-concurrent-reset",
        :user_time => 0.05,
        :sys_time => 0.00,
        :real_time => 0.02
      }
    )
  end

  def test_promotion_failure
    assert_parsed(
      "2011-02-26T18:01:07.838+0000: 43317.137: [GC 43317.137: [ParNew (promotion failed): 2658599K->2583089K(2831168K), 0.5888520 secs]43317.726: [CMS: 6913520K->591225K(9437184K), 4.3637290 secs] 9527815K->591225K(12268352K), [CMS Perm : 24617K->24383K(41104K)], 4.9529780 secs] [Times: user=5.85 sys=0.02, real=4.95 secs]",
      {
        :type => "promotion failure",
        :timestamp => "2011-02-26T18:01:07.838+0000",
        :newgen_kb_before => 2658599,
        :newgen_kb_after => 2583089,
        :oldgen_kb_before => 6913520,
        :oldgen_kb_after => 591225,
        :newgen_kb_after => 2583089,
        :total_kb_before => 9527815,
        :total_kb_after => 591225,
        :permgen_kb_before => 24617,
        :permgen_kb_after => 24383,
        :user_time => 5.85,
        :sys_time => 0.02, 
        :real_time => 4.95
      }
    )
  end

  def test_ignore
    [
         "par new generation   total 2831168K, used 2384921K [0x00007f32c0fc0000, 0x00007f3380fc0000, 0x00007f3380fc0000)            ",
         "eden space 2516608K,  90% used [0x00007f32c0fc0000, 0x00007f334b60c350, 0x00007f335a960000)                                ",
         " from space 314560K,  37% used [0x00007f335a960000, 0x00007f3361c1a490, 0x00007f336dc90000)                                ",
         " to   space 314560K,   0% used [0x00007f336dc90000, 0x00007f336dc90000, 0x00007f3380fc0000)                                ",
         "concurrent mark-sweep generation total 9437184K, used 3087239K [0x00007f3380fc0000, 0x00007f35c0fc0000, 0x00007f35c0fc0000)",
         "concurrent-mark-sweep perm gen total 41104K, used 24528K [0x00007f35c0fc0000, 0x00007f35c37e4000, 0x00007f35c63c0000)      ",
    ].each do |line|
      assert_parsed(
        line,
        {:ignore => true}
      )
    end
  end

  def test_kestrel
    assert_parsed(
      "2011-05-11T04:24:20.339+0000: 1.012: [GC [PSYoungGen: 96640K->640K(112704K)] 96640K->640K(370368K), 0.0123710 secs] [Times: user=0.07 sys=0.00, real=0.02 secs]",
      {
        :timestamp => "2011-05-11T04:24:20.339+0000",
        :type => "PSYoungGen",
        :newgen_kb_before => 96640,
        :newgen_kb_after => 640,
        :total_kb_before => 96640,
        :total_kb_after => 640,
        :user_time => 0.07,
        :sys_time => 0.0,
        :real_time => 0.02
      }
    )
  end

  def TODO_test_with_tenuring_distribution
    # 2011-05-13T01:14:09.835+0000: 0.920: [GC
    #   Desired survivor size 49545216 bytes, new threshold 7 (max 15)
    #   [PSYoungGen: 290560K->25022K(338944K)] 290560K->25022K(1113728K), 0.0237240 secs] [Times: user=0.13 sys=0.13, real=0.03 secs]
  end
end