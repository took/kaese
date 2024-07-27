from typing import Optional, List
import logging
from kaese.ai.ai import AI
from kaese.ai.ai_exception import AIException
from kaese.ai.better_ai import BetterAI
from kaese.ai.normal_ai import NormalAI
from kaese.ai.random_ai import RandomAI
from kaese.ai.simple_ai import SimpleAI
from kaese.gameboard.move import Move
from kaese.gameboard.gameboard import GameBoard


class Knoten:
    x = 0
    y = 0
    surroundings = 0

    def __init__(self, x, y, surroundings):
        self.x = x
        self.y = y
        self.surroundings = surroundings


class Path:
    x1 = 0
    y1 = 0
    surroundings1 = 0
    x2 = 0
    y2 = 0
    surroundings2 = 0
    totally_unused_till_now = True
    richtung = 0
    cluster_size = None

    def __init__(self, x1, y1, surroundings1, x2, y2, surroundings2):
        self.x1 = x1
        self.y1 = y1
        self.surroundings1 = surroundings1
        self.x2 = x2
        self.y2 = y2
        self.surroundings2 = surroundings2
        self.totally_unused_till_now = True


class ClusterAI(AI):
    """
    ClusterAI class represents an AI player that tries calculates the sizes of clusters to make an improved play.

    It inherits from the AI class.

    führe capture moves aus bis keine mehr verfügbar sind

    führe "better" Move aus (gib Gegner keine 3er solange möglich)




    erzeuge für jedes kästchen das noch nicht besetzt ist einen Knoten

    erzeuge für jede linie die noch nicht besetzt ist einen Path zwischen 2 knoten

    markiere kanten als clusterstartpunkt für die gilt:
    eines der kästchen der Kante hat 2 besetzt, das andere 1
    (es gibt noch weitere cluster: Die "rundlaufcluster" bei der es kein dediziertes startfeld gibt)


    für alle clusterstartpunkt pfade p tue:
      clusersize = 1
      markiere p als "nicht mehr totally unused till now"
      laufrichtung ist in richtung des kästchen das 2 besetzt hat.
      in laufrichtung schaue nach weiteren pfaden p2 aus dem kästchen raus die auf ein feld kommen mit 2 besetzten
      wenn keine vorhanden: speicher clusersize zu pfad p, continue with next p

      rufe rekursiv für p2 mit bekannter laufrichtung auf:
        clusersize += 1
        markiere p2 als "nicht mehr totally unused till now"
        in laufrichtung schaue nach weiteren pfaden p3 aus dem kästchen raus die auf ein feld kommen mit 2 besetzten
        wenn keine vorhanden: speicher clusersize zu pfad p, continue with next p
        rufe rekursiv für p3 mit bekannter laufrichtung sich selber

    wurde bereits ein cluster mit größe 1 gefunden? nutze ihn!

    solange es noch pfade gibt die totally unused sind:
      nimm den erst besten pfad p der noch nie benutzt wurde
      markiere p als "nicht mehr totally unused till now"
      cluster_size = 1
      laufrichtung ist egal
      in laufrichtung schaue nach weiteren pfaden p2 aus dem kästchen raus die auf ein feld kommen mit 2 besetzten
      wenn keine vorhanden: speicher clusersize zu pfad p, continue with next p

      rufe rekursiv für p2 mit bekannter laufrichtung auf:
        clusersize += 1
        markiere p2 als "nicht mehr totally unused till now"
        in laufrichtung schaue nach weiteren pfaden p3 aus dem kästchen raus die auf ein feld kommen mit 2 besetzten
        wenn keine vorhanden: speicher clusersize zu pfad p, continue with next p
        rufe rekursiv für p3 mit bekannter laufrichtung sich selber


    wähle cluster mit geringster größe aus und mach entsp zug
    (hier arbeiten wir nicht optimal in dem Sinne, das wir vll durch geschickte wahl eine clusters
    der sich mit einem anderen überschneidet, dafür sorgen können das wir am Ende des spiels den größten
    cluster erhalten und dadurch siegen ...)
    """

    tmp_used_pfade = []

    def get_next_move(self, gb: GameBoard, player: int) -> Move:
        """
        Calculates and returns the next move for the AI player.

        Args:
            gb (GameBoard): The game board object.
            player (int): The AI player's identifier.

        Returns:
            Optional[Move]: The next valid move found on the game board, or None if no moves are available.
        """
        player_ai = self.__class__.__name__

        # Check if any fields can be captured immediately and return the first found move
        capture_field_move = SimpleAI.get_capture_field_move(gb, player, player_ai)
        if capture_field_move:
            logging.info("%s Player %d: Used move from SimpleAI" % (player_ai, player))
            return capture_field_move

        if gb.current_player != player:
            raise AIException("ClusterAI: Wrong Player, can not handle this...")

        surroundings_count_matrix = NormalAI.get_field_with_count_of_surroundings(gb)

        # TODO versuche möglichst viele kleine cluster zu bauen

        # before using "any valid move", search for moves where surroundings<2
        move = BetterAI.get_better_moves(gb, player, surroundings_count_matrix, player_ai)
        if move:
            logging.info("%s Player %d: Used move from BetterAI" % (player_ai, player))
            return move

        # use cluster-finder
        z = ClusterAI.get_best_cluster_move(self, gb, player, surroundings_count_matrix, player_ai)
        if z:
            return z

        # Fallback: Use a random valid move
        logging.info("%s Player %d: Using fallback (a random valid move)" % (player_ai, player))
        return RandomAI.get_random_valid_move(gb, player, player_ai)

    def get_best_cluster_move(
            self,
            gb: GameBoard,
            player: int,
            surroundings_count_matrix: List[List[int]],
            player_ai: str = ""
    ) -> Optional[Move]:
        # erzeuge für jedes kästchen das noch nicht besetzt ist einen Knoten
        coordinates_to_paths = []
        for x in range(0, gb.size_x):
            column = []
            for y in range(0, gb.size_y):
                row = []
                column.append(row)
            coordinates_to_paths.append(column)

        # erzeuge für jede linie die noch nicht besetzt ist einen Path zwischen 2 knoten
        paths = []
        for x in range(0, gb.size_x):
            for y in range(0, gb.size_y):
                if gb.boxes[x][y].line_right == 0 and x + 1 < gb.size_x:
                    x2 = x + 1
                    y2 = y
                    p = Path(x, y, surroundings_count_matrix[x][y], x2, y2, surroundings_count_matrix[x2][y2])
                    paths.append(p)
                    coordinates_to_paths[x][y].append(p)
                    coordinates_to_paths[x2][y2].append(p)
                if gb.boxes[x][y].line_below == 0 and y + 1 < gb.size_y:
                    x2 = x
                    y2 = y + 1
                    p = Path(x, y, surroundings_count_matrix[x][y], x2, y2, surroundings_count_matrix[x2][y2])
                    paths.append(p)
                    coordinates_to_paths[x][y].append(p)
                    coordinates_to_paths[x2][y2].append(p)
        for i, p in enumerate(paths):
            self.debug("pfade x%d y%d nach x%d y%d" % (p.x1, p.y1, p.x2, p.y2), 2)

        cluster_start_punkte = []
        for i, p in enumerate(paths):
            # markiere kanten als clusterstartpunkt für die gilt:
            # eines der kästchen der kante hat 2 besetzt, das andere 1
            # (es gibt noch weitere cluster: die "rundlaufcluster" bei der es kein dediziertes startfeld gibt)
            if p.surroundings1 == 1 and p.surroundings2 == 2:
                p.richtung = 2
                cluster_start_punkte.append(p)
            if p.surroundings1 == 2 and p.surroundings2 == 1:
                p.richtung = 1
                cluster_start_punkte.append(p)

        # For all cluster starting point paths p, do the following:
        for i, p in enumerate(cluster_start_punkte):
            self.debug(" check cstp p.x1=%d p.y1=%d" % (p.x1, p.y1), 3)
            # mark p as "not anymore totally unused till now"
            p.totally_unused_till_now = False
            # The direction of movement is towards the box occupied by 2 lines.
            # Look for additional paths p2 in the direction of movement that extend from the box, leading to a square
            # with 2 occupied spots.
            if p.richtung == 1:
                old_x = p.x2
                old_y = p.y2
                next_x = p.x1
                next_y = p.y1
                next_surroundings = p.surroundings1
            elif p.richtung == 2:
                old_x = p.x1
                old_y = p.y1
                next_x = p.x2
                next_y = p.y2
                next_surroundings = p.surroundings2
            else:
                raise AIException("Invalid direction %d" % p.richtung)
            if next_surroundings == 2:
                p2 = ClusterAI.get_pfad_that_is_not_linking_back(
                    self,
                    coordinates_to_paths,
                    old_x,
                    old_y,
                    next_x,
                    next_y
                )
                # TODO Throw exception if more than one path is returned
                if p2 is None:
                    # If not paths exists, return immediately cluster move p that fetches a cluster of size 1
                    self.debug("return 1 x%d y%d old_x%d, old_y%d, next_x%d, next_y%d" % (
                        p.x1, p.y1, old_x, old_y, next_x, next_y), 2)
                    logging.info("%s Player %d greedily choose to use first single-cluster (size %d) it found at: "
                                 "From %d,%d to %d,%d since there is no path that is not linking back"
                                 % (player_ai, player, p.cluster_size, old_x, old_y, next_x, next_y))
                    return ClusterAI.get_move(old_x, old_y, next_x, next_y, player, player_ai)
                else:
                    p.cluster_size = ClusterAI.get_best_cluster_move_rekursion(
                        self,
                        p,
                        1,
                        coordinates_to_paths,
                        next_x,
                        next_y,
                        p2
                    )
            else:
                # wenn keine vorhanden: return sofort 1er cluster zug p
                self.debug("return 2 x%d y%d old_x%d, old_y%d, next_x%d, next_y%d" % (
                    p.x1, p.y1, old_x, old_y, next_x, next_y), 2)
                logging.info("%s Player %d greedily choose to use first single-cluster (size %d, next borders: %d) it "
                             "found at: From %d,%d to %d,%d since there is a path with not 2 borders on next field"
                             % (player_ai, player, p.cluster_size, next_surroundings, old_x, old_y, next_x, next_y))
                return ClusterAI.get_move(old_x, old_y, next_x, next_y, player, player_ai)

        for i, p in enumerate(cluster_start_punkte):
            self.debug("cluster starting points cs%d x%d y%d to x%d y%d (rev=%d)" % (
                p.cluster_size, p.x1, p.y1, p.x2, p.y2, p.richtung), 1)
        # solange es noch pfade gibt die totally unused sind:
        self.debug("check unused paths...", 1)
        p = ClusterAI.get_totally_unused_paths(paths)
        while p:
            self.tmp_used_pfade = []
            # - nimm den erst besten pfad p der noch nie benutzt wurde
            # - markiere p als "nicht mehr totally unused till now"
            p.totally_unused_till_now = False
            # - laufrichtung ist egal, in laufrichtung schaue nach weiteren pfaden p2 aus dem kästchen raus die auf ein
            # feld kommen mit 2 besetzten
            # - wenn keine vorhanden: speicher cluster_size zu pfad p, continue with next p
            old_x = p.x1
            old_y = p.y1
            next_x = p.x2
            next_y = p.y2
            next_surroundings = p.surroundings2

            # rufe rekursiv für p2 mit bekannter laufrichtung auf:
            if next_surroundings == 2:
                p2 = ClusterAI.get_pfad_that_is_not_linking_back(
                    self,
                    coordinates_to_paths,
                    old_x,
                    old_y,
                    next_x,
                    next_y
                )
                # TODO hier ggf auch in die andere richtung laufen wenn 2 züge zurückkamen, exception bei 3...
                if p2:
                    p.cluster_size = ClusterAI.get_best_cluster_move_rekursion(
                        self,
                        p,
                        1,
                        coordinates_to_paths,
                        next_x,
                        next_y,
                        p2,
                        save_tmp_used_paths=True
                    )
                else:
                    # wenn keine vorhanden: speicher cluster_size zu pfad p, continue with next p
                    p.cluster_size = 1
            else:
                # wenn keine vorhanden: speicher cluster_size zu pfad p, continue with next p
                p.cluster_size = 1

            # andere richtung auch prüfen
            # old_x = p.x2
            # old_y = p.y2
            # next_x = p.x1
            # next_y = p.y1
            # next_surroundings = p.surroundings1
            # rufe rekursiv für p2 mit bekannter laufrichtung auf:
            # if next_surroundings == 2:
            # p2 = self.getPfadThatsNotLinkingBack(coordinates_to_paths, old_x, old_y, next_x, next_y)
            # if not p2 is None:
            # p.cluster_size += self.getBestClusterMoveRekursion(p, 1, coordinates_to_paths, next_x, next_y,
            #   p2, save_tmp_used_paths=True)
            # else:
            # wenn keine vorhanden: speicher cluster_size zu pfad p, continue with next p
            # p.cluster_size += 1
            # else:
            # wenn keine vorhanden: speicher cluster_size zu pfad p, continue with next p
            # p.cluster_size += 1

            p = ClusterAI.get_totally_unused_paths(paths)
        ClusterAI.tmp_used_pfade = []

        # wähle cluster mit geringster größe aus und mache entsprechenden zug
        self.debug("wähle cluster mit geringster größe aus...", 1)
        smallest_found = 1000000
        smallest_pfad = None
        smallest_pfade = []
        for i, p in enumerate(paths):
            if p.cluster_size:
                self.debug("pfade cs%d x%d y%d nach x%d y%d" % (p.cluster_size, p.x1, p.y1, p.x2, p.y2), 2)
                if smallest_found > p.cluster_size:
                    smallest_found = p.cluster_size
                    smallest_pfad = p
                if smallest_found >= p.cluster_size:
                    smallest_pfade.append(p)
        p = smallest_pfad
        # p = random.choice(smallest_pfade)
        z = None
        if smallest_pfad:
            z = ClusterAI.get_move(p.x1, p.y1, p.x2, p.y2, player, player_ai)
            logging.info(
                "%s Player %d choose to give smallest cluster to opponent with size %d: From %d,%d to %d,%d "
                "(direction=%d)" % (player_ai, player, p.cluster_size, p.x1, p.y1, p.x2, p.y2, p.richtung)
            )
        return z

    @staticmethod
    def get_totally_unused_paths(pfade: List[Path]) -> Optional[Path]:
        for i, p in enumerate(pfade):
            if p.totally_unused_till_now:
                return p
        return None

    @staticmethod
    def get_move(x: int, y: int, next_x: int, next_y: int, player: int, player_ai="") -> Move:
        if x + 1 == next_x:
            horizontal = 0
        elif y + 1 == next_y:
            horizontal = 1
        elif x - 1 == next_x:
            horizontal = 0
            x = next_x
            y = next_y
        elif y - 1 == next_y:
            horizontal = 1
            x = next_x
            y = next_y
        else:
            raise AIException("Cannot determine direction for move.")
        return Move(x, y, horizontal, player, player_ai)

    @staticmethod
    def is_origin_p(p: Path, p2: Path) -> bool:
        if p.x1 == p2.x1 and p.y1 == p2.y1 and p.x2 == p2.x2 and p.y2 == p2.y2:
            return True
        if p.x1 == p2.x2 and p.y1 == p2.y2 and p.x2 == p2.x1 and p.y2 == p2.y1:
            return True
        return False

    def is_pfad_in_tmp_used_pfade_list(self, p: Path) -> bool:
        for i, p2 in enumerate(self.tmp_used_pfade):
            if ClusterAI.is_origin_p(p, p2):
                return True
        return False

    def get_pfad_that_is_not_linking_back(
            self,
            coordinates_to_paths: List[List[List[Path]]],
            old_x: int,
            old_y: int,
            x: int,
            y: int
    ) -> Optional[Path]:
        for i, p in enumerate(coordinates_to_paths[x][y]):
            self.debug("old_x=%d old_y=%d p.x1=%d p.y1=%d p.x2=%d p.y2=%d" % (old_x, old_y, p.x1, p.y1, p.x2, p.y2),
                       3)
            if len(self.tmp_used_pfade) > 0:
                if ClusterAI.is_pfad_in_tmp_used_pfade_list(self, p):
                    continue
            if (p.x1 != old_x or p.y1 != old_y) and (p.x2 != old_x or p.y2 != old_y):
                # TODO hier? die erstmal sammeln und wenn es mehr als einer ist muss der gespeichert werden
                #  und später die cs dazuadiert werden!
                return p
        return None

    def get_best_cluster_move_rekursion(
            self,
            p: Path,
            cluster_size: int,
            coordinates_to_paths: List[List[List[Path]]],
            old_x: int,
            old_y: int,
            p2: Path,
            save_tmp_used_paths: bool = False
    ) -> int:
        cluster_size += 1
        self.debug(" check cstp rek p2.x1=%d p2.y1=%d" % (p2.x1, p2.y1), 3)
        p2.totally_unused_till_now = False
        if save_tmp_used_paths:
            self.tmp_used_pfade.append(p2)
        # rufe rekursiv für p2 mit bekannter laufrichtung auf:
        # cluster_size += 1
        # markiere p2 als "nicht mehr totally unused till now"
        # in laufrichtung schaue nach weiteren pfaden p3 aus dem kästchen raus die auf ein feld kommen mit 2 besetzten
        # wenn keine vorhanden: speicher cluster_size zu pfad p, continue with next p
        # rufe rekursiv für p3 mit bekannter laufrichtung sich selber
        if old_x == p2.x1 and old_y == p2.y1:
            next_x = p2.x2
            next_y = p2.y2
            next_surroundings = p2.surroundings2
        else:
            next_x = p2.x1
            next_y = p2.y1
            next_surroundings = p2.surroundings1
        if next_surroundings == 2:
            p3 = ClusterAI.get_pfad_that_is_not_linking_back(self, coordinates_to_paths, old_x, old_y, next_x, next_y)
            # TODO ggf mehrere pfade durchlaufen und aufaddieren
            if p3 and not ClusterAI.is_origin_p(p, p3):
                return ClusterAI.get_best_cluster_move_rekursion(
                    self,
                    p,
                    cluster_size,
                    coordinates_to_paths,
                    next_x,
                    next_y,
                    p3
                )
            else:
                # wenn keine vorhanden: speicher cluster_size zu pfad p, continue with next p
                self.debug("ret cluster_size a cs%d x%d y%d nach x%d y%d (rev=%d)" % (
                    cluster_size, p.x1, p.y1, p.x2, p.y2, p.richtung), 2)
                return cluster_size
        else:
            self.debug("ret cluster_size-1 b cs%d x%d y%d nach x%d y%d (rev=%d), outlines%d" % (
                cluster_size, p.x1, p.y1, p.x2, p.y2, p.richtung, next_surroundings), 2)
            return cluster_size - 1
