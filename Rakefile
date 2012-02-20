TEMPLATES = FileList["template/**/*"]

task :clean do
  if File.directory? "build"
    rmdir "build"
  end
end

task :build => [:clean] do
  directory "build"
  cp_r Dir["template/*"], "build/"
end
