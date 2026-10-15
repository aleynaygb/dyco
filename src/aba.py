from dataclasses import dataclass

@dataclass(frozen=True)
class Rule:
    # rule : head <- body (body can be empty)
    head: str
    body: tuple = ()

    def __str__(self):
        # empty body -> only the head
        if not self.body:
            return f"{self.head} <-"
        return f"{self.head} <- {', '.join(self.body)}"

class ABAFramework:
    def __init__(self):
        self.literals = set()      # language l
        self.rules = []            # list of Rule
        self.assumptions = set()   # a
        self.contraries = {}       # assumption -> its contrary
        self.preferences = set()   # pairs (weaker, stronger)

    # ---------- 1 & 2. definition of the framework ----------

    def add_literal(self, lit):
        self.literals.add(lit)

    def add_rule(self, head, body=()):
        self.rules.append(Rule(head, tuple(body)))

    def add_assumption(self, a, contrary):
        # an assumption and its contrary are both literals
        self.literals.add(a)
        self.literals.add(contrary)
        self.assumptions.add(a)
        self.contraries[a] = contrary

    def add_preference(self, weaker, stronger):
        # weaker < stronger
        self.preferences.add((weaker, stronger))

    # ---------- 3. conversion ----------

    def copy_without_rules(self):
        # new framework with same l, a, contraries and preferences, but no rules
        new = ABAFramework()
        new.literals = set(self.literals)
        new.assumptions = set(self.assumptions)
        new.contraries = dict(self.contraries)
        new.preferences = set(self.preferences)
        return new

    def to_non_circular(self):
        non_assump = self.literals - self.assumptions
        k = len(non_assump) # number of levels

        def name(s, i):
            # last level keeps the original name
            return s if i == k else f"{s}_{i}"

        new = self.copy_without_rules()
        # add the copies of each non assumption (one per level)
        for s in non_assump:
            for i in range(1, k + 1):
                new.literals.add(name(s, i))

        for rule in self.rules:
            atomic = set(rule.body) <= self.assumptions
            start = 1 if atomic else 2 # atomic rules: levels 1..k, others: 2..k
            for i in range(start, k + 1):
                if atomic:
                    new_body = rule.body
                else:
                    # assumptions stay, other literals come from the level below
                    new_body = tuple(b if b in self.assumptions else name(b, i - 1)
                                     for b in rule.body)
                new.rules.append(Rule(name(rule.head, i), new_body))
        return new

    def to_atomic(self):
        non_assump = self.literals - self.assumptions
        new = self.copy_without_rules()
        # two new assumptions for each non assumption
        for s in non_assump:
            new.literals |= {s + "_d", s + "_nd"}
            new.assumptions |= {s + "_d", s + "_nd"}
            new.contraries[s + "_d"] = s + "_nd"
            new.contraries[s + "_nd"] = s
        # in each body, a non assumption s becomes s_d
        for rule in self.rules:
            new_body = tuple(b if b in self.assumptions else b + "_d" for b in rule.body)
            new.rules.append(Rule(rule.head, new_body))
        return new

    def convert(self):
        # first remove cycles, then make atomic
        return self.to_non_circular().to_atomic()

    # ---------- 4. arguments and attacks ----------

    def build_arguments(self):
        # an argument is (support, conclusion)
        # every assumption is an argument for itself
        args = {(frozenset([a]), a) for a in self.assumptions}
        changed = True
        while changed: # repeat until nothing new
            changed = False
            for rule in self.rules:
                # for each literal of the body, all the supports that prove it
                options = [[X for (X, s) in args if s == b] for b in rule.body]
                # pick one support per body literal and merge them
                combos = [frozenset()]
                for opt in options:
                    combos = [c | X for c in combos for X in opt]
                for X in combos:
                    if (X, rule.head) not in args:
                        args.add((X, rule.head))
                        changed = True
        return args

    def build_attacks(self, args):
        # (x, s) attacks (y, t) if s is the contrary of an assumption in y
        attacks = set()
        for (X, s) in args:
            for (Y, t) in args:
                if any(self.contraries[a] == s for a in Y):
                    attacks.add(((X, s), (Y, t)))
        return attacks

    # ---------- 5. preferences: normal / reverse attacks ----------

    def build_attacks_plus(self, args):
        normal, reverse = set(), set()
        for (X, s) in args:
            for (Y, t) in args:
                for y in Y:
                    if self.contraries[y] == s: # (x, s) attacks y
                        # is one assumption of x weaker than the attacked y ?
                        if any((x, y) in self.preferences for x in X):
                            reverse.add(((Y, t), (X, s))) # attack is reversed
                        else:
                            normal.add(((X, s), (Y, t))) # normal attack
        return normal, reverse

        # ---------- display of the framework and its properties (for tests) ----------

    def is_atomic(self):
        # atomic if the body of every rule only contains assumptions
        for rule in self.rules:
            if not set(rule.body) <= self.assumptions:
                return False
        return True

    def is_circular(self):
        # circular if a literal can depend on itself through the rules
        # deps[h] = literals that appear in the bodies of the rules with head h
        deps = {}
        for rule in self.rules:
            deps.setdefault(rule.head, set()).update(rule.body)

        def has_cycle(lit, path):
            if lit in path:                    # we came back to a literal of the path
                return True
            for d in deps.get(lit, []):        # follow each dependency
                if has_cycle(d, path | {lit}):
                    return True
            return False

        return any(has_cycle(h, set()) for h in deps)

    def display(self):
        print("literals    :", sorted(self.literals))
        print("assumptions :", sorted(self.assumptions))
        print("rules       :")
        for rule in self.rules:
            print("   ", rule)
        print("contraries  :")
        for a, c in self.contraries.items():
            print(f"    contrary({a}) = {c}")
        print("preferences :", sorted(self.preferences))
        print("atomic      :", self.is_atomic())
        print("circular    :", self.is_circular())


def fmt(arg):
    # print an argument like {a} |- p
    X, s = arg
    return "{" + ",".join(sorted(X)) + "} |- " + s


# ---------- test : default reasoning (tweety and joe) ----------

f = ABAFramework()

# literals (non assumptions)
for lit in ["fly_tweety", "fly_joe", "bird_tweety", "bird_joe",
            "penguin_tweety", "penguin_joe"]:
    f.add_literal(lit)

# assumptions : "tweety / joe are normal", with their contrary
f.add_assumption("normal_tweety", "not_fly_tweety")
f.add_assumption("normal_joe", "not_fly_joe")

# fly(X) <- bird(X), normal(X)
f.add_rule("fly_tweety", ["bird_tweety", "normal_tweety"])
f.add_rule("fly_joe", ["bird_joe", "normal_joe"])
# not_fly(X) <- penguin(X)
f.add_rule("not_fly_tweety", ["penguin_tweety"])
f.add_rule("not_fly_joe", ["penguin_joe"])
# bird(X) <- penguin(X)
f.add_rule("bird_tweety", ["penguin_tweety"])
f.add_rule("bird_joe", ["penguin_joe"])
# facts
f.add_rule("penguin_tweety")
f.add_rule("bird_joe")

f.display()
# not circular, so to_atomic is enough (convert would build 8 levels)
print("rules after to_atomic :")
#f.convert().display()