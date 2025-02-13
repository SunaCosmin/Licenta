#!usr/bin/perl
use strict;
use warnings;
my @dirs=split('\n',`ls | grep http`);
for my $dir (@dirs){
    my $buffer=$dir;
    $dir =~ s/_/\//g;
    if(!(-e "$buffer/url.txt")){
        system("touch $buffer/url.txt");
        system("echo \"$dir\" > $buffer/url.txt");
    }
}
    
    
