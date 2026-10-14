from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    """ABA rule : head <- body (body can be empty)."""
    head: str
    body: tuple = ()

    def __str__(self):
        """if empy body -> return head"""
        if not self.body:
            return f"{self.head} <-"
        return f"{self.head} <- {', '.join(self.body)}"


class ABAFramework:
    """ABA framework: (L, R, A, contrary)."""

    def __init__(self):
        self.literals = set()      # L : language
        self.rules = []            # R : rules /list
        self.assumptions = set()   # A : assumptions (A included in L)
        self.contraries = {}       # contrary : assumption -> literal /dictionary

    # =================== PART 1 : a + b ====================== 
    def add_literal(self, name):
        """add a literal in L."""
        self.literals.add(name)

    def add_assumption(self, name, contrary):
        """form an assumption and its contrary"""
        if any(rule.head == name for rule in self.rules):
            raise ValueError(f"'{name}' est tête d'une règle : ABA non plat.")
        # add assumption both in A and L
        self.add_literal(name)
        self.add_literal(contrary)
        self.assumptions.add(name)
        self.contraries[name] = contrary

    def add_rule(self, head, body=()):
        """add 'head <- body' rule, after verification."""
        for literal in (head, *body):
            # each literal must be declared
            if literal not in self.literals:
                raise ValueError(f"Littéral inconnu : '{literal}'.")
        # refuses a rule if its head is an assumption    
        if head in self.assumptions:
            raise ValueError(f"'{head}' est une assumption : ABA non plat.")
        self.rules.append(Rule(head, tuple(body)))

    def display(self):
        """display framework."""
        print("Langage L      :", sorted(self.literals))
        print("Assumptions A  :", sorted(self.assumptions))
        print("Règles R       :")
        for rule in self.rules:
            print("   ", rule)
        print("Contraires     :")
        for assumption, contrary in self.contraries.items():
            print(f"    contrary({assumption}) = {contrary}")

    # =================== PART 1 : c ====================== 


    def is_atomic(self):
        """atomic : body of each rule is included in A."""
        for rule in self.rules:
            # if body of the rule not included in A 
            if not set(rule.body) <= self.assumptions: 
                return False
        return True 

    def is_circular(self):
        """circular : an atom can be derived from itself (cycle in the rules)."""
        # dependances : for each head of rule, atoms that it depends on 
        depends_on = {}
        for rule in self.rules:
            if rule.head not in depends_on:
                depends_on[rule.head] = set()
            for atom in rule.body:
                depends_on[rule.head].add(atom)

        in_progress = set()   # atoms to check
        checked = set()       # checked atoms

        def has_cycle(atom):
            if atom in in_progress: # cycle
                return True
            if atom in checked: # no cycle
                return False
            in_progress.add(atom)
            for dep in depends_on.get(atom, []):
                if has_cycle(dep):
                    return True
            in_progress.remove(atom)
            checked.add(atom)
            return False

        for atom in depends_on:
            if has_cycle(atom):
                return True
        return False

    def to_non_circular(self):
        non_assumptions = self.literals - self.assumptions
        k = len(non_assumptions)

        def name(s, i):
            # s^k = s, other steps are renamed
            return s if i == k else f"{s}_{i}"

        new = ABAFramework()

        # 1. literals : old ones + copies
        for lit in self.literals:
            new.add_literal(lit)
        for s in non_assumptions:
            for i in range(1, k + 1):
                new.add_literal(name(s, i))

        # 2. inchanged assumptions and contraries
        for a in self.assumptions:
            new.add_assumption(a, self.contraries[a])

        # 3. rules
        for rule in self.rules:
            atomic = set(rule.body) <= self.assumptions
            start = 1 if atomic else 2      # atomique : étages 1..k, sinon 2..k
            for i in range(start, k + 1):
                if atomic:
                    new_body = list(rule.body)
                else:
                    new_body = [p if p in self.assumptions else name(p, i - 1)
                                for p in rule.body]
                new.add_rule(name(rule.head, i), new_body)

        return new

    def to_atomic(self):
        non_assumptions = self.literals - self.assumptions

        new = ABAFramework()

        # 1. original literals and assumptions
        for lit in self.literals:
            new.add_literal(lit)
        for a in self.assumptions:
            new.add_assumption(a, self.contraries[a])

        # 2. new assumptions s_d and s_nd
        for s in non_assumptions:
            new.add_assumption(f"{s}_d", f"{s}_nd")   # contraire de s_d  = s_nd
            new.add_assumption(f"{s}_nd", s)          # contraire de s_nd = s

        # 3. rules : each literals\assumption becomes s_d
        for rule in self.rules:
            new_body = [p if p in self.assumptions else f"{p}_d" for p in rule.body]
            new.add_rule(rule.head, new_body)

        return new

    def convert(self):
        return self.to_non_circular().to_atomic()

def show_properties(framework):
    """Affiche si le framework est atomique et/ou circulaire."""
    print("Atomique   ?", framework.is_atomic())
    print("Circulaire ?", framework.is_circular())

# ======================= TEST ==========================

f = ABAFramework()
f.add_literal("q")
f.add_assumption("a", "r")   # contraire de a = r
f.add_assumption("b", "p")   # contraire de b = p

f.add_rule("p", ["q"])       # p <- q  (non atomique : q n'est pas une hypothèse)
f.add_rule("q", ["a"])       # q <- a  (atomique)
f.add_rule("r", ["b"])       # r <- b  (atomique)
f.add_rule("p", ["a"])       # p <- a  (atomique)
f.add_rule("q", ["p"])       # q <- p 

print("=== AVANT ===")
f.display()
show_properties(f)

g = f.to_atomic()

print("\n=== APRES ===")
g.display()
show_properties(g)