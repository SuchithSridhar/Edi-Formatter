class bc:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class LoopObject():
	def __init__(self,
			  name: str,
			  start: list,
			  end: list,
			  situational: list,
			  desc: str,
			  repeat: int,
			  required: bool,
			  parent
		) -> None:

		self.name = name
		self.start = start
		self.end = end
		self.situational = situational
		self.desc = desc
		self.repeat = repeat
		self.required = required
		self.parent = parent

	def print_str(self) -> str:

		string = f"{bc.OKGREEN}{self.name}{bc.ENDC} :: start: {bc.OKCYAN}{self.start}{bc.ENDC}, end: {bc.OKCYAN}{self.end}{bc.ENDC}, sit: {bc.OKCYAN}{self.situational}{bc.ENDC}\n" \
				f"desc: {self.desc}\n" \
				f"repeat: {self.repeat}, req: {bc.WARNING}{self.required}{bc.ENDC}"

		if self.parent is None:
			string += ", parent: None\n"
		else:
			string += f", parent: {bc.OKBLUE}{self.parent.name}{bc.ENDC}\n"

		return string


# This code means that this part of the segment
# should increment according to count of segments 
COUNTER = 101

# Used to identify >1 loop repeat
INF = 0


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
				flag = flag and (possible_start[i] == segment[i] or possible_start[i] == "*")

			if flag:
				return loop

	return None


LOOP_INFO = [
#           name,     start,           end,    situ,      desc,     repeat, required, parent
LoopObject("1000A",  [("NM1", "41")], [("PER",)], [], "Submitter Name", 1, True, None),
LoopObject("1000B",  [("NM1", "40")], [], [], "Receiver Name", 1, True, None),

LoopObject("2000A",  [("HL", "*", "*","20")], [], [("PRV",), ("CUR",)], "Provider Hierarchical Level", 1, True, None),
LoopObject("2010AA", [("NM1", "85")], [("REF",)], [("PER",)], "Billing Provider Name", 1, True, "2000A"),
LoopObject("2010AB", [("NM1", "87")], [("REF",)], [], "Pay to address name", 1, False, "2000A"),
LoopObject("2010AC", [("NM1", "PE")], [("REF",), ("REF",)], [], "Pay to plan name", 1, False, "2000A"),

LoopObject("2000B",  [("HL", "*", "*","22")], [("SBR",)], [], "Subscriber Hierarchial Level", INF, True, None),
LoopObject("2010BA", [("NM1", "IL")], [("REF",), ("REF",)], [], "Subscriber Name", 1, True, "2000B"),
LoopObject("2010BB-1", [("NM1", "AO")], [("REF",)], [], "Account Holder Name", 1, True, "2000B"),
LoopObject("2010BB-2", [("NM1", "PR")], [("REF",), ("REF",)], [], "Payer Name", 1, True, "2000B"),
LoopObject("2010BD", [("NM1", "QD")], [("N3",), ("N4",)], [], "Responsible Party Name", 1, False, "2000B"),

LoopObject("2000C", [("HL", "*", "*","23")], [("N3",), ("N4",)], [], "Patient Hierarchical Level", 1, False, None),
LoopObject("2010CA", [("NM1", "QC")], [], [], "Patient Name", 1, False, "2000C"),
LoopObject("2300", [("CLM",)], [], [], "Claim Information", 1, True, "2000C"),
LoopObject("2310A", [("NM1","71")], [], [], "Attending Provider", 1, False, "2300"),
LoopObject("2310A", [("NM1","72")], [], [], "Operating Physician", 1, False, "2300"),
LoopObject("2310D", [("NM1","82")], [], [], "Rendering Provider", 1, False, "2300"),
LoopObject("2310E", [("NM1","77")], [], [], "Service Location", 1, False, "2300"),
LoopObject("2310F", [("NM1","DN")], [], [], "Referring Provider", 1, False, "2300"),
LoopObject("2320", [("SBR","S")], [], [], "Other Subscriber Info", 1, False, "2300"),
LoopObject("2330A", [("NM1","IL")], [], [], "Other Subscriber Name", 1, False, "2320"),
LoopObject("2400", [("LX",)], [], [], "Service Line", 1, False, "2300"),
LoopObject("2410", [("LIN",)], [], [], "Drug Information", 1, False, "2400"),
LoopObject("2430", [("SVD",)], [], [], "Line Adjudication Info", 1, False, "2400"),
]

set_parent(LOOP_INFO)















