import io
import contextlib
import streamlit as st
from aba import fmt
from input_parser import parse_text

EXAMPLE = """## Literals
L: [a,b,c,q,p,r,s,t]

## Assumptions
A: [a,b,c]

## Contraries
C(a): r
C(b): s
C(c): t

## Rules
[r1]: p <- q,a
[r2]: q <-
[r3]: r <- b,c
[r4]: t <- p,c
[r5]: s <- t

## Preferences
PREF: a > b
"""


def show(framework):
    # display() prints in the console, so we catch the text and show it in the page
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        framework.display()
    st.code(buffer.getvalue())


def attack_lines(attacks):
    # attacker --> attacked, sorted
    lines = [fmt(x) + "  -->  " + fmt(y) for x, y in attacks]
    return "\n".join(sorted(lines))


st.title("ABA generator")
st.write("Write your ABA framework below (same format as the example) and click on Generate.")
text = st.text_area("Input", EXAMPLE, height=450)

if st.button("Generate"):
    try:
        f = parse_text(text)
    except ValueError as error:
        st.error(f"Input error : {error}")
        st.stop()

    st.header("1. Framework")
    show(f)

    st.header("2. Non-circular framework")
    show(f.to_non_circular())

    st.header("3. Non-circular and atomic framework")
    show(f.convert())

    # arguments and attacks of the framework of part 1
    args = f.build_arguments()
    st.header("4. Arguments")
    st.write(f"{len(args)} arguments")
    st.code("\n".join(sorted(fmt(a) for a in args)))

    st.header("5. Attacks (without preferences)")
    attacks = f.build_attacks(args)
    st.write(f"{len(attacks)} attacks")
    st.code(attack_lines(attacks))

    st.header("6. Normal and reverse attacks (with preferences)")
    normal, reverse = f.build_attacks_plus(args)
    st.write(f"{len(normal)} normal attacks")
    st.code(attack_lines(normal))
    st.write(f"{len(reverse)} reverse attacks")
    st.code(attack_lines(reverse))
