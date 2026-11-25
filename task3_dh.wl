SeedRandom[2633];
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

(* Secret numbers: 1 < a, b <= p - 2 and at least 256 bits *)
a = RandomInteger[{2^255, p - 2}];
b = RandomInteger[{2^255, p - 2}];
Print["a = ", a, "  (", BitLength[a], " bits)"];
Print["b = ", b, "  (", BitLength[b], " bits)"];

(* Public values sent over the open channel *)
A = PowerMod[g, a, p];
B = PowerMod[g, b, p];
Print["A = ", A];
Print["B = ", B];

(* Each side computes the common secret *)
kAlice = PowerMod[B, a, p];
kBob = PowerMod[A, b, p];
Print["k (Alice) = ", kAlice];
Print["k (Bob)   = ", kBob];
Print["Equal: ", kAlice == kBob, ",  ", BitLength[kAlice], " bits"];

(* AES-256 key: SHA-256 of the 256 bytes of k *)
kBytes = ByteArray[IntegerDigits[kAlice, 256, 256]];
aesKey = Hash[kBytes, "SHA256", "HexString"];
Print["AES-256 key = ", aesKey, "  (", 4*StringLength[aesKey], " bits)"];

(* Check: the name is encrypted with AES-256 and decrypted again *)
keyBytes = ByteArray[IntegerDigits[FromDigits[aesKey, 16], 256, 32]];
sk = SymmetricKey[<|"Cipher" -> "AES256", "BlockMode" -> "CBC", "Key" -> keyBytes|>];
enc = Encrypt[sk, "Oberst Eduard"];
Print[enc];
Print["Decrypt = ", Decrypt[sk, enc]];
Print["IV = ", Normal[enc["InitializationVector"]]];
Print["Data = ", Normal[enc["Data"]]];
