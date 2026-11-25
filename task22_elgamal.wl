SeedRandom[2622];
p = 323170060713110073001535134778251633624880571334890751745884341392698068\
    341362100027920563626401646854585563579353308169288290230805734726252735\
    547424612457410262025279165729728627063003252634282131457669314142236542\
    209411113486299916574782680342305530863490506355577122191878903327295696\
    961297438562417412362372251973464026918557977679768230146253979330580152\
    268587307611975324364674758554607150438968449403661304976978128542959586\
    595975670512838521327844685229255045682728791137200989318739591433741758\
    378260002780349731985520606075332341226032546840881200311059074842810039\
    94966956119696956248629032338072839127039;
g = 2;
Print["PrimeQ[p] = ", PrimeQ[p], ",  ", BitLength[p], " bits"];

msg = "Oberst Eduard";
m = FromDigits[StringJoin[IntegerString[ToCharacterCode[msg], 16, 2]], 16];
Print["m = ", m];

(* Key generation: private key a, 1 < a <= p - 2 *)
a = RandomInteger[{2, p - 2}];
y = PowerMod[g, a, p];
Print["a = ", a];
Print["y = ", y];

(* Encryption: session key k, 1 < k <= p - 2 *)
k = RandomInteger[{2, p - 2}];
A = PowerMod[g, k, p];
B = Mod[PowerMod[y, k, p]*m, p];
Print["k = ", k];
Print["A = ", A];
Print["B = ", B];

(* Decryption with the two formulas from the course *)
m1 = Mod[B*PowerMod[PowerMod[A, a, p], -1, p], p];
m2 = Mod[B*PowerMod[A, p - 1 - a, p], p];
Print["B (A^a)^-1 mod p = ", m1];
Print["B A^(p-1-a) mod p = ", m2];
Print["text = ", FromCharacterCode[IntegerDigits[m2, 256]]];
