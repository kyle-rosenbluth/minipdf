import sys
import subprocess
import os

# cf_old = open(sys.argv[1], "a")
# cf_old.write("\n")
# cf_old.close()

crossword_file = open(sys.argv[1]).read()
mini_number = sys.argv[2]
tex_header = open("tex_header.txt").read()
tex_header_solved = open("tex_header_solved.txt").read()
tex_header = tex_header.replace("\\textsf{\\textbf{\\huge{Mini Meta}}}", "\\textsf{\\textbf{\\huge{Mini Meta " + mini_number + "}}}")
tex_header_solved = tex_header_solved.replace("\\textsf{\\textbf{\\huge{Mini Meta Solution}}}", "\\textsf{\\textbf{\\huge{Mini Meta " + mini_number + " Solution}}}")


# Indeces variables indicate what #value to label the tiles. It does not offer any insight on to which tiles get the numbers, just what the tiles # values should be.
acrossIndeces = [[], [], [], [], [], []]
downIndeces = [[], [], [], [], [], []]

# acrossClueCount = [0] * 6
# downClueCount = [0] * 6

acrossClues = [[], [], [], [], [], []]
downClues = [[], [], [], [], [], []]
escapeChars = {"_": "\_", "&":"\&", "%": "\%", "$":"\$", "#":"\#", "{":"\{", "}":"\}", "~":"\\textasciitilde", "^":"\\textasciicircum", "\\":"\\textbackslash", """'""":"{\\myfont \\textquotesingle}"}
invertEscape  = {v: k for k, v in escapeChars.items()}
metaClueIndeces = None
metaSolutionIndeces = None
metaClues = []
metaSolution = []
saturday_solution_indeces = None
solution_indeces = []
saturday_solution = ""
solutions = ["", "", "", "", ""]
def generatePuzzle(solved):
    global solution_indeces
    global saturday_solution_indeces
    global saturday_solution
    section = 0
    unitLength = 25 if solved else 21
    gray_cell ="""\\cellcolor{gray!25}\n"""
    puzzle_start_pre_toprow = """\\renewcommand{\\PuzzleUnitlength}{""" + str(unitLength) + """pt}\n\\begin{minipage}[t][23em][t]{\colwidth}\n\\vspace{.25em}\n\\center{\\textsf{\\textbf{"""
    puzzle_start_pre_bottomrow = """\\renewcommand{\\PuzzleUnitlength}{""" + str(unitLength) + """pt}\n\\begin{minipage}[c][23em][t]{\colwidth}\n\\vspace{1em}\n\\center{\\textsf{\\textbf{"""
    puzzle_start_post = """}}}\\vspace{0.55em}\\\\\n\\begin{Puzzle}{5}{5}\n"""
    if (solved):
        puzzle_start_post = """}}}\\vspace{0.55em}\\\\\n\\PuzzleSolution\n\\Large\n\\begin{Puzzle}{5}{5}\n"""


    crosswords = [gray_cell + puzzle_start_pre_toprow + "MONDAY" + puzzle_start_post,
                puzzle_start_pre_toprow + "TUESDAY" + puzzle_start_post,
                gray_cell + puzzle_start_pre_toprow + "WEDNESDAY" + puzzle_start_post,
                puzzle_start_pre_bottomrow + "THURSDAY" + puzzle_start_post,
                gray_cell + puzzle_start_pre_bottomrow + "FRIDAY" + puzzle_start_post,
                puzzle_start_pre_bottomrow + "SATURDAY" + puzzle_start_post]
    col_num = [[0 for j in range(5)] for i in range(6)]
    row_num = [[0 for j in range(5)] for i in range(6)]

    # clueIndeces is a counter array to keep count for numbering tiles. It's ending value is garbage.
    clueIndeces = [0] * 6

    downCluesFlat = []
    acrossCount = 0
    boardIdx = 0
    row = 0
    col = 0
    level = 0
    puzzleText = []
    for line in iter(crossword_file.splitlines()):
        if (line == "\n" or line == ""):
            # Skip empty line
            continue
        elif (line == "Across"):
            # Begin parsing across clues for all puzzles.
            section = 1
            continue
        elif line == "Down":
            # Begin parsing down clues for all puzzles
            section = 2
            continue
        elif line == "===":
            # Begin parsing meta solutions
            section = 3
            continue
        if section == 0:
            puzzleText.append(line)
        elif section == 1:
            # Across clues we can parse and place in one step. Down clues are a little tougher.
            num_clue = line.split(". ", 1)
            acrossCount += 1
            boardIdx = int(acrossCount / 5)
            if (acrossCount % 5 == 0):
                boardIdx -= 1
            acrossClues[col + level].append(num_clue[1].replace("\n", "").translate(str.maketrans(escapeChars)))
            col += 1
            if (col == 3):
                row += 1
                col = 0
            if (row == 5):
                level = 3
                row = 0
        elif section == 2:
            num_clue = line.split(". ", 1)
            downCluesFlat.append(num_clue[1].replace("\n", "").translate(str.maketrans(escapeChars)))
        elif section == 3:
            print("section 3")
            if not solution_indeces:
                solution_indeces = line.split(",")
            else:
                saturday_solution_indeces = eval("[" + line + "]")
    level = 0
    row = 0
    col = 0
    boardIdx = 0
    amuse_solutions = ["", "", "", "", "", ""]
    saturday_solution = "." * len(saturday_solution_indeces)
    for line in puzzleText:
        if (line == "................."):
            # Row of all black tiles means we've moved down to the Thu / Fri / Sat row
            level = 3
            row = 0
            col = 0
            continue
        boardIdx = level
        crosswords[boardIdx] += "|"
        squareIdx = -1
        for c in (line + "\n"):
            squareIdx += 1
            if (squareIdx > 0 and squareIdx % 5 == 0):
                # This means we've gone to a new board
                crosswords[boardIdx] += ".\n"
                amuse_solutions[boardIdx] += "\n"
                boardIdx += 1
                col = 0
                if boardIdx > 5 or boardIdx == 3:
                    continue
                crosswords[boardIdx] = crosswords[boardIdx] + "|"
                squareIdx = -1
                continue
            if (c == '.'):
                crosswords[boardIdx] += "* |"
                amuse_solutions[boardIdx] += "."
            else:
                solution_pre = ""
                if boardIdx < 5 and solved:
                    solIdx, isColSol = solution_indeces[boardIdx]
                    isColSol = True if isColSol == "a" else False
                    solIdx = int(solIdx)
                    if isColSol and row == solIdx:
                        solutions[boardIdx] += c
                        solution_pre = "[sf]"
                    elif (not isColSol) and col == solIdx:
                        solutions[boardIdx] += c
                        solution_pre = "[sf]"
                else:
                    if (col, row) in saturday_solution_indeces and solved:
                        index_of = saturday_solution_indeces.index((col, row))
                        saturday_solution = saturday_solution[:index_of] + c + saturday_solution[index_of + 1:]
                        if (index_of == 0):
                            next_idx = saturday_solution_indeces[index_of + 1]
                            if (next_idx[0] > col):
                                solution_pre = "[gH]"
                            elif next_idx[0] < col:
                                solution_pre = "[gh]"
                            elif next_idx[1] > row:
                                solution_pre = "[gv]"
                            else:
                                solution_pre = "[gV]"
                        elif index_of == len(saturday_solution_indeces) - 1:
                            prev_idx = saturday_solution_indeces[index_of - 1]
                            if (col > prev_idx[0]):
                                solution_pre = "[rh]"
                            elif col < prev_idx[0]:
                                solution_pre = "[rH]"
                            elif row > prev_idx[1]:
                                solution_pre = "[rV]"
                            else:
                                solution_pre = "[rv]"
                        else:
                            prev_idx = saturday_solution_indeces[index_of - 1]
                            next_idx = saturday_solution_indeces[index_of + 1]
                            if (prev_idx[0] < col):
                                #Horizontal In from left
                                if (next_idx[0] > col):
                                    #Horizontal line
                                    solution_pre = "[e]"
                                elif next_idx[1] > row:
                                    #elbow down
                                    solution_pre = "[3]"
                                elif next_idx[1] < row:
                                    # elbow up
                                    solution_pre = "[2]"
                            elif prev_idx[0] > col:
                                #Horizontal in from right
                                if (next_idx[0] < col):
                                    # Horizontal line
                                    solution_pre = "[e]"
                                elif next_idx[1] > row:
                                    #elbow down
                                    solution_pre = "[4]"
                                elif next_idx[1] < row:
                                    #elbow up
                                    solution_pre = "[1]"
                            elif prev_idx[1] > row:
                                #vertical in from bottom
                                if next_idx[1] < row:
                                    #vertical line
                                    solution_pre = "[p]"
                                elif next_idx[0] < col:
                                    #elbow left
                                    solution_pre = "[3]"
                                elif next_idx[0] > col:
                                    #elbow right
                                    solution_pre = "[4]"
                            elif prev_idx[1] < row:
                                #vertical in from top
                                if next_idx[1] > row:
                                    #vertical line
                                    solution_pre = "[p]"
                                elif next_idx[0] < col:
                                    #elbow left
                                    solution_pre = "[2]"
                                elif next_idx[0] > col:
                                    #elbow right
                                    solution_pre = "[1]"
                if not (col_num[boardIdx][col] and row_num[boardIdx][row]):
                    clueIndeces[boardIdx] += 1
                    crosswords[boardIdx] += "[" + str(clueIndeces[boardIdx]) + "]" + solution_pre + c + " |"
                    if not col_num[boardIdx][col]:
                        downIndeces[boardIdx].append(clueIndeces[boardIdx])
                        downClues[boardIdx].append(downCluesFlat.pop(0))
                    if not row_num[boardIdx][row]:
                        acrossIndeces[boardIdx].append(clueIndeces[boardIdx])
                    col_num[boardIdx][col] = clueIndeces[boardIdx]
                    row_num[boardIdx][row] = clueIndeces[boardIdx]
                else:
                    crosswords[boardIdx] +="[]" + solution_pre + c + " |"
                amuse_solutions[boardIdx] += c
            col += 1
        row += 1
    if (not solved):
        # Across
        for i in range(len(crosswords)):
            crosswords[i] += """\\end{Puzzle}\\\\\n{\\fontfamily{phv}\\selectfont\n\\begin{PuzzleClues}{\\textbf{Across}}\n\\begin{enumerate}[topsep=0pt,itemsep=-1ex,partopsep=1ex,parsep=1ex, left=0pt, align=left, labelsep=2pt]\n\\fontsize{8}{9}\\selectfont\n"""
        boardIdx = 0
        for puz in acrossClues:
            clueIdx = 0
            for clue in puz:
                clue_num = acrossIndeces[boardIdx][clueIdx]
                clue = acrossClues[boardIdx][clueIdx]
                # acrossClueCount[boardIdx] += 1
                clueIdx += 1
                crosswords[boardIdx] += """\\item [\\textbf{""" + str(clue_num) + """}] \\raggedright{""" + clue + """} \\\\\n"""
            boardIdx += 1

        #Down
        for i in range(len(crosswords)):
            crosswords[i] += """\\end{enumerate}\n\\end{PuzzleClues}\n\\begin{PuzzleClues}{\\textbf{Down}}\n\\begin{enumerate}[topsep=0pt,itemsep=-1ex,partopsep=1ex,parsep=1ex, left=0pt, align=left, labelsep=2pt]\n\\fontsize{8}{9}\\selectfont\n"""

        boardIdx = 0
        for puz in downClues:
            clueIdx = 0
            for clue in puz:
                clue_num = downIndeces[boardIdx][clueIdx]
                clue = downClues[boardIdx][clueIdx]
                clueIdx += 1
                crosswords[boardIdx] += """\\item [\\textbf{""" + str(clue_num) + """}] \\raggedright{""" + clue + """} \\\\\n"""
            boardIdx += 1

        for i in range(len(crosswords)):
            crosswords[i] += """\n\\end{enumerate}\n\\end{PuzzleClues}\n}\n\\end{minipage}\n\\vspace{1em}\n"""
            if i == 2:
                crosswords[i] += """\\\\"""
            elif i != 5:
                crosswords[i] += """&\n"""
    else:
        for i in range(len(crosswords)):
#             \vspace{2em}
# \center{\textsf{\textbf{\Large{SOME}}}}\\
            solutions_linear = solutions + [saturday_solution]
            crosswords[i] += """\\end{Puzzle}\\\\\n\\vspace{2em}\n\\center{\\textsf{\\textbf{\\Large{""" + solutions_linear[i] + """}}}}\\\\\n\\end{minipage}\n\\vspace{1em}\n"""
            if i == 2:
                crosswords[i] += """\\\\"""
            elif i != 5:
                crosswords[i] += """&\n"""

    #     for i in range(len(crosswords)):
    #         crosswords[i] += """\\end{Puzzle}\\\\\n"""
    return (crosswords,  amuse_solutions)

solved = False
crosswords_unsolved, amuse_solutions = generatePuzzle(solved)
document = (tex_header_solved if solved else tex_header) + "\n" + ''.join(crosswords_unsolved)
document += """\\\\\n\\end{tabular}\n\\end{center}\n\\end{document}"""

# Indeces variables indicate what #value to label the tiles. It does not offer any insight on to which tiles get the numbers, just what the tiles # values should be.
acrossIndeces = [[], [], [], [], [], []]
downIndeces = [[], [], [], [], [], []]

# acrossClueCount = [0] * 6
# downClueCount = [0] * 6

acrossClues = [[], [], [], [], [], []]
downClues = [[], [], [], [], [], []]
escapeChars = {"_": "\_", "&":"\&", "%": "\%", "$":"\$", "#":"\#", "{":"\{", "}":"\}", "~":"\\textasciitilde", "^":"\\textasciicircum", "\\":"\\textbackslash", """'""":"{\\myfont \\textquotesingle}"}
invertEscape  = {v: k for k, v in escapeChars.items()}
metaClueIndeces = None
metaSolutionIndeces = None
metaClues = []
metaSolution = []
saturday_solution_indeces = None
solution_indeces = []
saturday_solution = ""
solutions = ["", "", "", "", ""]

solved = True
crosswords_solved, amuse_solutions = generatePuzzle(solved)
document_solved = (tex_header_solved if solved else tex_header) + "\n" + ''.join(crosswords_solved)
document_solved += """\\\\\n\\end{tabular}\n\\end{center}\n\\end{document}"""
# print(solution_indeces)
amuse_doc = ""
for i in range(6):
    amuse_doc += amuse_solutions[i] + "\n"
    amuse_doc +=  "Across\n"
    for (clue, num) in zip(acrossClues[i], acrossIndeces[i]):
        clue_fixed = clue
        for word, initial in invertEscape.items():
            clue_fixed = clue_fixed.replace(word, initial)
        amuse_doc  += str(num) + ". " + clue_fixed + "\n"
    amuse_doc += "\n"
    amuse_doc +=  "Down\n"
    for (clue, num) in zip(downClues[i], downIndeces[i]):
        clue_fixed = clue
        for word, initial in invertEscape.items():
            clue_fixed = clue_fixed.replace(word, initial)
        amuse_doc  += str(num) + ". " + clue_fixed  + "\n"
    amuse_doc += "\n---\n\n"
    # amuse_doc += solution_indeces
for sol_idx in solution_indeces:
    amuse_doc += sol_idx + ","
amuse_doc = amuse_doc[:-1] + "\n"
for sat_sol_idx in saturday_solution_indeces:
    amuse_doc += str(sat_sol_idx)

try:  
    os.mkdir("output")  
except OSError as error:  
    print(error)

try:  
    os.mkdir(os.path.dirname("output/amuse"))
except OSError as error:  
    print(error)
try:  
    os.mkdir("output/pdf")  
except OSError as error:  
    print(error)

try:  
    os.mkdir("output/tex")  
except OSError as error:  
    print(error)
fileName = "MiniMeta" +  mini_number
f = open("output/amuse/" + fileName + ".txt", "w")
f.write(amuse_doc)
f.close()


f = open("output/tex/" + fileName + ".tex", "w")
f.write(document)
f.close()

subprocess.check_call(['pdflatex', "output/tex/" + fileName + ".tex"])
os.rename(fileName + ".pdf", "output/pdf/" + fileName + ".pdf")

f = open("output/tex/" + fileName + "(solved)" + ".tex", "w")
f.write(document_solved)
f.close()

subprocess.check_call(['pdflatex', "output/tex/" + fileName + "(solved)" + ".tex"])
os.rename(fileName + "(solved)" + ".pdf", "output/pdf/" + fileName + "(solved)" + ".pdf")