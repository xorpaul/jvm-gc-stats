require 'test/unit'

require 'jvm-gc-stats'

include JvmGcStats

class TestTailer < Test::Unit::TestCase
  def test_open_file
    assert_kind_of File, Tailer.new(__FILE__, 0).open_file()
  end
end