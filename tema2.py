import math
import psutil
import os
import time
import sys
import stopit

# fisierul 2 blocheaza ucs ul
# fisierul 1 si 3 nu au solutii
# input_Date5  si 6 au lungime 10

timeout = int(sys.argv[1])
nrSolutiiCautate = int(sys.argv[2])
fisier_input = str(sys.argv[3])
start = None


def citire_fisier():
    global start
    with open(fisier_input, 'r') as fin:
        raza = float(fin.readline().strip('\n'))
        greutate_initiala_broasca = int(fin.readline().strip('\n'))
        id_frunza_start = fin.readline().strip('\n')
        noduri = []
        for line in fin:
            cuvinte_linie = line.split()
            nod = dict(id_frunza=cuvinte_linie[0], xy=(float(cuvinte_linie[1]), float(cuvinte_linie[2])),
                       insecte=int(cuvinte_linie[3]), greutate_max=int(cuvinte_linie[4]))
            if cuvinte_linie[0] == id_frunza_start:
                start = nod
            noduri.append(nod)
        print("Raza: {}\nGreutate initiala broscuta:{}\n".format(raza, greutate_initiala_broasca))
        print("Id frunza start: {}\nNoduri:\n{}\n\n".format(id_frunza_start, noduri))
        return raza, greutate_initiala_broasca, id_frunza_start, noduri


raza, greutate_initiala_broasca, id_frunza_start, noduri = citire_fisier()


def d_euclidiana(xy1, xy2):
    return math.sqrt((xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2)


def calcMaxMem():
    global maxMem
    process = psutil.Process(os.getpid())
    memCurenta = process.memory_info()[0]
    if maxMem < memCurenta:
        maxMem = memCurenta


class NodParcurgere:
    def __init__(self, info, cost, parinte, insecteMancate=None, greutateCurenta=None):
        self.greutateCurenta = greutateCurenta
        self.insecteMancate = insecteMancate
        self.info = info
        self.parinte = parinte
        self.cost = cost

    def obtineDrum(self):
        drum = [self]
        nod = self
        while nod.parinte is not None:
            drum.insert(0, nod.parinte)
            nod = nod.parinte
        return drum

    def afisDrum(self):
        drum = self.obtineDrum()
        for nod in drum:
            print('{}){}'.format(drum.index(nod) + 1, nod))
            scrie_in_fisier('{}){}\n'.format(drum.index(nod) + 1, nod))
        print('{})Broscuta a ajuns la mal in {} sarituri.'.format(len(drum) + 1, len(drum)))
        scrie_in_fisier('{})Broscuta a ajuns la mal in {} sarituri.\n\n\n'.format(len(drum) + 1, len(drum)))
        scrie_in_fisier('#' * 10 + '\n' * 3)
        return len(drum)

    def sirAfisare(self):
        sir = ""
        if self.parinte is None:
            sir += 'Broscuta se afla pe frunza initiala {}.\n'.format(self.info['id_frunza'])
            sir += 'Greutate broscuta: {}'.format(str(self.info['greutate_max']))
        else:
            stare_trecuta = self.parinte.info['id_frunza'] + str(self.parinte.info['xy'])
            stare_curenta = self.info['id_frunza'] + str(self.info['xy'])
            sir += 'Broscuta a sarit de la {} la {}.\n'.format(stare_trecuta, stare_curenta)
            sir += 'Broasca a mancat {} insecte. Greutate broscuta: {}'.format(self.insecteMancate,
                                                                               self.greutateCurenta)
        return sir

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if infoNodNou['xy'] == nodDrum.info['xy']:
                return True
            nodDrum = nodDrum.parinte

        return False

    def __repr__(self):
        return self.sirAfisare()

    def __str__(self):
        return self.sirAfisare()


class Graph:
    def __init__(self, noduri, start):
        self.noduri = noduri
        self.nrNoduri = len(noduri)
        self.start = start

    def genereazaSuccesori(self, nodCurent):
        greutate_inainte_de_saritura = nodCurent.greutateCurenta
        if greutate_inainte_de_saritura is None:
            greutate_inainte_de_saritura = greutate_initiala_broasca
        listaSuccesori = []
        if greutate_inainte_de_saritura - 1 == 0:
            return listaSuccesori

        for i in range(len(self.noduri)):
            nod_i = self.noduri[i]
            if nodCurent.contineInDrum(nod_i):
                continue
            if d_euclidiana(nodCurent.info['xy'], nod_i['xy']) > greutate_inainte_de_saritura / 3:
                continue
            greutate_dupa_saritura = greutate_inainte_de_saritura - 1
            insecteMancate = 0

            while greutate_dupa_saritura < nod_i['greutate_max'] and insecteMancate < nod_i['insecte']:
                greutate_dupa_saritura += 1
                insecteMancate += 1
            nod_i['insecte'] -= insecteMancate

            nodSuccesor = NodParcurgere(nod_i, nodCurent.cost + d_euclidiana(nodCurent.info['xy'],
                                                                             nod_i['xy']), nodCurent, insecteMancate,
                                        greutate_dupa_saritura)
            listaSuccesori.append(nodSuccesor)
        return listaSuccesori

    def __repr__(self):
        sir = ""
        for (k, v) in self.__dict__.items():
            sir += "{} = {}\n".format(k, v)
        return sir


##############################################################################################
#                                 Initializare problema                                      #
##############################################################################################

gr = Graph(noduri, start)


def test_scop(nodCurent):
    if nodCurent.info['xy'][0] ** 2 + nodCurent.info['xy'][1] ** 2 == raza ** 2:  # x^2 + y^2 = raza^2
        return True
    return False


@stopit.threading_timeoutable(default="Algoritmul UCS a intrat in timeout")
def uniform_cost(graph):
    global nrSolutiiCautate
    c = [NodParcurgere(start, 0, None)]
    continua = True
    while len(c) > 0 and continua:
        nodCurent = c.pop(0)

        if test_scop(nodCurent):
            nodCurent.afisDrum()
            print("#" * 40)
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                continua = False
        lSuccesori = graph.genereazaSuccesori(nodCurent)
        for s in lSuccesori:
            inserare_in_coada_prioritati(c, s)
        calcMaxMem()
    return "Algoritmul UCS a fost finalizat\n"


def inserare_in_coada_prioritati(c, s):
    i = 0
    ok = 0
    while True:
        for i in range(len(c)):
            if c[i].cost >= s.cost:
                c.insert(i, s)
                ok = 1
        if ok == 1:
            break
        else:
            c.insert(i + 1, s)
            break


def scrie_in_fisier(output):
    fisier_output = fisier_input.replace('input', 'output')
    with open(fisier_output, "a") as fout:
        fout.write(output)


maxMem = 0
t1 = time.time()
print(uniform_cost(gr))
t2 = time.time()
milis = round(1000 * (t2 - t1))
print("Memorie maxim folosita la UCS: {}. Timp: {}\n\n\n".format(maxMem, milis))

# ##################################### A STAR ###################################################
raza, greutate_initiala_broasca, id_frunza_start, noduri = citire_fisier()


def d_manhattan(xy1, xy2):
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])  # |x1 - x2| + |y1 - y2|


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
noduri_graf_euclid = [Nod(start, float('inf'))]  # consideram ca nodul de start are h = infinit
for nod in noduri:
    if scop(nod):
        noduri_graf_euclid.append(Nod(nod, 0))  # consideram ca nodurile scop au h = 0
    else:  # celelalte noduri au h = distanta euclidiana
        distante = []
        for nod_scop in noduri_scop:  # calculam distantele de la nod la nodurile scop pentru a o alege apoi pe cea mai mica
            distante.append(d_euclidiana(nod['xy'], nod_scop['xy']))
        if len(distante) != 0:  # daca avem noduri scop
            noduri_graf_euclid.append(
                Nod(nod, min(distante)))  # consideram h = cea mai mica distanta de la nod la un nod scop
        else:  # daca nu avem noduri scop
            noduri_graf_euclid.append(Nod(nod, 1))  # consideram h = 1

# noduri cu euristica data de distanta Manhattan
noduri_graf_manhattan = [Nod(start, float('inf'))]
for nod in noduri:
    if scop(nod):
        noduri_graf_manhattan.append(Nod(nod, 0))
    else:
        distante = []
        for nod_scop in noduri_scop:
            distante.append(d_manhattan(nod['xy'], nod_scop['xy']))
        if len(distante) != 0:
            noduri_graf_manhattan.append(Nod(nod, min(distante)))
        else:
            noduri_graf_manhattan.append(Nod(nod, 1))


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
        listaSuccesori = []
        if greutate_inainte_de_saritura - 1 == 0:
            return listaSuccesori
        for i in range(len(self.noduri)):
            if self.noduri[i].info != nodCurent.info:
                nod_i = self.noduri[i]
                if d_euclidiana(nodCurent.info['xy'], nod_i.info['xy']) > greutate_inainte_de_saritura / 3:
                    continue

                greutate_dupa_saritura = greutate_inainte_de_saritura - 1
                insecteMancate = 0

                while greutate_dupa_saritura < nod_i.info['greutate_max'] and insecteMancate < nod_i.info['insecte']:
                    greutate_dupa_saritura += 1
                    insecteMancate += 1
                cost = d_euclidiana(nodCurent.info['xy'], nod_i.info['xy'])
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
        # return len(drum)

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


@stopit.threading_timeoutable(default="Algoritmul A STAR a intrat in timeout")
def a_star(graf):
    rad_arbore = NodParcurgere(nod_graf=graf.nod_start)
    open = [rad_arbore]
    closed = []
    while len(open) > 0:
        # nod_curent = open.pop(0)
        nod_curent = open[0]  # nu l am scos din coada pentru ca daca este scop dar este ultimul din coada, coada va
        # deveni vida iar la iesirea din while, va afisa ca nu avem solutii
        closed.append(nod_curent)  # il adaugam in closed pt ca urmeaza sa l expandez
        # testez daca nodul extras din lista open este nod scop (si daca da, ies din bucla while)
        if graf.scop(nod_curent.nod_graf):
            break
        nod_curent = open.pop(0)
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
        calcMaxMem()
    # iese din while daca a gasit o solutie sau daca len(c)a devenit 0 (am verificat toate nodurile si niciunul n a
    # fost scop)
    if len(open) == 0:
        print("Lista open e vida, nu avem drum de la nodul start la nodul scop")
    else:
        nod_curent.afis_adrum()
    return "Algoritmul A star s-a finalizat cu succes"


if __name__ == "__main__":
    maxMem = 0
    print("#" * 30 + " A STAR CU EURISTICA BANALA " + "#" * 30)
    problema_h_banala = Graf(noduri_graf, noduri_scop)
    t1 = time.time()
    print(a_star(problema_h_banala))
    t2 = time.time()
    milis = round(1000 * (t2 - t1))
    print("Memorie maxim folosita la A star: {}. Timp: {}\n\n\n".format(maxMem, milis))

    maxMem = 0
    print("#" * 30 + " A STAR CU DISTANTA EUCLIDIANA " + "#" * 30)
    problema_h_euclid = Graf(noduri_graf_euclid, noduri_scop)
    t1 = time.time()
    print(a_star(problema_h_euclid, timeout=timeout))
    t2 = time.time()
    milis = round(1000 * (t2 - t1))
    print("Memorie maxim folosita la A star: {}. Timp: {}\n\n\n".format(maxMem, milis))

    maxMem = 0
    print("#" * 30 + " A STAR CU DISTANTA MANHATTAN " + "#" * 30)
    problema_h_manhattan = Graf(noduri_graf_manhattan, noduri_scop)
    t1 = time.time()
    print(a_star(problema_h_manhattan, timeout=timeout))
    t2 = time.time()
    milis = round(1000 * (t2 - t1))
    print("Memorie maxim folosita la A star: {}. Timp: {}\n\n\n".format(maxMem, milis))
