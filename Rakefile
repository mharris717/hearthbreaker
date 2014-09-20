task :test do
  exec "python -m unittest discover -s tests -p *_tests.py"
end

task default: :test

task :play do
  num = (ENV['num_games'] || 1).to_i
  puts "num: #{num}"
  exec "python hearthbreaker/ui/text_runner.py vanilla.hsdeck vanilla.hsdeck #{num}"
end