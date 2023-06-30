# =============================================================
#                                                  
#   █████████   █████████                          
#  ███░░░░░███ ███░░░░░███  Suchith Sridhar        
# ░███    ░░░ ░███    ░░░   
# ░░█████████ ░░█████████   https://suchicodes.com 
#  ░░░░░░░░███ ░░░░░░░░███  https://github.com/suchithsridhar
#  ███    ░███ ███    ░███  
# ░░█████████ ░░█████████                            
#  ░░░░░░░░░   ░░░░░░░░░                            
#                                                    
# =============================================================
# A program to format and clean up X12 / .edi files
# =============================================================

import os
import sys

args = sys.argv
logs = []


if (len(args) != 2):
	print("Invalid call to program")
	print("Valid example: python <program>.py <filename>.edi")
	exit(1)


try:
	with open(args[1]) as f:
		data = f.readlines()
except FileNotFoundError as e:
	print("File given was not found: ", args[1])
	exit(1)


fname_without_ext, ext = os.path.splitext(args[1])

if (ext.lower() != ".edi"):
	print("File given did not end with .edi - exiting")
	exit(1)


new_data = []
for i, line in enumerate(data, 1):
	line = line.strip("\n")

	l2 = line.strip("\t")
	if (l2 != line):
		logs.append(("Removed tabs on line", i))
		line = l2

	if len(line) == 0:
		continue

	if line[:2] == "//":
		logs.append(("Removed comment on line",i))
		continue

	l2 = line.strip(" ")
	if (l2 != line):
		logs.append(("Removed spaces on line", i))
		line = l2

	if (line[-1] != "~"):
		logs.append(("Added missing ~ on line", i))
		line += "~"

	line = line + "\n"
	new_data.append(line)

new_data[-1] = new_data[-1].strip("\n") 

max_comment = 0
for comment, line in logs:
	if (len(comment)) > max_comment:
		max_comment = len(comment)

max_comment += 2

log_strs = []
for comment, line in logs:
	string = f"{comment}: {'.' * (max_comment - len(comment))} {line}\n"
	log_strs.append(string)

log_strs[-1] = log_strs[-1]

with open(f"{fname_without_ext}-formatted{ext}", 'w') as f:
	f.writelines(new_data)

with open(f"{fname_without_ext}-errors.txt", 'w') as f:
	f.writelines(log_strs)
