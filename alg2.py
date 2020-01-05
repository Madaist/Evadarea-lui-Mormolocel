import math

fisier_input = 'input_date17.txt'
start = None
with open(fisier_input, 'r') as fin:
    raza = int(fin.readline().strip('\n'))
    greutate_initiala_broasca = int(fin.readline().strip('\n'))
    id_frunza_start = fin.readline().strip('\n')
    noduri = []
    for line in fin:
        line = line.split()
        nod = dict(id_frunza=line[0], xy=(int(line[1]), int(line[2])), insecte=int(line[3]),
                   greutate_max=int(line[4]))
        if line[0] == id_frunza_start:
            start = nod
        else:
            noduri.append(nod)
    print("Raza: ", raza)
    print("Greutate initiala broscuta: ", greutate_initiala_broasca)
    print("Id frunza start: ", id_frunza_start)
    print("Noduri: ")
    print(noduri)


def d_euclidiana(xy1, xy2):
    return math.sqrt((xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2)


def d_manhattan(xy1, xy2):
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])  # |x1 - x2| + |y1 - y2|


def scrie_in_fisier(output):
    fisier_output = fisier_input.replace('input', 'output')
    with open(fisier_output, "a") as fout:
        fout.write(output)


def scop(nodCurent):
    if nodCurent['xy'][0] ** 2 + nodCurent['xy'][1] ** 2 == raza ** 2:  # x^2 + y^2 = raza^2
        return True
    return False


class Nod:
    def __init__(self, info, h, insecteMancate=None, greutateCurenta=None):
        self.greutateCurenta = greutateCurenta
        self.insecteMancate = insecteMancate
        self.info = info
        self.h = h

    def __str__(self):
        return "(" + str(self.info) + ", h=" + str(self.h) + ")"

    def __repr__(self):
        return "(" + str(self.info) + ", h=" + str(self.h) + ")"


# noduri cu euristica banala
noduri_graf = [Nod(start, float('inf'))]
noduri_scop = []
for nod in noduri:
    if scop(nod):
        noduri_graf.append(Nod(nod, 0))
        noduri_scop.append(nod)
    else:
        noduri_graf.append(Nod(nod, 1))

# noduri cu euristica data de distanta euclidiana
noduri_graf_euclid = [Nod(start, float('inf'))]
for nod in noduri:
    if scop(nod):
        noduri_graf_euclid.append(Nod(nod, 0))
    else:
        ds = []
        for nod_scop in noduri_scop:
            ds.append(d_euclidiana(nod['xy'], nod_scop['xy']))
        noduri_graf_euclid.append(Nod(nod, min(ds)))

# noduri cu euristica data de distanta Manhattan
noduri_graf_manhattan = [Nod(start, float('inf'))]
for nod in noduri:
    if scop(nod):
        noduri_graf_manhattan.append(Nod(nod, 0))
    else:
        ds = []
        for nod_scop in noduri_scop:
            ds.append(d_manhattan(nod['xy'], nod_scop['xy']))
        noduri_graf_manhattan.append(Nod(nod, min(ds)))


class Graf:
    def __init__(self, noduri_graf, noduri_scop):
        self.noduri = noduri_graf
        self.nod_start = self.noduri[0]
        self.noduri_scop = noduri_scop

    def scop(self, nod):  # testeaza daca nodul dat ca parametru este un nod scop
        if nod.info in noduri_scop:
            return True
        return False

    def genereazaSuccesori(self, nodCurent):
        greutate_inainte_de_saritura = nodCurent.greutateCurenta
        if greutate_inainte_de_saritura is None:
            greutate_inainte_de_saritura = nodCurent.info['greutate_max']
        xy_curent = nodCurent.info['xy']
        listaSuccesori = []
        if greutate_inainte_de_saritura - 1 == 0:
            return listaSuccesori
        for i in range(len(self.noduri)):
            if self.noduri[i].info != nodCurent.info:
                greutate_max = self.noduri[i].info['greutate_max']
                xy = self.noduri[i].info['xy']
                insecte_frunza = self.noduri[i].info['insecte']

                if d_euclidiana(xy_curent, xy) > greutate_inainte_de_saritura / 3:
                    continue

                greutate_dupa_saritura = greutate_inainte_de_saritura - 1
                insecteMancate = 0

                while greutate_dupa_saritura < greutate_max and insecteMancate < insecte_frunza:
                    greutate_dupa_saritura += 1
                    insecteMancate += 1

                cost = d_euclidiana(xy_curent, xy)

                nodSuccesor = Nod(self.noduri[i].info, self.noduri[i].h, insecteMancate, greutate_dupa_saritura)
                listaSuccesori.append((nodSuccesor, cost))
        return listaSuccesori


class NodParcurgere:

    def __init__(self, nod_graf, succesori=None, parinte=None, g=0, f=None):
        if succesori is None:
            succesori = []
        self.nod_graf = nod_graf
        self.succesori = succesori
        self.parinte = parinte
        self.g = g
        if f is None:
            self.f = self.g + self.nod_graf.h
        else:
            self.f = f

    def obtineDrum(self):
        drum = [self]
        nod = self
        while nod.parinte is not None:
            drum.insert(0, nod.parinte)
            nod = nod.parinte
        return drum

    def afis_adrum(self):
        drum = self.obtineDrum()
        for nod in drum:
            print('{}){}'.format(drum.index(nod) + 1, nod))
            scrie_in_fisier('{}){}\n'.format(drum.index(nod) + 1, nod))
        print('{})Broscuta a ajuns la mal in {} sarituri.'.format(len(drum) + 1, len(drum)))
        scrie_in_fisier('{})Broscuta a ajuns la mal in {} sarituri.\n\n\n'.format(len(drum) + 1, len(drum)))
        scrie_in_fisier('#' * 10 + '\n' * 3)
        return len(drum)

    def contine_in_drum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if infoNodNou.info == nodDrum.nod_graf.info:
                return True
            nodDrum = nodDrum.parinte
        return False

    def sirAfisare(self):
        sir = ""
        if self.parinte is None:
            sir += 'Broscuta se afla pe frunza initiala {}.\n'.format(self.nod_graf.info['id_frunza'])
            sir += 'Greutate broscuta: {}'.format(str(self.nod_graf.info['greutate_max']))
        else:
            stare_trecuta = self.parinte.nod_graf.info['id_frunza'] + str(self.parinte.nod_graf.info['xy'])
            stare_curenta = self.nod_graf.info['id_frunza'] + str(self.nod_graf.info['xy'])
            sir += 'Broscuta a sarit de la {} la {}.\n'.format(stare_trecuta, stare_curenta)
            sir += 'Broasca a mancat {} insecte. Greutate broscuta: {}'.format(self.nod_graf.insecteMancate,
                                                                               self.nod_graf.greutateCurenta)
        return sir

    def __repr__(self):
        return self.sirAfisare()

    def __str__(self):
        return self.sirAfisare()


def in_lista(l, nod):
    for x in l:
        if x.nod_graf.info == nod.info:
            return x
    return None


def a_star(graf):
    rad_arbore = NodParcurgere(nod_graf=graf.nod_start)
    open = [rad_arbore]
    closed = []
    while len(open) > 0:
        nod_curent = open.pop(0)
        closed.append(nod_curent)  # il adaugam in closed pt ca urmeaza sa l expandez
        if graf.scop(
                nod_curent.nod_graf):  # testez daca nodul extras din lista open este nod scop (si daca da, ies din bucla while)
            break
        l_succesori = graf.genereazaSuccesori(nod_curent.nod_graf)
        for (nod, cost) in l_succesori:
            if not nod_curent.contine_in_drum(nod):
                # verific daca se afla in closed
                x = in_lista(closed, nod)
                g_succesor = nod_curent.g + cost  # calculam noul g al nodului
                f = g_succesor + nod.h
                if x is not None:
                    if f < nod_curent.f:  # daca f ul calculat acum este mai mic decat cel de dinainte,
                        # setam noul parinte si recalcumal g si f
                        x.parinte = nod_curent
                        x.g = g_succesor
                        x.f = f
                        print(x)
                else:
                    # verific daca se afla in open
                    x = in_lista(open, nod)
                    if x is not None:
                        if x.g > g_succesor:
                            x.parinte = nod_curent
                            x.g = g_succesor
                            x.f = f
                            print(x)
                    else:  # cand nu e nici in closed nici in open, adica nu a fost vizitat, il adaug la lista
                        # nodurilor de expandat
                        nod_cautare = NodParcurgere(nod_graf=nod, parinte=nod_curent,
                                                    g=g_succesor)  # se calculeaza f automat in constructor
                        open.append(nod_cautare)
        open.sort(key=lambda x: (x.f, -x.g))  # pentru f-uri egale sortam descrescator dupa g
        # pentru x (care va fi pe rand fiecare element din open), sorteaza dupa f; daca f urile sunt egale,
        # sorteaza dupa g, descrescator pentru ca il preferam pe cel din care stim mai mult, adica unde g-ul este cel
        # mai mare
    # iese din while daca a gasit o solutie sau daca len(c)a devenit 0 (am verificat toate nodurile si niciunul n a
    # fost scop)
    if len(open) == 0:
        print("Lista open e vida, nu avem drum de la nodul start la nodul scop")
    else:
        print("Drum de cost minim: " + str(nod_curent.afis_adrum()))


if __name__ == "__main__":
    problema_h_banala = Graf(noduri_graf, noduri_scop)
    a_star(problema_h_banala)

    problema_h_euclid = Graf(noduri_graf_euclid, noduri_scop)
    a_star(problema_h_euclid)

    problema_h_manhattan = Graf(noduri_graf_manhattan, noduri_scop)
    a_star(problema_h_manhattan)
