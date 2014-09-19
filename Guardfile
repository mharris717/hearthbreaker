# A sample Guardfile
# More info at https://github.com/guard/guard#readme

def test_once
  pid = fork do
    exec "python -m unittest discover -s tests -p *_tests.py -f"
  end

  puts "\n"

  Process.wait pid
end

guard :shell do
  watch /\.py$/ do |m|
    puts m.inspect
    test_once
  end
end
