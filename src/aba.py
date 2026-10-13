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


# exemple for better understanding 
if __name__ == "__main__":
    aba = ABAFramework()

    # 0. On donne un nom lisible à chaque phrase
    SOLEIL_ANNONCE = "la météo annonce du soleil"                # q (fait)
    CIEL_DEGAGE = "le ciel reste dégagé"                         # a (assumption)
    IL_VA_PLEUVOIR = "il va pleuvoir"                            # c_a (contraire de a)
    NUAGES_PLUIE = "les nuages noirs annoncent la pluie"         # b (assumption)
    NUAGES_INOFFENSIFS = "ces nuages sont inoffensifs"           # c_b (contraire de b)
    PAS_DE_PARAPLUIE = "je laisse le parapluie à la maison"      # p (conclusion)

    # 1. Littéraux ordinaires
    for lit in [SOLEIL_ANNONCE, PAS_DE_PARAPLUIE]:
        aba.add_literal(lit)

    # 2. Assumptions (avec leur contraire)
    aba.add_assumption(CIEL_DEGAGE, IL_VA_PLEUVOIR)
    aba.add_assumption(NUAGES_PLUIE, NUAGES_INOFFENSIFS)

    # 3. Règles
    aba.add_rule(PAS_DE_PARAPLUIE, [SOLEIL_ANNONCE, CIEL_DEGAGE])
    aba.add_rule(SOLEIL_ANNONCE)
    aba.add_rule(IL_VA_PLEUVOIR, [NUAGES_PLUIE])

    aba.display()