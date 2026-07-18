#!/usr/bin/env python3
"""Generate src/levels.h: 10 maps, per-level config, boss table.
Chars: '#' solid  '=' one-way  '*' gem  'H' cherry  'E' eagle  'F' frog
'O' opossum  'B' boss  'P' spawn  'C' checkpoint  'D' door"""
W, H = 90, 30

def new(): return [[' ']*W for _ in range(H)]
def hseg(g,row,c0,c1,ch='#'):
    for c in range(c0,c1+1): g[row][c]=ch
def vseg(g,col,r0,r1,ch='#'):
    for r in range(r0,r1+1): g[r][col]=ch
def fill(g,r0,r1,c0,c1,ch='#'):
    for r in range(r0,r1+1): hseg(g,r,c0,c1,ch)
def put(g,r,c,ch):
    assert g[r][c]==' ', f"overlap {ch}@({r},{c})={g[r][c]!r}"
    g[r][c]=ch
def grounded(g,r,c,ch):
    assert r+2<H and (g[r+1][c] in '#=' or g[r+2][c] in '#='), f"{ch}@({r},{c}) floats"
    put(g,r,c,ch)

levels=[]; cfgs=[]

# --- reachability validator ------------------------------------------------
# Jump model for the tuned physics (JUMP_VEL -6.3, air jump -5.4, glide):
# single jump ~3 tiles, jump+air-jump ~5 tiles, glide gives long flat reach.
def validate(s, name):
    solid=lambda r,c: 0<=r<H and 0<=c<W and s[r][c] in '#='
    def standable(r,c):
        if not (0<=r<H-1 and 0<=c<W): return False
        if s[r][c] in '#=': return False
        if not solid(r+1,c): return False
        if r>0 and s[r-1][c]=='#': return False      # need 2-tile headroom
        return True
    stand={(r,c) for r in range(H-1) for c in range(W) if standable(r,c)}
    def drop_to_stand(r,c):
        while r<H-1:
            if (r,c) in stand: return (r,c)
            r+=1
        return None
    def find(ch):
        for r in range(H):
            c=s[r].find(ch)
            if c>=0: return (r,c)
        return None
    start=drop_to_stand(*find('P'))
    assert start, f"{name}: P has no footing"
    # BFS over standable cells with the jump-reach envelope
    from collections import deque
    seen={start}; q=deque([start])
    def reach(r,c,r2,c2):
        rise=r-r2; dc=abs(c2-c)
        if rise<=0: return dc<=11                    # drop / level, glide reach
        if rise<=2: return dc<=7
        if rise<=3: return dc<=6
        if rise<=4: return dc<=5
        if rise<=5: return dc<=3                     # needs a clean double jump
        return False
    cand=sorted(stand)
    while q:
        r,c=q.popleft()
        for r2,c2 in cand:
            if (r2,c2) in seen: continue
            if reach(r,c,r2,c2): seen.add((r2,c2)); q.append((r2,c2))
    door=drop_to_stand(*find('D'))
    assert door in seen, f"{name}: door unreachable from spawn"
    # every gem must stay collectible from spawn AND from the door area,
    # so descending early can never soft-lock the gem requirement
    seen_door={door}; q=deque([door])
    while q:
        r,c=q.popleft()
        for r2,c2 in cand:
            if (r2,c2) in seen_door: continue
            if reach(r,c,r2,c2): seen_door.add((r2,c2)); q.append((r2,c2))
    for label,vis in (("spawn",seen),("door",seen_door)):
        for r in range(H):
            for c in range(W):
                if s[r][c]!='*': continue
                ok=any((0<=sr-r<=5 and abs(sc-c)<=4) or (sr-r<0 and abs(sc-c)<=9)
                       for sr,sc in vis)
                assert ok, f"{name}: gem at ({r},{c}) unreachable from {label}"
    for ch in 'CH':
        for r in range(H):
            for c in range(W):
                if s[r][c]!=ch: continue
                cell=drop_to_stand(r,c)
                assert cell in seen, f"{name}: {ch} at ({r},{c}) unreachable"

def add(g,name,req,boss,back,jungle):
    s=[''.join(r) for r in g]
    assert sum(r.count('P') for r in s)==1, name+" P"
    assert sum(r.count('D') for r in s)==1, name+" D"
    nb=sum(r.count('B') for r in s)
    assert (nb==1)==(boss>=0), name+" B"
    ng=sum(r.count('*') for r in s)
    assert ng>=req+3, f"{name} gems {ng} req {req}"
    validate(s,name)
    levels.append(s); cfgs.append((name,req,boss,back,jungle))
    print(f"{name}: gems={ng} req={req} boss={boss}")

# ---------- L1 VERDANT WOODS (forest intro, door) ----------
L1=[
"                                                                                          ",
"                                                                                          ",
"                                              E                                           ",
"                                          *  *  *  *                                      ",
"                                      E                                                   ",
"                                        =============                                     ",
"                                                         *                                ",
"                                 * *                      *         E                     ",
"                                                        =====                             ",
"                                =====                                                     ",
"                           *                          E                                   ",
"                      E                                        ====                       ",
"                          ====                                        *                   ",
"                     *                                                          E         ",
"                                                                     ====                 ",
"                    ====                                                    *             ",
"               *                                                                          ",
"                                                                           ====           ",
"              ====                                                                *       ",
"          *                                                                        *      ",
"                                                                                 ====     ",
"        ====                  E                                                           ",
"                                                                                          ",
"     P      F   H   *            O         C                *       F  C  O          *    ",
"                                                                                          ",
"  #####################   ###################   ###########   ##########################  ",
"  ######################################                     ###########################  ",
"  ######################################  *       E *     *  ###########################  ",
"  ######################################                     ###########################  ",
"  ######################################################################################  ",
]
g=[list(r.ljust(W)) for r in L1]
grounded(g,23,80,'D')
add(g,"VERDANT WOODS",12,-1,(255,255,255),(255,255,255))

# ---------- L2 TWILIGHT HOLLOW (cave galleries, door) ----------
g=new()
hseg(g,0,0,89); hseg(g,1,0,89); hseg(g,28,0,89); hseg(g,29,0,89)
vseg(g,0,2,27); vseg(g,1,2,27); vseg(g,88,2,27); vseg(g,89,2,27)
for r in (9,10): hseg(g,r,2,30); hseg(g,r,38,60); hseg(g,r,68,87)
for r in (17,18): hseg(g,r,2,20); hseg(g,r,28,50); hseg(g,r,58,87)
hseg(g,26,2,87); hseg(g,27,2,87)
for col in (14,34,52,72): vseg(g,col,2,4)
for col in (24,44,64): vseg(g,col,24,25)
hseg(g,13,32,35,'='); hseg(g,13,62,65,'=')
hseg(g,21,22,25,'='); hseg(g,21,52,55,'=')
hseg(g,5,30,33,'='); hseg(g,5,58,61,'=')
put(g,7,4,'P'); grounded(g,25,84,'D')
for r,c in [(7,10),(7,22),(3,16),(3,36),(7,44),(7,56),(3,54),(3,74),(7,80),
            (15,6),(15,14),(12,33),(15,34),(15,46),(12,63),(15,64),(15,76),
            (24,10),(24,50),(24,78)]: put(g,r,c,'*')
for r,c in [(7,18),(7,50),(7,76)]: put(g,r,c,'E')
for r,c in [(16,40),(25,30),(25,56)]: grounded(g,r,c,'F')
for r,c in [(16,70),(25,16),(25,70)]: grounded(g,r,c,'O')
grounded(g,16,30,'H'); grounded(g,25,40,'H')
grounded(g,16,60,'C'); grounded(g,25,20,'C')
add(g,"TWILIGHT HOLLOW",12,-1,(140,150,210),(120,120,180))

# ---------- L3 CANOPY HEIGHTS (tall trees, frog boss) ----------
g=new()
fill(g,25,29,0,89)               # forest floor
for c0 in (12,30,48):            # tree trunks with branch platforms
    vseg(g,c0,8,24); vseg(g,c0+1,8,24)
    hseg(g,20,c0-5,c0-2,'='); hseg(g,16,c0+3,c0+6,'=')
    hseg(g,12,c0-5,c0-2,'='); hseg(g,8,c0+3,c0+6,'=')
hseg(g,5,20,40,'=')              # canopy walkway
hseg(g,5,48,60,'=')
fill(g,22,24,66,87)              # boss arena plateau
put(g,23,3,'P')
grounded(g,20,84,'D')
put(g,19,74,'B')
for r,c in [(23,8),(18,8),(10,8),(23,26),(18,20),(14,20),(23,44),(18,38),
            (10,38),(3,24),(3,32),(3,52),(3,58),(14,56),(10,56),(20,62)]: put(g,r,c,'*')
for r,c in [(14,26),(6,44),(14,44)]: put(g,r,c,'E')
for r,c in [(24,20),(24,56)]: grounded(g,r,c,'F')
grounded(g,24,38,'O')
grounded(g,4,36,'H'); grounded(g,24,62,'H')
grounded(g,24,10,'C'); grounded(g,21,68,'C')
add(g,"CANOPY HEIGHTS",12,0,(255,240,210),(235,255,215))

# ---------- L4 SUNKEN GROTTO (winding tunnels, door) ----------
g=new()
hseg(g,0,0,89); hseg(g,1,0,89); hseg(g,28,0,89); hseg(g,29,0,89)
vseg(g,0,2,27); vseg(g,1,2,27); vseg(g,88,2,27); vseg(g,89,2,27)
fill(g,6,7,2,70)                 # top shelf, gap right
fill(g,12,13,20,87)              # second shelf, gap left
fill(g,19,20,2,66)               # third shelf, gap right
hseg(g,26,2,87); hseg(g,27,2,87) # bottom floor
vseg(g,40,8,11); vseg(g,41,8,11)         # dividers
vseg(g,56,14,18); vseg(g,57,14,18)
vseg(g,28,21,25); vseg(g,29,21,25)
hseg(g,9,76,79,'='); hseg(g,16,8,11,'='); hseg(g,23,74,77,'=')
hseg(g,19,70,73,'='); hseg(g,12,14,17,'=')   # climb-back ladders (no one-way trips)
put(g,4,4,'P'); grounded(g,25,84,'D')
for r,c in [(4,14),(4,30),(4,48),(4,64),(4,80),(10,10),(10,30),(10,52),(10,70),
            (16,26),(16,44),(16,62),(16,80),(22,8),(22,40),(22,58),(25,14),(25,50)]: put(g,r,c,'*')
for r,c in [(4,40),(10,60),(16,36),(22,50)]: put(g,r,c,'E')
for r,c in [(11,26),(25,36)]: grounded(g,r,c,'F')
for r,c in [(17,50),(25,60)]: grounded(g,r,c,"O")
grounded(g,10,44,'H'); grounded(g,25,20,'H')
grounded(g,11,34,'C'); grounded(g,18,62,'C')
add(g,"SUNKEN GROTTO",12,-1,(110,170,195),(90,150,170))

# ---------- L5 WINDY CLIFFS (terraces up-right, possum boss) ----------
g=new()
steps=[(26,0,17),(22,14,31),(18,28,45),(14,42,59),(10,56,73),(8,70,89)]
for top,c0,c1 in steps: fill(g,top,29,c0,c1)
hseg(g,19,8,11,'='); hseg(g,15,22,25,'='); hseg(g,11,36,39,'='); hseg(g,7,50,53,'=')
put(g,24,4,'P')
grounded(g,7,86,'D')
put(g,5,78,'B')
for r,c in [(24,10),(20,18),(20,26),(17,10),(16,32),(16,40),(13,24),(12,46),
            (12,54),(9,38),(8,60),(8,66),(5,52),(10,24),(23,6),(6,74)]: put(g,r,c,'*')
for r,c in [(20,22),(16,36),(12,50),(8,64),(4,44)]: put(g,r,c,'E')
grounded(g,21,16,'F'); grounded(g,13,44,'F')
grounded(g,17,30,'O'); grounded(g,9,58,'O')
grounded(g,13,48,'H'); grounded(g,6,72,'H')
grounded(g,21,24,'C'); grounded(g,7,74,'C')
add(g,"WINDY CLIFFS",12,1,(255,225,185),(235,215,190))

# ---------- L6 RUINED HAMLET (broken ground, rooftops, door) ----------
g=new()
fill(g,24,29,0,19); fill(g,24,29,26,43); fill(g,24,29,50,65); fill(g,24,29,72,89)
hseg(g,21,20,25,'='); hseg(g,21,44,49,'='); hseg(g,21,66,71,'=')   # bridges over pits
for c0 in (8,32,56):                       # rooftop platform stacks
    hseg(g,19,c0,c0+5,'='); hseg(g,15,c0+8,c0+13,'='); hseg(g,11,c0+2,c0+7,'=')
hseg(g,7,40,52,'=')                        # high line
put(g,22,3,'P'); grounded(g,23,84,'D')
for r,c in [(22,12),(19,22),(18,10),(14,18),(10,6),(22,36),(18,34),(14,42),
            (10,34),(19,46),(22,60),(18,58),(14,66),(10,58),(19,68),(5,44),(5,48),(22,78)]: put(g,r,c,'*')
for r,c in [(16,26),(12,50),(16,74),(5,60)]: put(g,r,c,'E')
grounded(g,23,30,'F'); grounded(g,23,54,'F')
grounded(g,23,8,'O'); grounded(g,23,76,'O')
grounded(g,10,36,'H'); grounded(g,23,62,'H')
grounded(g,23,16,'C'); grounded(g,23,74,'C')
add(g,"RUINED HAMLET",12,-1,(235,185,160),(215,175,160))

# ---------- L7 THE UNDERROOT (maze, purple eagle boss) ----------
g=new()
hseg(g,0,0,89); hseg(g,1,0,89); hseg(g,28,0,89); hseg(g,29,0,89)
vseg(g,0,2,27); vseg(g,1,2,27); vseg(g,88,2,27); vseg(g,89,2,27)
fill(g,8,9,2,24); fill(g,8,9,32,56); fill(g,8,9,64,87)
fill(g,15,16,10,38); fill(g,15,16,46,74)
fill(g,21,22,2,30); fill(g,21,22,38,58)     # boss chamber right-bottom open
hseg(g,26,2,87); hseg(g,27,2,87)
vseg(g,30,10,14); vseg(g,31,10,14)
vseg(g,60,17,20); vseg(g,61,17,20)
hseg(g,12,26,29,'='); hseg(g,18,40,43,'='); hseg(g,24,32,35,'=')
put(g,5,4,'P'); grounded(g,25,84,'D')
put(g,24,70,'B')
for r,c in [(5,12),(5,28),(5,44),(5,60),(5,76),(12,14),(12,36),(12,52),(12,70),
            (19,6),(19,22),(19,50),(19,66),(25,10),(25,26),(25,44),(11,27),(23,33)]: put(g,r,c,'*')
for r,c in [(5,20),(12,44),(19,56),(5,68)]: put(g,r,c,'E')
grounded(g,14,20,'F'); grounded(g,25,16,'F')
grounded(g,7,40,'O'); grounded(g,20,52,'O')
grounded(g,14,34,'H'); grounded(g,25,38,'H')
grounded(g,7,14,'C'); grounded(g,20,46,'C')
add(g,"THE UNDERROOT",12,2,(150,125,195),(135,115,185))

# ---------- L8 SKYBRIDGE (island chain over the void, door) ----------
g=new()
isl=[(20,2,8),(22,14,19),(18,25,30),(21,36,41),(17,47,52),(20,58,63),(16,69,74),(19,80,87)]
for top,c0,c1 in isl: fill(g,top,top+1,c0,c1)
bridges=[(19,9,13),(20,20,24),(19,31,35),(19,42,46),(18,53,57),(18,64,68),(17,75,79)]
for row,c0,c1 in bridges: hseg(g,row,c0,c1,'=')
hseg(g,8,20,26,'='); hseg(g,6,40,46,'='); hseg(g,8,60,66,'=')      # bonus high line
hseg(g,14,18,21,'='); hseg(g,10,14,17,'=')                         # ladder up to it
hseg(g,7,32,35,'='); hseg(g,6,50,53,'=')                           # hops along the top
put(g,18,4,'P'); grounded(g,17,84,'D')
for r,c in [(18,16),(16,27),(19,38),(15,49),(18,60),(14,71),(17,82),
            (17,11),(18,22),(17,33),(17,44),(16,55),(16,66),(15,77),
            (6,22),(4,42),(6,62),(2,52),(2,32)]: put(g,r,c,'*')
for r,c in [(15,20),(13,40),(14,62),(11,78),(4,30),(4,56)]: put(g,r,c,'E')
grounded(g,16,28,'F'); grounded(g,15,70,'O')
grounded(g,5,42,'H'); grounded(g,15,50,'H')
grounded(g,20,38,'C'); grounded(g,15,73,'C')
add(g,"SKYBRIDGE",12,-1,(205,230,255),(215,235,255))

# ---------- L9 STORM ASCENT (vertical zigzag climb, door) ----------
g=new()
fill(g,26,29,2,16)
climb=[(23,20,26),(20,10,16),(17,22,28),(14,34,40),(17,46,52),(11,44,50),
       (8,32,38),(11,20,26),(5,24,30),(8,56,62),(5,66,72),(2,76,84)]
for top,c0,c1 in climb: fill(g,top,top+1,c0,c1)
hseg(g,24,30,33,'='); hseg(g,13,54,57,'='); hseg(g,6,40,43,'='); hseg(g,3,60,63,'=')
put(g,24,6,'P'); grounded(g,0,80,'D')
for r,c in [(24,12),(21,23),(18,13),(15,25),(12,37),(15,49),(9,47),(6,35),
            (9,23),(3,27),(6,59),(3,69),(1,78),(22,31),(11,55),(4,41),(1,61),(25,10)]: put(g,r,c,'*')
for r,c in [(20,30),(14,18),(10,40),(6,52),(2,44),(12,60),(4,74)]: put(g,r,c,'E')
grounded(g,16,24,'F'); grounded(g,7,60,'O')
grounded(g,13,36,'H'); grounded(g,4,68,'H')
grounded(g,16,26,'C'); grounded(g,7,58,'C')
add(g,"STORM ASCENT",12,-1,(160,180,225),(150,170,215))

# ---------- L10 TYRANT'S THRONE (sky arena, final boss) ----------
g=new()
fill(g,27,29,2,14)
islands=[(24,18,24),(21,28,33),(24,38,44),(18,44,49),(15,34,39),(12,24,30),
         (9,34,40),(12,50,56),(9,62,67),(15,58,63),(18,68,74),(12,76,82),(6,72,84)]
for top,c0,c1 in islands: fill(g,top,top+1,c0,c1)
for row,c0,c1 in [(22,12,15),(19,20,23),(16,28,31),(13,42,45),(10,46,49),
                  (7,54,57),(10,68,71),(4,64,67)]: hseg(g,row,c0,c1,'=')
put(g,25,5,'P')
grounded(g,5,82,'D')
put(g,3,76,'B')
for r,c in [(22,21),(19,31),(22,41),(16,46),(13,37),(10,27),(7,37),(10,53),
            (7,64),(13,60),(16,71),(10,79),(20,13),(11,43),(5,55),(25,10),(17,21),(20,86)]: put(g,r,c,'*')
for r,c in [(22,26),(17,40),(11,32),(10,58),(14,70),(4,50)]: put(g,r,c,'E')
grounded(g,5,74,'F'); grounded(g,20,32,'O')
grounded(g,9,47,'H'); grounded(g,3,65,'H')
grounded(g,20,29,'C'); grounded(g,8,63,'C')
add(g,"TYRANTS THRONE",0,3,(255,205,175),(255,215,195))

# ---------- emit C header ----------
out=[]
out.append("/* generated by genlevels.py - do not edit by hand */")
out.append("#define NUM_LEVELS 10")
out.append(f"#define MAP_W {W}")
out.append(f"#define MAP_H {H}")
out.append("")
out.append(f"static const char *LEVELS[NUM_LEVELS][MAP_H] = {{")
for s in levels:
    out.append("{")
    for row in s:
        out.append('"'+row+'",')
    out.append("},")
out.append("};")
out.append("")
out.append("typedef struct { const char *name; int req_gems; int boss_kind;")
out.append("                 Uint8 br, bg, bb, jr, jg, jb; } LevelCfg;")
out.append("static const LevelCfg LEVEL_CFG[NUM_LEVELS] = {")
for (name,req,boss,(br,bg,bb),(jr,jg,jb)) in cfgs:
    out.append(f'    {{"{name}", {req}, {boss}, {br},{bg},{bb}, {jr},{jg},{jb}}},')
out.append("};")
out.append("")
out.append("typedef struct { const char *name; int hp; } BossCfg;")
out.append("static const BossCfg BOSS_CFG[4] = {")
out.append('    {"MIRE KING", 24}, {"RUST FANG", 28},')
out.append('    {"GALE WRAITH", 34}, {"SKY TYRANT", 42},')
out.append("};")
open(__file__.rsplit("/tools/",1)[0]+"/src/levels.h","w").write("\n".join(out)+"\n")
print("levels.h written,", len(levels), "levels")
