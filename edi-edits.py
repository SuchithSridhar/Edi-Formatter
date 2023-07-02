#!/usr/bin/python3
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
# A program to identify loops, fix-errors,
# clean edi / X12 files.
# =============================================================

import os
import sys
from random import randint

# Separator for segment parts
DELIMITER = "*"

# Terminates a segment
TERMINATOR = "~"

WHITESPACE = " \t\n\r"
COMMENT = "//"
NEWLINE = "\n"
INDENT_STR = "\t"

# Just used for internal purposes
START = "start"
END = "end"
SEGMENT = "segment"

FILE_MARKER = "SSEDI"


class bc:
    '''Class to just keep of terminal colors.'''

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


help_msg = f'''
edi-edits.py: A utility program for edi files.
Author: Suchith Sridhar

Help:
    Call the program in the following way.

    {bc.OKGREEN}
    $ python edi-edits.py [operator-flags] [options-flags] <filename>.edi
    {bc.ENDC}

    Operations:
        {bc.OKCYAN}-id-loops{bc.ENDC} : Identify loops in the EDI file by placing "comments".

        {bc.OKCYAN}-fix-errors{bc.ENDC} : Fix basic errors such as count mistakes and unique ids.
                       (further options mentioned below)

        {bc.OKCYAN}-format{bc.ENDC} : Format the file by removing "comments" and whitespaces.

    Options:
        (new files are created by default)
        {bc.OKCYAN}-i{bc.ENDC} : (in-place) rewrite the input file and do not create a new one.
        {bc.OKCYAN}-o{bc.ENDC} <filename> : write the output to this specific file.

    Fix Error Options (only applies for -fix-errors):
        {bc.OKCYAN}-gen-uuid{bc.ENDC} : generate unique ID's for ST and SE control numbers.
        {bc.OKCYAN}-claim-amount{bc.ENDC} : Validate the total claim amount.
        {bc.OKCYAN}-hl-num{bc.ENDC} : Number the HL segments according to their occurance order.

        {bc.OKCYAN}-hl-logic-off{bc.ENDC} : Don't fix HL segment logic (on by default).
        {bc.OKCYAN}-seg-count-off{bc.ENDC} : Don't update segment count (on by default).
'''

OPT_ID_LOOPS = '-id-loops'
OPT_FIX_ERRORS = '-fix-errors'
OPT_FORMAT = '-format'
OPT_INPLACE = '-i'
OPT_OUT_FILE = '-o'
OPT_GEN_UUID = '-gen-uuid'
OPT_HL_NUM = '-hl-num'
OPT_CLM_AMT = '-claim-amount'
OPT_HL_LOGIC = '-hl-logic-off'
OPT_SEG_COUNT = '-seg-count-off'
OPT_INPUT_FILE = 'input-file'

LOG_WARN = 'warn'
LOG_ERROR = 'error'
LOG_INFO = 'info'
LOG_SUCC = 'success'

logs = []


def print_help():
    print(help_msg)


def print_log(msg: str, level: str):
    mapping = {
        'warn': bc.WARNING,
        'error': bc.FAIL,
        'info': bc.ENDC,
        'success': bc.OKGREEN
    }

    color = mapping.get(level, bc.ENDC)
    print(color+msg+bc.ENDC)


class LoopObject():

    def __init__(self, name: str, start: list, end: list, situational: list,
                 desc: str, repeat: int, required: bool, parent) -> None:

        self.name = name
        self.start = start
        self.end = end
        self.situational = situational
        self.desc = desc
        self.repeat = repeat
        self.required = required
        self.parent = parent

    def print_str(self) -> str:

        string = f"{bc.OKGREEN}{self.name}{bc.ENDC} :: start: " \
                 f"{bc.OKCYAN}{self.start}{bc.ENDC}, end: " \
                 f"{bc.OKCYAN}{self.end}{bc.ENDC}, sit: " \
                 f"{bc.OKCYAN}{self.situational}{bc.ENDC}\n" \
                 f"desc: {self.desc}\n" \
                 f"repeat: {self.repeat}, req: " \
                 f"{bc.WARNING}{self.required}{bc.ENDC}"

        if self.parent is None:
            string += ", parent: None\n"
        else:
            string += f", parent: {bc.OKBLUE}{self.parent.name}{bc.ENDC}\n"

        return string


def get_parent_loop(items, name):
    '''Find the parent object from the name of the loop.'''

    for item in items:
        if name == item.name:
            return item
    return None


def set_parent(loops):
    '''Update the string parent name to the parent object.'''
    for loop in loops:
        if loop.parent is not None and isinstance(loop.parent, str):
            loop.parent = get_parent_loop(loops, loop.parent)


def check_loop_start(loops: list[LoopObject], segment) -> None | LoopObject:
    for loop in loops:
        for possible_start in loop.start:
            flag = True
            for i in range(len(possible_start)):
                flag = (flag and
                        (possible_start[i] == segment[i]
                         or possible_start[i] == "*"))

            if flag:
                return loop

    return None


LOOP_INFO = [
    # name, start, end, situ, desc, repeat, required, parent
    LoopObject(
        "1000A",  [("NM1", "41")], [("PER",)], [], "Submitter Name", 1,
        True, None
    ),
    LoopObject(
        "1000B",  [("NM1", "40")], [], [], "Receiver Name",
        1, True, None
    ),
    LoopObject(
        "2000A",  [("HL", "*", "*", "20")], [], [("PRV",), ("CUR",)],
        "Provider Hierarchical Level", 1, True, None
    ),
    LoopObject(
        "2010AA", [("NM1", "85")], [("REF",)], [("PER",)],
        "Billing Provider Name", 1, True, "2000A"
    ),
    LoopObject(
        "2010AB", [("NM1", "87")], [("REF",)], [],
        "Pay to address name", 1, False, "2000A"
    ),
    LoopObject(
        "2010AC", [("NM1", "PE")], [("REF",), ("REF",)], [],
        "Pay to plan name", 1, False, "2000A"
    ),

    LoopObject(
        "2000B",  [("HL", "*", "*", "22")], [("SBR",)], [],
        "Subscriber Hierarchial Level", -1, True, None
    ),
    LoopObject(
        "2010BA", [("NM1", "IL")], [("REF",), ("REF",)], [],
        "Subscriber Name", 1, True, "2000B"
    ),
    LoopObject(
        "2010BB-1", [("NM1", "AO")], [("REF",)], [],
        "Account Holder Name", 1, True, "2000B"
    ),
    LoopObject(
        "2010BB-2", [("NM1", "PR")], [("REF",), ("REF",)], [],
        "Payer Name", 1, True, "2000B"
    ),
    LoopObject(
        "2010BD", [("NM1", "QD")], [("N3",), ("N4",)], [],
        "Responsible Party Name", 1, False, "2000B"
    ),

    LoopObject(
        "2000C", [("HL", "*", "*", "23")], [("N3",), ("N4",)], [],
        "Patient Hierarchical Level", 1, False, None
    ),
    LoopObject(
            "2010CA", [("NM1", "QC")], [], [],
            "Patient Name", 1, False, "2000C"
    ),
    LoopObject(
            "2300", [("CLM",)], [], [],
            "Claim Information", 1, True, "2000C"
    ),
    LoopObject(
            "2310A", [("NM1", "71")], [], [],
            "Attending Provider", 1, False, "2300"
    ),
    LoopObject(
            "2310A", [("NM1", "72")], [], [],
            "Operating Physician", 1, False, "2300"
    ),
    LoopObject(
            "2310D", [("NM1", "82")], [], [],
            "Rendering Provider", 1, False, "2300"
    ),
    LoopObject(
            "2310E", [("NM1", "77")], [], [],
            "Service Location", 1, False, "2300"
    ),
    LoopObject(
            "2310F", [("NM1", "DN")], [], [],
            "Referring Provider", 1, False, "2300"
    ),
    LoopObject(
            "2320", [("SBR", "S")], [], [],
            "Other Subscriber Info", 1, False, "2300"
    ),
    LoopObject(
            "2330A", [("NM1", "IL")], [], [],
            "Other Subscriber Name", 1, False, "2320"
    ),
    LoopObject(
            "2400", [("LX",)], [], [],
            "Service Line", 1, False, "2300"
    ),
    LoopObject(
            "2410", [("LIN",)], [], [],
            "Drug Information", 1, False, "2400"
    ),
    LoopObject(
            "2430", [("SVD",)], [], [],
            "Line Adjudication Info", 1, False, "2400"
    ),
]


def find_non_whitespace_character(string: str):
    for index, char in enumerate(string):
        if char not in WHITESPACE:
            return index

    # For empty lines
    raise ValueError("non-whitespace character not found.")


def parse_edi_to_array(lines: list[str]):
    # Example line: "\t\t SE*1393*3013~\n\r"
    data = []
    for line in lines:
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
                if (NEWLINE in line):
                    index_tilda = line.index(NEWLINE)
                else:
                    index_tilda = len(line)-1
            else:
                if (COMMENT in line):
                    index_tilda = line.index(COMMENT)
                else:
                    if (NEWLINE in line):
                        index_tilda = line.index(NEWLINE)
                    else:
                        index_tilda = len(line)-1

        parts = {
            START: line[:index_start],
            SEGMENT: line[index_start:index_tilda].split(DELIMITER),
            END: line[index_tilda:]
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


class SegmentCounter:
    counting = False
    count = 0
    start = 0


def handle_segment_count(item, index):
    if (item[SEGMENT][0] == "ST"):
        if (SegmentCounter.counting):
            print(f"Recieved ST 2x in a row at {SegmentCounter.start + 1}"
                  f" and {index + 1}. Exiting.")
            exit(1)

        SegmentCounter.counting = True
        SegmentCounter.start = index
        SegmentCounter.count = 0

    if (SegmentCounter.counting):
        SegmentCounter.count += 1

    if (item[SEGMENT][0] == "SE"):
        if (not SegmentCounter.counting):
            print(f"Recieved SE before ST at {index + 1}. Exiting.")
            exit(1)

        count = int(item[SEGMENT][1])
        if (count != SegmentCounter.count):
            logs.append((index, f"Segment Count for SE mismatch, "
                                f"updating to {SegmentCounter.count}"))
            item[SEGMENT][1] = str(SegmentCounter.count)

        SegmentCounter.counting = False

    return item


class SegmentIDTracker:
    generated_id = 0


def handle_segment_uuid(item, index):

    if (item[SEGMENT][0] == "ST"):
        # Random 9 digit number
        SegmentIDTracker.generated_id = randint(10**8, 10**9 - 1)
        item[SEGMENT][2] = str(SegmentIDTracker.generated_id)

    if (item[SEGMENT][0] == "SE"):
        item[SEGMENT][2] = str(SegmentIDTracker.generated_id)

    return item


class ClaimAmountCheck:
    clm_pos = 0
    clm_total = 0.0
    sv2_sum = 0.0
    sv2_pos = []
    active = False


def handle_claim_sum(item, index):
    if (item[SEGMENT][0] == "CLM"):
        if (ClaimAmountCheck.active):
            print(f"Recieved two CLMs in a row at "
                  f"{ClaimAmountCheck.clm_pos+1} and {index+1}. Exiting.")
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
            print(f"{bc.FAIL}CLM total mismatch. SV2 total: "
                  f"{ClaimAmountCheck.sv2_sum}, CLM total: "
                  f"{ClaimAmountCheck.clm_total}{bc.ENDC}")
            print(f"\t SV2 segments lines: {ClaimAmountCheck.sv2_pos} "
                  f"and CLM segment line: {ClaimAmountCheck.clm_pos}")

        ClaimAmountCheck.active = False

    return item


class HLNumber:
    counter = 1


def handle_hl_num(item, index):
    if (item[SEGMENT][0] == "SE"):
        HLNumber.counter = 1

    if (item[SEGMENT][0] == "HL"):
        item[SEGMENT][1] = str(HLNumber.counter)
        HLNumber.counter += 1

        if (len(item[SEGMENT]) != 5):
            item[SEGMENT] = item[SEGMENT].insert(2, "")

    return item


def handle_hl_logic(item, index):
    if (item[SEGMENT][0] == "HL" and item[SEGMENT][3] == "20"):
        if (item[SEGMENT][2] != ""):
            logs.append((index, "HL Billing Provider Level had value "
                                "for 2nd element, removed."))
            item[SEGMENT][2] = ""

        if (item[SEGMENT][4] != "1"):
            logs.append((index, "HL Billing Provider Level 4th element "
                                "was NOT set to 1. Updated."))
            item[SEGMENT][4] = "1"

    if (item[SEGMENT][0] == "HL" and item[SEGMENT][3] == "22"):
        if (item[SEGMENT][2] != "1"):
            logs.append((index, "HL Subscriber Level 2nd element was "
                                "NOT set to 1, updated."))
            item[SEGMENT][2] = "1"

        if (item[SEGMENT][4] != "0"):
            logs.append((index, "HL Subscriber Level 4th element was "
                                "NOT set to 0. Updated."))
            item[SEGMENT][4] = "0"

    return item


def parse_arguments(args: list[str]):
    opts = {
        OPT_ID_LOOPS: False,
        OPT_FIX_ERRORS: False,
        OPT_FORMAT: False,
        OPT_INPLACE: False,
        OPT_OUT_FILE: "",
        OPT_GEN_UUID: False,
        OPT_HL_NUM: False,
        OPT_CLM_AMT: False,

        # Note that the string may have contridictor name
        # This being true imples we perform HL logic.
        OPT_HL_LOGIC: True,
        OPT_SEG_COUNT: True,

        OPT_INPUT_FILE: ""
    }

    recieved_flags = []

    for key in opts:
        if key in args and key not in recieved_flags:
            recieved_flags.append(key)

            if key == OPT_OUT_FILE:
                index = args.index(key)
                outfile = args[index+1]

                if (outfile in opts):
                    print_log(
                        "ERROR: Please provide an "
                        f"output file with {OPT_OUT_FILE}.",
                        LOG_ERROR
                    )
                    sys.exit(1)

                opts[OPT_OUT_FILE] = outfile
                args.pop(index+1)
                args.pop(index)

            else:
                args.remove(key)
                opts[key] = not opts[key]

        elif key in recieved_flags:
            print_log(f"Recieved {key} twice. Ignoring.", LOG_WARN)
            continue

    if (OPT_INPLACE in recieved_flags and OPT_OUT_FILE in recieved_flags):
        print_log("Recieved both -i and -o. Not valid arguments. Exiting.",
                  LOG_ERROR)

    if len(args) != 2:
        print_log("Improper number of arguments.", LOG_ERROR)
        sys.exit(1)

    input_file = args[1]
    if (not os.path.isfile(input_file)):
        print_log(f"Unable to find file {input_file}. Exiting", LOG_ERROR)
        sys.exit(1)

    opts[OPT_INPUT_FILE] = input_file
    fname_without_ext, ext = os.path.splitext(input_file)

    if (opts[OPT_INPLACE]):
        opts[OPT_OUT_FILE] = input_file

    if (opts[OPT_OUT_FILE] == ""):
        if (opts[OPT_FORMAT]):
            opts[OPT_OUT_FILE] = f"{fname_without_ext}-formatted{ext}"

        elif (opts[OPT_ID_LOOPS]):
            opts[OPT_OUT_FILE] = f"{fname_without_ext}-withloops{ext}"

        elif (opts[OPT_FIX_ERRORS]):
            opts[OPT_OUT_FILE] = f"{fname_without_ext}-fixed{ext}"

    if (not opts[OPT_FIX_ERRORS]
            and not opts[OPT_ID_LOOPS]
            and not opts[OPT_FORMAT]):

        print_log("No operation was selected. Exiting.", LOG_WARN)
        sys.exit(1)

    return opts


def print_opts(opts: dict):
    print("The following options have been set:")
    print(f"\tInput File :: {bc.OKGREEN}{opts[OPT_INPUT_FILE]}{bc.ENDC}")
    print(f"\tOutput File :: {bc.OKGREEN}{opts[OPT_OUT_FILE]}{bc.ENDC}")

    rest_of_opts = [OPT_FORMAT, OPT_ID_LOOPS, OPT_FIX_ERRORS,
                    OPT_GEN_UUID, OPT_HL_NUM, OPT_HL_LOGIC, OPT_SEG_COUNT]

    for key in rest_of_opts:
        value = opts[key]
        off_value = key.endswith("off")
        if (value and not off_value):
            print(f"\t{key} :: {bc.OKGREEN}{value}{bc.ENDC}")
        elif (not value and off_value):
            print(f"\t{key} :: {bc.OKGREEN}{not value}{bc.ENDC}")

    if opts[OPT_ID_LOOPS] and opts[OPT_FORMAT]:
        print("You really want me to ID loops AND format the file??")
        print("Format would remove all the loop comments...")


def fix_errors_module(index, item, opts, additions, deletions):

    if (opts[OPT_SEG_COUNT]):
        item = handle_segment_count(item, index)

    if (opts[OPT_GEN_UUID]):
        item = handle_segment_uuid(item, index)

    if (opts[OPT_CLM_AMT]):
        item = handle_claim_sum(item, index)

    if (opts[OPT_HL_NUM]):
        item = handle_hl_num(item, index)

    if (opts[OPT_HL_LOGIC]):
        item = handle_hl_logic(item, index)

    return item


class IdLoopsState:
    loop_line = ""
    item_ref = {}


def id_loops_module(index, item: dict, opts, additions, deletions):

    segment: list[str] = item[SEGMENT]

    if (len(segment) == 0):
        return item

    if segment[0].startswith("//"):
        return item

    if (segment[0].startswith(f"// {FILE_MARKER}")):
        IdLoopsState.loop_line = segment[0]
        IdLoopsState.item_ref = item
        return item

    loop = check_loop_start(LOOP_INFO, segment)

    if (loop is not None):
        marker = f"// {FILE_MARKER} Loop: {loop.name} :: {loop.desc}"

        # Out-dated marker present
        if (IdLoopsState.loop_line != "" and IdLoopsState.loop_line != marker):
            IdLoopsState.item_ref[SEGMENT][0] = marker

        # Marker not present
        if (IdLoopsState.loop_line == ""):
            additions.append((index, "\n", marker, "\n"))

    return item


def format_module(index, item, opts, additions, deletions):

    segment = item[SEGMENT]

    if (len(segment) == 0):
        logs.append((index+1, "Removed empty line."))
        deletions.append(index)
        return item

    if segment[0].startswith("//"):
        logs.append((index+1, "Removed comment line."))
        deletions.append(index)
        return item

    if (item[START] != ""):
        item[START] = ""
        logs.append((index+1, "Removed whitespace from start."))

    if (item[END][0] != TERMINATOR):
        item[END] = TERMINATOR + item[END]
        logs.append((index+1, "Added missing terminator."))

    if (NEWLINE in item[END] and item[END].index(NEWLINE) != 1):
        # There isn't a newline right after ~
        item[END] = TERMINATOR + NEWLINE
        logs.append((index+1, "Removed character after terminator."))

    return item


def main():
    args = sys.argv

    if ("-help" in args or "--help" in args or len(args) == 1):
        print_help()
        exit(0)

    opts = parse_arguments(args)
    print()
    print_opts(opts)

    if opts[OPT_ID_LOOPS] and opts[OPT_FORMAT]:
        opts[OPT_ID_LOOPS] = False

    choice = ""
    while (choice.lower() != "y" and choice.lower() != "n"):
        print()
        choice = input("Continue with the above configuration? (Y/N): ")
        print()

    if (choice == "n"):
        print_log("Aborted.", LOG_ERROR)
        sys.exit(1)

    with open(opts[OPT_INPUT_FILE]) as f:
        lines = f.readlines()

    data = parse_edi_to_array(lines)

    # data format: [ {0}, {1}, {2}, {}, ... ]
    # {n}: START: All the whitespace at the start of segment
    #      SEGMENT: The actual segment in the form of an array of it's parts
    #      END: The end string of the segment ("~\n\r")
    #
    # Example: data[2][SEGMENT]: ["SE", "102102", "AB201"]
    # Example: data[0][SEGMENT][0]: "ISA"
    #               ^     ^     ^
    #     line number  segment part-of-segment

    # ------------ Modify `data` to be written -------------------

    # 4-tuple (index, start, segment, end)
    additions: list[tuple] = []

    # Indices of the items to be deleted
    deletions: list[int] = []

    for index, item in enumerate(data):

        if (opts[OPT_FIX_ERRORS]):
            item = fix_errors_module(index, item, opts, additions, deletions)

        if (opts[OPT_ID_LOOPS]):
            item = id_loops_module(index, item, opts, additions, deletions)

        if (opts[OPT_FORMAT]):
            item = format_module(index, item, opts, additions, deletions)

    for index in reversed(deletions):
        data.remove(index)

    offset = len(deletions)

    for addition in reversed(additions):
        data.insert(addition[0] - offset, {
            START: addition[1],
            SEGMENT: [addition[2],],
            END: addition[3]
        })

    # ------------------------------------------------------------

    new_lines = edi_array_to_lines(data)
    with open(opts[OPT_OUT_FILE], 'w') as f:
        f.writelines(new_lines)

    max_comment = 0
    for _, comment in logs:
        if (len(comment)) > max_comment:
            max_comment = len(comment)

    max_comment += 2

    for item in logs:
        print(f"{item[1]}: {'.' * (max_comment - len(item[1]))}"
              f"{bc.WARNING}{item[0]}{bc.ENDC}")


if __name__ == "__main__":
    main()
