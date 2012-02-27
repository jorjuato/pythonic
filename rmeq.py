# Python script uses R to compute two-way ANOVA and paired T-tests.
#
# Data file must be in default format preferred by R, with columns labeled in the first line of the
# file, and rows labeled by incrementing case number, for example...
# 		FIELD1	FIELD2
# 1	0.900		0.09
# 2	0.890		0.11
#
# OPEN ISSUES:
# 1. We need to determine what type of authorship/copyright notice to put here.

# import sys and check arguments...
import sys
if len(sys.argv) not in (7,8) or sys.argv[6] not in ('min', 'max') or (len(sys.argv) == 8 and sys.argv[7] != 'rank'):
	sys.stderr.write("\nusage:%s <data-file> <system-label-field-name> <test-case-field-name> <score-field-name> <alpha> <min|max> rank?\n" % sys.argv[0])
	sys.stderr.write("  Where:\n")
	sys.stderr.write("  min - the best system is the minimum sum of the test case scores.\n")
	sys.stderr.write("  max - the best system is the maximum sum of the test case scores.\n")
	sys.stderr.write("  rank - perform a rank transformation of the data before processing,")	
	sys.stderr.write("  			 where low to high score is mapped to low to high rank.")	
	sys.exit(0)

# try to import RPy library and catch error if not available...
try:
	import rpy
	from rpy import r
except:
	sys.stderr.write("\nERROR: Unable to import RPy!\n")
	sys.stderr.write("This script requires that R and RPy both be installed.\n")
	sys.stderr.write("R is available at: http://www.r-project.org\n")
	sys.stderr.write("RPy is available at: http://rpy.sourceforge.net\n")
	sys.exit(0)
	
# utility function...
def convert_r_dataframe_to_python_nested_dict(dataframe):
	rownames = r.row_names(dataframe).as_py(rpy.BASIC_CONVERSION)
	dataframe = dataframe.as_py(rpy.BASIC_CONVERSION)
	pythonframe = {}
	for key in dataframe:
		pythonframe[key] = {}
		for (subkey, value) in zip(rownames, dataframe[key]):
			pythonframe[key][subkey] = value
	return pythonframe

# store command-line arguments...
data_filename = sys.argv[1]
run_label_fieldname = sys.argv[2]
measure_label_fieldname = sys.argv[3]
score_fieldname = sys.argv[4]
alpha = float(sys.argv[5])
if sys.argv[6] == 'min':
	minOrMax = min
elif sys.argv[6] == 'max':
	minOrMax = max
	
# no data conversion by default for Rpy...
rpy.set_default_mode(rpy.NO_CONVERSION)

# load data table...
table = r.read_table(data_filename)

# perform rank conversion if requested...
if len(sys.argv) == 8 and sys.argv[7] == 'rank':
	# all measure labels...
	labels = table.as_py(rpy.BASIC_CONVERSION)[measure_label_fieldname]
	# build a replacement score vector large enough to hold all the scores
	scores = [None] * len(labels)
	# grab all the repeated measure names...
	measures = set(labels)
	# loop over the measures, replacing with ranks...
	for measure in measures:
		# select out scores for this measure...
		flags = [t == measure for t in table.as_py(rpy.BASIC_CONVERSION)[measure_label_fieldname]]
		# rank the scores...
		ranks = r.rank(r.subset(r['$'](table, score_fieldname), flags), 'average').as_py(rpy.BASIC_CONVERSION)
		# replace the scores for this measure by the ranks...
		indexes = [index for (index, flag) in zip(range(len(flags)), flags) if flag]
		for (index, rank) in zip(indexes, ranks):
			scores[index] = rank
	# create a new data table that has the original scores replaced by ranks...
	table = r['$<-'](table, score_fieldname, scores)

# grab all the run names...
names = set(table.as_py(rpy.BASIC_CONVERSION)[run_label_fieldname])

# loop over set of names...
equivalent_groups = []
equivalent_group_heads = []
equivalent_group_ties = []
while len(names) > 1:
	# select out runs with labels in set of names...
	flags = [t in names for t in table.as_py(rpy.BASIC_CONVERSION)[run_label_fieldname]]
	subtable = r.subset(table, flags)
	# perform two-way ANOVA with run-label-field-name as a fixed factor and measure-field-name as a random factor...
	model = "%s ~ %s + %s" % (score_fieldname, measure_label_fieldname, run_label_fieldname)
	linear_model = r.lm(r(model), data = subtable)
	anv = r.anova(linear_model)
	pdx = convert_r_dataframe_to_python_nested_dict(r.as_data_frame(anv))
	pvalue = pdx['Pr(>F)'][run_label_fieldname]
	if pvalue >= alpha:
		# if not significant, then stop...
		break
	# if significant, take the top scoring run of the group...
	score_sums = {}
	for (run, score) in zip(table.as_py(rpy.BASIC_CONVERSION)[run_label_fieldname], table.as_py(rpy.BASIC_CONVERSION)[score_fieldname]):
		# only include runs in the current set of names...
		if run in names:
			score_sums[run] = score_sums.get(run, 0.0) + score
	(top_score, top_run) = minOrMax([(score_sums[run], run) for run in score_sums])
	# error check to detect ties for top runs...
	ties = [run for run in score_sums if score_sums[run] == top_score]	
	if len(ties) > 1:
		ties.sort()
		sys.stderr.write("\nWarning, tie between best %s in equivalent group %d.\n" %  (run_label_fieldname, len(equivalent_groups)+1))
		sys.stderr.write("Select best group:\n")
		for (index, label) in zip(range(1, 1+len(ties)), ties):			
			sys.stderr.write("%d. %s\n" % (index, label))
		choice = None
		while not choice:
			sys.stderr.write("Please choose 1 through %d =>" % len(ties))
			try:
				choice = int(sys.stdin.readline())
			except:
				choice = None
			if choice < 1 or choice > len(ties):
				choice = None
		sys.stderr.write("\n")
		# set the top run to the chosen run...
		top_run = ties[choice - 1]	
		equivalent_group_ties.append(ties)				
	else:
		equivalent_group_ties.append(None)		
	# compute pairwise significant differences against the top run...
	pairwise = []
	aflags = [x == top_run for x in table.as_py(rpy.BASIC_CONVERSION)[run_label_fieldname]]
	asubset = r.subset(r['$'](table, score_fieldname), aflags)	
	for run in names:
		if run == top_run:
			# don't compare run to itself...
			continue
		else:
			# compute paired t-test against current top run...
			bflags = [x == run for x in table.as_py(rpy.BASIC_CONVERSION)[run_label_fieldname]]
			bsubset = r.subset(r['$'](table, score_fieldname), bflags)	
			try:
				t = r.t_test(asubset, bsubset, paired=True)
				t = t.as_py(rpy.BASIC_CONVERSION)
			except:
				# traps some arithmetic errors...
				t = {'p.value': 1.0}
			# extract the p-value of the paired t-test...
			pvalue = t['p.value']
			# check for other arithmetic errors, usually these are runs with identical values and therefore zero squared differences...
			# this is a bit of a nightmare, since this is platform specific and the number was computed by R and just passed back to
			# Python. Special values usually compare False to everything, so we can check for inconsistent behavior as well as matching
			# to string representations...
			if (not pvalue < 0.0 and not pvalue > 0.0 and not pvalue == 0.0) or str(pvalue) in ("-1.#IND", "+1.#IND", "+1.#INF", "-1.#INF"):
				pvalue = 1.0
			pairwise.append((pvalue, run))
	# separate the group of non-signficant differences using linear step up procedure to perform FDR at the given alpha...
	acceptNull = []
	rejectNull = []
	reject = False
	for ((pvalue, run), rank) in reversed(zip(sorted(pairwise), range(1, len(pairwise)+1))):
		if not reject:
			if pvalue < (alpha * rank) / len(pairwise):
				reject = True
		if reject:
			rejectNull.append(run)
		else:
			acceptNull.append(run)
	# save the current equivalent group...
	equivalent_group_heads.append(top_run)
	equivalent_groups.append(tuple(sorted(acceptNull + [top_run])))
	# further subdivide the statistically different group...
	names = rejectNull
# done with loop, anything left goes into a separate group...
if names:
	equivalent_group_heads.append("None")
	equivalent_groups.append(tuple(sorted(names)))
	equivalent_group_ties.append(None)		
# display the system equivalent groups...
sys.stdout.write("\n")
for (head, ties, group, rank) in zip(equivalent_group_heads, equivalent_group_ties, equivalent_groups, range(1, len(equivalent_groups)+1)):
	if ties:
		sys.stdout.write("RANK GROUP %d (chose %s from %s): %s\n" % (rank, head, str(ties), str(group)))
	else:
		sys.stdout.write("RANK GROUP %d (top = %s): %s\n" % (rank, head, str(group)))

