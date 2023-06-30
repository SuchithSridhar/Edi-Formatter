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
# A program to identify loops in X12/edi.
# =============================================================

import os
import sys
import loopinfo
from loopinfo import bc
from random import randint

# Separator for segment parts
DELIMITER="*"

# Terminates a segment
TERMINATOR="~"

WHITESPACE=" \t\n\r"
COMMENT="//"
NEWLINE="\n"
INDENT_STR="\t"

# Just used for internal purposes
START="start"
END="end"
SEGMENT="segment"

FILE_MARKER="SSEDI"

logs = []

GENERATE_RAND = False
HL_MODIFIER = True

class SegmentCounter:
	counting = False
	count = 0
	start = 0
	generated_id = 0

class ClaimAmountCheck:
	clm_pos = 0
	clm_total = 0
	sv2_sum = 0
	sv2_pos = []
	active = False

class HLTracker:
	counter = 1


def find_non_whitespace_character(string: str):
	for index, char in enumerate(string):
		if char not in WHITESPACE:
			return index

	# For empty lines
	raise ValueError("non-whitespace character not found.");

def parse_edi_to_array(lines: list[str]):
	# Example line: "\t\t SE*1393*3013~\n\r"
	data = []
	for index, line in enumerate(lines):
		try:
			index_start = find_non_whitespace_character(line)
		except ValueError:
			# Empty line
			parts = {
				START: "",
				SEGMENT: "",
				END: line
			}
			data.append(parts)
			continue

		try:
			index_tilda = line.index(TERMINATOR)
		except ValueError:
			if (not line[index_start:].startswith(COMMENT)):
				# Missing terminator "~"
				index_newline = line.index(NEWLINE)
				if (index_newline == -1):
					line += TERMINATOR
				else:
					line = line[:index_newline] + TERMINATOR + line[index_newline:]

				logs.append((index+1, f"Added missing {TERMINATOR}"))
				
				# we added the TERMINATOR so it's not going to be -1
				index_tilda = line.index(TERMINATOR)
			else:
				# Comment
				index_tilda = line.index(NEWLINE)

		parts = {
			START: line[:index_start],
			SEGMENT: line[index_start:index_tilda].split(DELIMITER),
			END:line[index_tilda:]
		}
		data.append(parts)
	
	return data

def edi_array_to_lines(edi_array):
	lines = []

	for item in edi_array:
		segment_str = DELIMITER.join(item[SEGMENT])
		line = item[START] + segment_str + item[END]
		lines.append(line)

	return lines

def check_errors(args):
	if (len(args) != 2):
		print("Invalid call to program")
		print("Valid example: python <program>.py <filename>.edi")
		exit(1)

	try:
		with open(args[1]):
			pass

	except FileNotFoundError:
		print("File given was not found: ", args[1])
		exit(1)

	_, ext = os.path.splitext(args[1])

	if (ext.lower() != ".edi"):
		print("File given did not end with .edi - exiting")
		exit(1)


def handle_segment_count(item, index):
	if (item[SEGMENT][0] == "ST"):
		if (SegmentCounter.counting):
			print(f"Recieved ST 2x in a row at {SegmentCounter.start + 1} and {index + 1}. Exiting.")
			exit(1)

		SegmentCounter.counting = True
		SegmentCounter.start = index
		SegmentCounter.count = 0
		SegmentCounter.generated_id = randint(10**8, 10**9 -1)

		if GENERATE_RAND:
			item[SEGMENT][2] = str(SegmentCounter.generated_id)

	if (SegmentCounter.counting):
		SegmentCounter.count += 1

	if (item[SEGMENT][0] == "SE"):
		if (not SegmentCounter.counting):
			print(f"Recieved SE before ST at {index + 1}. Exiting.")
			exit(1)

		count = int(item[SEGMENT][1])
		if (count != SegmentCounter.count):
			logs.append((index, f"Segment Count for SE mismatch, updating to {SegmentCounter.count}"))
			item[SEGMENT][1] = str(SegmentCounter.count)

		if GENERATE_RAND:
			item[SEGMENT][2] = str(SegmentCounter.generated_id)


		SegmentCounter.counting = False

	return item


def handle_claim_sum(item, index):
	if (item[SEGMENT][0] == "CLM"):
		if (ClaimAmountCheck.active):
			print(f"Recieved two CLMs in a row at {ClaimAmountCheck.clm_pos+1} and {index+1}. Exiting.")
			exit(1)

		ClaimAmountCheck.active = True
		ClaimAmountCheck.clm_pos = index
		ClaimAmountCheck.clm_total = float(item[SEGMENT][2])  # Total amount
		ClaimAmountCheck.sv2_sum = 0
		ClaimAmountCheck.sv2_pos.clear()

	if (item[SEGMENT][0] == "SV2"):
		if (not ClaimAmountCheck.active):
			print(f"Recieved SV2 without CLM at {index+1}. Exiting.")
			exit(1)

		ClaimAmountCheck.sv2_sum += float(item[SEGMENT][3])
		ClaimAmountCheck.sv2_pos.append(index)

	if (item[SEGMENT][0] == "SE"):
		if (not ClaimAmountCheck.active):
			print(f"Recieved SE without CLM at {index+1}. Exiting.")
			exit(1)

		if (ClaimAmountCheck.sv2_sum != ClaimAmountCheck.clm_total):
			print(f"{bc.FAIL}CLM total mismatch. SV2 total: {ClaimAmountCheck.sv2_sum}, CLM total: {ClaimAmountCheck.clm_total}{bc.ENDC}")
			print(f"\t SV2 segments lines: {ClaimAmountCheck.sv2_pos} and CLM segment line: {ClaimAmountCheck.clm_pos}")

		ClaimAmountCheck.active = False

	return item

def handle_hl_tags(item, index):

	if HL_MODIFIER:
		if (item[SEGMENT][0] == "SE"):
			HLTracker.counter = 1

		if (item[SEGMENT][0] == "HL"):
			item[SEGMENT][1] = str(HLTracker.counter)
			HLTracker.counter += 1

			if (len(item[SEGMENT]) != 5):
				item[SEGMENT] = item[SEGMENT].insert(2, "")


	if (item[SEGMENT][0] == "HL" and item[SEGMENT][3] == "20"):
		if (item[SEGMENT][2] != ""):
			logs.append((index, f"HL Billing Provider Level had value for 2nd element, removed."))
			item[SEGMENT][2] = ""

		if (item[SEGMENT][4] != "1"):
			logs.append((index, f"HL Billing Provider Level 4th element was NOT set to 1. Updated."))
			item[SEGMENT][4] = "1"

	if (item[SEGMENT][0] == "HL" and item[SEGMENT][3] == "22"):
		if (item[SEGMENT][2] != "1"):
			logs.append((index, f"HL Subscriber Level 2nd element was NOT set to 1, updated."))
			item[SEGMENT][2] = "1"

		if (item[SEGMENT][4] != "0"):
			logs.append((index, f"HL Subscriber Level 4th element was NOT set to 0. Updated."))
			item[SEGMENT][4] = "0"


	return item

def main():
	args = sys.argv
	check_errors(args)

	filename, (fname_without_ext, ext) = args[1], os.path.splitext(args[1])
	with open(filename) as f:
		lines = f.readlines()

	data = parse_edi_to_array(lines)	

	# data format: [ {0}, {1}, {2}, {}, ... ]
	# {n}: START: All the whitespace at the start of segment
	#	   SEGMENT: The actual segment in the form of an array of it's parts
	#      END: The end string of the segment ("~\n\r")
	#
	# Example: data[2][SEGMENT]: ["SE", "102102", "AB201"]
	# Example: data[0][SEGMENT][0]: "ISA"
	#               ^     ^     ^
	#     line number  segment part-of-segment

	# ------------ Modify `data` to be written -------------------

	# 4-tuple (index, start, segment, end)
	additions = []

	for index, item in enumerate(data):
		segment: list[str] = item[SEGMENT]

		if (len(segment) == 0):
			# Empty line here
			continue

		if segment[0].startswith("//"):
			# Comment segment
			continue

		item = handle_segment_count(item, index)
		item = handle_claim_sum(item, index)
		item = handle_hl_tags(item, index)

		loop_item = loopinfo.check_loop_start(loopinfo.LOOP_INFO, segment)

		# Current item is loop and has not already been documented in the previous line
		if (loop_item is not None and not data[index-1][SEGMENT][0].startswith(f"// {FILE_MARKER}")):
			additions.append(
				(index, "\n", f"// {FILE_MARKER} Loop: {loop_item.name} :: {loop_item.desc}", "\n")
			)

		data[index] = item

	for addition in reversed(additions):
		data.insert(addition[0], {
			START: addition[1],
			SEGMENT: [addition[2],],
			END: addition[3]
		})

	# ------------------------------------------------------------

	new_lines = edi_array_to_lines(data)
	with open(f"{fname_without_ext}-withloops{ext}", 'w') as f:
		f.writelines(new_lines)


	max_comment = 0
	for _, comment in logs:
		if (len(comment)) > max_comment:
			max_comment = len(comment)

	max_comment += 2

	for item in logs:
		print(f"{item[1]}: {'.' * (max_comment - len(item[1]))} {bc.WARNING}{item[0]}{bc.ENDC}")


if __name__ == "__main__":
	main()
