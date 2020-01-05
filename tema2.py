import math
import psutil
import os
import time
import sys
import stopit

timeout = int(sys.argv[1])
nrSolutiiCautate = int(sys.argv[2])
fisier_input = str(sys.argv[3])

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


def calcMaxMem():
    global maxMem
    process = psutil.Process(os.getpid())
    memCurenta = process.memory_info()[0]
    if maxMem < memCurenta:
        maxMem = memCurenta


class NodParcurgere:
    def __init__(self, info, cost, parinte):
        self.info = info
        self.parinte = parinte  # parintele din arborele de parcurgere
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
            insecte = self.info['greutate_max'] - self.parinte.info['greutate_max'] + 1
            sir += 'Broasca a mancat {} insecte. Greutate broscuta: {}'.format(insecte, self.info['greutate_max'])
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
        greutate_max_curenta = nodCurent.info['greutate_max']
        xy_curent = nodCurent.info['xy']
        listaSuccesori = []
        # if greutate_max_curenta - 1 == 0:
        #     return listaSuccesori
        for i in range(self.nrNoduri):
            if nodCurent.contineInDrum(noduri[i]):
                continue
            greutate_max = self.noduri[i]['greutate_max']
            xy = self.noduri[i]['xy']
            insecte = self.noduri[i]['insecte']
            id_frunza = self.noduri[i]['id_frunza']

            if d_euclidiana(xy_curent, xy) > greutate_max_curenta / 3:
                continue

            greutate_noua = greutate_max_curenta - 1
            for i in range(insecte):
                if greutate_noua <= greutate_max:
                    greutate_noua += 1
                    insecte -= 1

            nodSuccesor = NodParcurgere(dict(id_frunza=id_frunza, xy=xy, insecte=insecte, greutate_max=greutate_noua),
                                        nodCurent.cost + d_euclidiana(xy_curent, xy), nodCurent)
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
        if nodCurent.info['greutate_max'] == 1:
            break

        if test_scop(nodCurent):
            nodCurent.afisDrum()
            print("#"*40)
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                continua = False
        lSuccesori = graph.genereazaSuccesori(nodCurent)
        for s in lSuccesori:
            inserare_in_coada_prioritati(c, s)
        calcMaxMem()
    return "Algoritmul UCS a fost finalizat"


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
print(uniform_cost(gr, timeout=timeout))
t2 = time.time()
milis = round(1000 * (t2 - t1))
print("Memorie maxim folosita la UCS: {}. Timp: {}\n\n\n".format(maxMem, milis))























