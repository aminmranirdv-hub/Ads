# Règles pour les vidéos IA (plaquiste / peinture)

Ces règles viennent des retours de l'utilisateur sur la première vidéo. Il faut les appliquer à chaque vidéo.

## Ordre obligatoire des étapes (doublage / cloison placo), donné par l'utilisateur
1. Mur nu
2. Ferraillage partout avant toute plaque : rails haut et bas, montants (fourrures) verticaux, appuis ou équerres fixés au mur pour tenir les montants, comme sur un vrai chantier
3. Laine de verre posée entre les montants
4. Pose des plaques et vissage
5. Bandes à joint, rebouchage des vis et des vides
6. Ponçage des bandes
7. Première couche (blanc)
8. Deuxième couche (blanc), et c'est fini

## Exactitude du métier : vérifier chaque plan avant de le montrer
- **Bandes à joint** : la bande en papier doit être visible et posée dans l'enduit, et il ne doit plus rester de joint vide ni de vis apparente à la fin de l'étape.
- **Ponçage** : on ne ponce que là où il y a des bandes et de l'enduit secs (bandes blanches visibles sur la plaque). On ponce avec une ponceuse girafe ou une cale, jamais avec un pulvérisateur.
- **Sous-couche** : après la sous-couche, le mur est entièrement BLANC et le reste dans tous les plans suivants. Il ne doit jamais redevenir vert ou gris comme la plaque.
- **Finition** : la couleur finale part du mur blanc. Si la finition est blanche, le mur final est blanc.
- L'état du mur ne recule jamais d'un plan à l'autre (nu → plaques → bandes → poncé → blanc → peint).
- Si un plan est faux, je le corrige avant de livrer. Je ne le minimise jamais en le qualifiant de « subtil ».

## Méthode pour économiser les crédits (Magnific)
1. Générer d'abord une **image fixe par état du mur** (environ 135 crédits chacune) et les vérifier.
2. Animer chaque étape avec **Kling 2.5, 1080p, 5 s, image de départ et image de fin** (environ 325 crédits). L'image de fin d'une étape sert d'image de départ à la suivante, ce qui garantit la continuité.
3. Ne jamais générer de vidéo multi-plans de 30 s d'un seul coup (13 200 crédits, et l'état du mur n'est pas suivi d'un plan à l'autre).
4. Estimer le coût avec `simulate_cost` et annoncer le total avant de lancer.
5. Pour la voix off, utiliser la voix clonée « Ma voix FR (plaquiste) » (Magnific `audio_tts`, `source=mine`).
6. Activer « Info IA » à la publication.
