SeedRandom[2611];
(* Message: "Nume Prenume" written in ASCII *)
msg = "Oberst Eduard";
codes = ToCharacterCode[msg];
hex = StringJoin[IntegerString[codes, 16, 2]];
m = FromDigits[hex, 16];
Print["ASCII codes: ", codes];
Print["hex = ", hex];
Print["m = ", m];

(* Key generation: p and q of different lengths, n >= 2048 bits *)
p = RandomPrime[{2^1033, 2^1034 - 1}];
q = RandomPrime[{2^1023, 2^1024 - 1}];
n = p*q;
phi = (p - 1)*(q - 1);
Print["p = ", p, "  (", BitLength[p], " bits)"];
Print["q = ", q, "  (", BitLength[q], " bits)"];
Print["n = ", n, "  (", BitLength[n], " bits)"];
Print["phi(n) = ", phi];

(* e is chosen at random, 65537 <= e < phi(n), gcd(e, phi(n)) = 1 *)
e = RandomInteger[{65537, phi - 1}];
While[GCD[e, phi] != 1, e = RandomInteger[{65537, phi - 1}]];
d = PowerMod[e, -1, phi];
Print["e = ", e];
Print["GCD[e, phi] = ", GCD[e, phi]];
Print["d = ", d];
Print["Mod[e*d, phi] = ", Mod[e*d, phi]];

(* Encryption and decryption *)
Print["m < n: ", m < n];
c = PowerMod[m, e, n];
Print["c = ", c];
m2 = PowerMod[c, d, n];
Print["m' = ", m2];
Print["text = ", FromCharacterCode[IntegerDigits[m2, 256]]];
