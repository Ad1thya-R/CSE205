#userid: Adithya.ravichadran
#!/bin/bash
#if no directory is specified, set directory to root
if [ $# -eq 0 ]
then
    dir=.
else
    dir=$1
fi
#check that dir is a directory
if [ ! -d $dir ]
then
    echo "Error: $dir is not a directory"
    exit 1
fi
#Recursive subtree to display directory structure
function subtree {
    #keep track of level of directory relative to starting directory and current directory itself
    local level=$1
    local dir=$2
    local i
    #iterate through the current directory
    for i in `ls $dir`
    do
	#if the current item is a directory, then proceed to display it in the file structure
        if [ -d $dir/$i ]
        then
	    bars=""
	    #iterate to add bars based on the level of the current directory
            for ((j=0; j<$level; j++))
            do
                bars+="| "
            done
            echo "$bars""+ $i"
	    #Recurse with one level higher and in the current subdirectory
            subtree $((level+1)) $dir/$i
        fi
    done
}
subtree 0 $dir