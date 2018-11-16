import json
# set the output file for the escaped json to use in the cloudformation template
outfile = open('endpoints/escaped-table-settings.txt','w')
# set the input file of the original json to escape
infile = json.loads(open('endpoints/table-settings.json','r').read())
# this is the line that writes the escaped json for the s3 settings
outfile.writelines(json.dumps(json.dumps(infile)))