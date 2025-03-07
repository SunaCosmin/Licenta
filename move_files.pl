#!usr/bin/perl

my @dirs = split(/\n/,qx/ls data\/buffer/);

foreach my $dir (@dirs){
   if(-e "data/$dir"){
        print("$dir deleted because it alerdy exists\n");
        system("rm -rf data/buffer/$dir");
   }
}
if(qx/ls data\/buffer/){
   system("mv data/buffer/* data")
}