#!usr/bin/perl

my @dirs = split(/\n/,qx/ ls buffer /);

foreach my $dir (@dirs){
   if(-e "../data/$dir"){
        print("$dir deleted because it alerdy exists\n");
        system("rm -rf buffer/$dir");
   }
}
if(qx/ls buffer/){
   system("mv buffer/* ../data")
}