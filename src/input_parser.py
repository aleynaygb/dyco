from aba import ABAFramework


def read_list(text):
    # "[a,b,c]" or "a,b" -> ["a", "b", "c"]
    text = text.replace("[", "").replace("]", "")
    return [x.strip() for x in text.split(",") if x.strip() != ""]


def parse_text(text):
    # read the text of the user and build an ABAFramework
    literals = []
    assumptions = []
    contraries = {}
    rules = []
    preferences = []

    for line in text.splitlines():
        line = line.strip()
        if line == "" or line.startswith("##"):
            continue # empty line or title
        if line.startswith("L:"):
            literals = read_list(line[2:])
        elif line.startswith("A:"):
            assumptions = read_list(line[2:])
        elif line.startswith("C("):
            # C(a): r
            if ":" not in line:
                raise ValueError(f"missing ':' in : {line}")
            left, right = line.split(":", 1)
            contraries[left[2:-1].strip()] = right.strip()
        elif line.startswith("["):
            # [r1]: p <- q,a   (the name r1 is not used)
            if ":" not in line or "<-" not in line:
                raise ValueError(f"wrong rule : {line}")
            rule = line.split(":", 1)[1]
            head, body = rule.split("<-")
            rules.append((head.strip(), read_list(body)))
        elif line.startswith("PREF:"):
            preferences.append(line[5:])
        else:
            raise ValueError(f"line not understood : {line}")

    # check the input
    for a in assumptions:
        if a not in literals:
            raise ValueError(f"assumption {a} is not in L")
        if a not in contraries:
            raise ValueError(f"no contrary given for {a}")
        if contraries[a] not in literals:
            raise ValueError(f"contrary {contraries[a]} is not in L")
    for head, body in rules:
        for lit in [head] + body:
            if lit not in literals:
                raise ValueError(f"{lit} is used in a rule but is not in L")
        if head in assumptions:
            raise ValueError(f"{head} is an assumption, it cannot be the head of a rule")

    # build the framework
    f = ABAFramework()
    for lit in literals:
        f.add_literal(lit)
    for a in assumptions:
        f.add_assumption(a, contraries[a])
    for head, body in rules:
        f.add_rule(head, body)

    # PREF: a,b > c  means a and b are equally preferred and preferred to c
    for pref in preferences:
        groups = [read_list(g) for g in pref.split(">")]
        for group in groups:
            for a in group:
                if a not in assumptions:
                    raise ValueError(f"{a} in PREF is not an assumption")
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                for strong in groups[i]:
                    for weak in groups[j]:
                        f.add_preference(weak, strong)   # weak < strong
    return f
