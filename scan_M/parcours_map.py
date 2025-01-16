import map_class
import parcours_v2 as parcours_class

map = map_class.Map()
parcours = parcours_class.Parcours("parcours.txt")

map.run()

if map.parcours:
    map._map_quit()
    parcours.boucle_principale()






