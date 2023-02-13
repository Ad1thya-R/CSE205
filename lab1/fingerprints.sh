#Display titles for table
echo Hostname$'\t'"| Fingerprint"
echo "---------------------|----------------------"
#Iterate through inputs
for var
do
	{

    		{
		#scan for key in variable with ends encoding
			ssh-keyscan -t ecdsa "$var" > key.pub 2> /dev/null
		} && { 
		#generate public key and cut out only key without names
			ssh-keygen -l -f key.pub 1> hash.txt
			hash=$(cut -d" " -f 2 hash.txt) 
			echo "$var"$'\t'"| ""$hash"
		}

	} || {
		#if keyscan fails to query host, report error for that row in the table
		echo "$var"$'\t'"| ERROR" 
    		 
	}
	
done