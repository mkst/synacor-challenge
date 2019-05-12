# synacor-challenge

An incomplete solution to the [2012 Synacor Challenge](http://challenge.synacor.com) written in Python.

## Codes

Codes discovered so far:

 - `fbwwsldZmWKv` (arch-spec)
 - `wLCVsTGpgzqR` (pre-selftest)
 - `KCojPVcoOdVP` (post-selftest)
 - `AqxdDiCYrzVE` ("use tablet")
 - `EjNzmoeZrZQC` ("use teleporter" when broken)
 - `????????????` ("use teleporter" once fixed)
 - `dxVYIIAbxMl8` => `bxVYIIAdxMl8` ("use mirror")

## Walkthrough

Commands can be found in [walkthrough.txt](/artefacts/walkthru.txt)

### Coins

```
_ + _ * _^2 + _^3 - _ = 399
```

| coin     | value |
|:--------:|:-----:|
| blue     | 9     |
| red      | 2     |
| shiny    | 5     |
| corroded | 3     |
| concave  | 7     |

```
9 + 2 * 5^2 + 7^3 - 3 = 399
```

### Vault

```
-------------------------------------
|   *    |   8    |   -    |  1 (V) |
-------------------------------------
|   4    |   *    |   11   |   *    |
-------------------------------------
|   +    |   4    |   -    |   18   |
------------------------------------
| 22 (O) |   -    |   9    |   *    |
-------------------------------------
```

Orb is `22`

Vault requires `30`

**Steps:**
 - north, east, 22 + 4 => 26
 - east, north, 26 - 11 => 15
 - west, south, 15 * 4 => 60
 - east, east, 60 - 18 => 42
 - west, north, 42 - 11 => 31
 - north, east, 31 - 1 => 30

**Extra:**
- `memory[3953]` keeps track of number of moves
- `memory[3952]` keeps track of orb value

## Notes

 - Journal entry days are the start of the Fibonacci sequence
