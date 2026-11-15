"""Constructed calibration bridges; established mathematics, not historical discoveries.

These contrast documented conventional references with justified additional structure.
They are public development/audit contract tests, not human preference measurements.
"""
from .schema import Task


def novelty_example(index: int, split: str) -> tuple[Task, str, str, str]:
    """Return equally correct answers with conventional, constructive and false theory."""
    n = 4 + 2 * index + (100 if split == "audit" else 0)
    family = ("gcd", "lcm", "polynomial_multiplication", "dice")[index % 4]
    if family == "gcd":
        problem, answer = f"Find gcd({2*n}, {3*n}).", str(n)
        standard = ("Any divisor of 2n and 3n divides their difference n, and every divisor of n "
                    "divides both. Thus gcd(2n,3n)=n for positive n. The same argument gives "
                    "gcd(a,b)=gcd(a,b-a), the invariant of Euclid's algorithm.")
        bridge = ("View I(a,b)={ua+vb: u,v integers} as the lattice of reachable displacements "
                  "on an integer line. It is closed under addition and negation. Let d be its "
                  "least positive element for nonzero positive a,b. Dividing any t in I by d "
                  "leaves a remainder in I smaller than d, hence zero. Therefore I=dZ. "
                  "Both a,b are multiples of d; every common divisor divides every ua+vb, "
                  "so d is their gcd. This turns gcd into the spacing of a reachable lattice. "
                  "For a=2n,b=3n, every displacement is a multiple of n and n=3n-2n is reachable, "
                  "so I=nZ. Further, ua+vb=t has an integer solution exactly when d divides t; "
                  "with these step sizes n is reachable and n+1 is not for n>1. The construction "
                  "requires integer signed moves; nonnegative moves do not form a subgroup.")
        false = ("Define I(a,b)={ua+vb: u,v nonnegative integers}. This set is a group under "
                 "addition and equals gcd(a,b)*Z; therefore every negative multiple is reachable.")
    elif family == "lcm":
        problem, answer = f"Find lcm({2*n}, {3*n}).", str(6*n)
        standard = ("A multiple of 2n and 3n is n*k with both 2 and 3 dividing k, so 6 divides k. "
                    "Conversely 6n is common. Thus lcm(2n,3n)=6n. More generally maximum prime "
                    "exponents give lcm; minimum exponents give gcd, proving gcd(a,b)*lcm(a,b)=a*b.")
        bridge = ("Represent exact recurring events by subgroups aZ,bZ of integer time. Their "
                  "intersection is a subgroup; if l is its least positive element, division with "
                  "remainder shows every member is a multiple of l. Hence aZ intersect bZ=lZ "
                  "and l=lcm(a,b). For 2n and 3n this is 6nZ, since t=n*k must have 6 dividing k. "
                  "For events with phases r,s the schedules are cosets r+aZ and s+bZ. If a common "
                  "time t0 exists, subtracting t0 shows their entire intersection is t0+lZ. "
                  "Thus a single coincidence determines all future coincidences. For phases "
                  "r=s=n with periods 2n,3n, common times are n+6nZ. Arbitrary phases may give "
                  "an empty intersection: even times and odd times with period 2 never coincide.")
        false = ("Every pair of cosets r+aZ and s+bZ intersects, regardless of phases. "
                 "For example 0+2Z and 1+2Z have a common integer time. This proves universal synchronization.")
    elif family == "polynomial_multiplication":
        problem, answer = f"Expand (x+{n})*(x-{n}).", f"x**2-{n*n}"
        standard = ("Distributivity in a commutative ring gives (x+n)(x-n)=x*x-x*n+n*x-n*n "
                    "=x**2-n**2. The general identity (a+b)(a-b)=a**2-b**2 also computes "
                    "(m+1)(m-1)=m**2-1. Noncommuting products retain a cross-term commutator.")
        bridge = ("Use the quadratic algebra A=R[x][e]/(e**2-1): each element has unique form "
                  "a+b*e, with a,b in R[x]. Conjugation a+b*e -> a-b*e preserves products, "
                  "so the scalar norm N(a+b*e)=a**2-b**2 is multiplicative. Indeed "
                  "N(uv)=uv*conj(u)*conj(v)=N(u)*N(v) by commutativity. Setting u=x+n*e "
                  "gives N(u)=x**2-n**2, equal to (x+n)(x-n) by evaluation at e=1 and e=-1. "
                  "This yields the reusable composition law (a**2-b**2)(c**2-d**2) "
                  "=(a*c+b*d)**2-(a*d+b*c)**2, by multiplying the two pairs. The algebra "
                  "has zero divisors: (1+e)(1-e)=0 although both factors are nonzero; it is not a field.")
        false = ("Define A=R[e]/(e**2-1). It is a field, so every nonzero element has an inverse. "
                 "In particular 1+e is invertible even though (1+e)(1-e)=0 and 1-e is nonzero.")
    else:
        problem, answer = f"Roll two independent fair {n}-sided dice. What is the probability their sum is even?", "1/2"
        standard = ("For an even-sided fair die, half the faces are even and half odd. Independence "
                    "gives P(even sum)=P(even,even)+P(odd,odd)=1/4+1/4=1/2. More generally, "
                    "independent dice with even-face probabilities p,q give p*q+(1-p)*(1-q).")
        bridge = ("Encode parity by the character chi(k)=(-1)**k of the additive integers into "
                  "{1,-1}. Its law chi(a+b)=chi(a)*chi(b) changes addition into multiplication. "
                  "The even indicator is (1+chi(k))/2. Independence therefore gives "
                  "P(X+Y even)=(1+E[chi(X)]*E[chi(Y)])/2. Each even-sided fair die has "
                  "equally many signs, so each expectation is zero and the answer is 1/2. "
                  "For any number of independent integer-valued variables, the same argument "
                  "gives even-sum probability (1+product_i E[chi(X_i)])/2; one parity-balanced "
                  "summand suffices. Independence matters: for Y=X with X uniform on {1,2}, "
                  "each expectation is zero but X+Y is always even. This character transform "
                  "is a reusable bridge from probability convolution to multiplicative statistics.")
        false = ("The character chi(k)=(-1)**k implies E[chi(X)*chi(Y)]=E[chi(X)]*E[chi(Y)] "
                 "for all X,Y without independence. Thus if X is uniform on {1,2} and Y=X, "
                 "the probability X+Y is even is 1/2.")
    task = Task(id=f"novelty-{split}-{index}", problem=problem, answer=answer,
                family=family, split=f"calibration_{split}", provenance={"constructed": True},
                metadata={"variables": ["x"]} if family == "polynomial_multiplication" else {})
    final = f"\n<final>{answer}</final>"
    if index >= 4:
        standard += " I rename this the Universal Conceptual Ocean, a completely new mathematical paradigm."
    return task, bridge + final, standard + final, false + final
