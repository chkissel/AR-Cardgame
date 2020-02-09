# AR-Cardgame

- Projektbeschreibung
- Requirements
    - Versionen
    - Installation
- Programm
    - Funktionaler Ablauf
    - Feature Deskriptoren & Matching
    - Homographie & Transformation
- Rendering


### Projektbeschreibung

Das Projekt 'AR-Cardgame' erweitert das beliebte 'Trading Card'-Spielprinzip um eine neue Erlebnisebene. Mit Hilfe von Augmented Reality(AR)-Techniken werden Figuren auf den Spielkarten eingeblendet. Außerdem wird die Lage der Karte, und somit ihr Zustand, automatisch erkannt. So befinden sich Karten, die parallel zum Gegner ausgerichtet liegen, in einer Art Verteidigungsposition.
Das zu diesem Zweck geschriebene Python-Programm bedient sich verschiedener Frameworks und Bibliotheken. Diese sowie der generelle Programmaufbau werden im Folgenden beschrieben. Weiterhin wird evaluiert welche Faktoren einen Einfluss auf die Performance und Stabilität des Programms nehmen. Zum Schluss werden noch einige Technologien zum Rendering der AR-Inhalte vorgestellt.

![alt text](./assets/gifs/ORB_1_card.gif)

### Requirements
#### Versionen

Folgende Dependencies besitzt das Programm:

| Package       | Version       |
| ------------- |:-------------:|
| Python        | 3.7.5         |
| NumPy         | 1.17.4        |
| OpenCV-Python | 3.4.2.17      |  
| Panda3D       | 1.10.5        |

#### Installation

Für die Installation der Dependencies wird der Pip-Paketmanager empfohlen:

```bash
sudo apt-get update

sudo apt-get install python3

pip install opencv-python numpy Panda3D

```

### Programm
#### Funktionaler Ablauf

Das Programm startet mit einer Initialisierungsphase in der die verschiedenen verwendeten Klassen geladen werden. Zudem werden benötigte Spielkarten geladen, das Modell sowie Bild geladen und deren Features extrahiert. Karten die während der Laufzeit erkannt werden sollen werden in eine Liste geschrieben durch die im Loop des Programmes iteriert wird.
Im Loop wird das aktuelle Kamerabild ausgelesen und Features daraus extrahiert. Anschließend werden für jede Karte in der Kartenliste folgende Aktionen durchgeführt.

- Kartenfeatures mit Bildfeatures matchen
- Bei genug Matches die Homographiematrix ermitteln
- Eigenschaften der Kartenrotation bestimmen
- Rechteck um die Karte zeichnen
- Projektionsmatrix berechnen
- 3D Modell rendern

#### Feature Deskriptoren & Matching

Bildfeatures können mit verschiedenen Algorithmen bestimmt werden. Für dieses Projekt wurden die Algorithmen SIFT, ORB und SURF angewandt und verglichen. Dabei war sowohl die Performance als auch die Qualität der Erkennung relevant. Die durchschnittliche Framerate wurde während der Laufzeit erhoben und kann schwanken, die Qualitätseinschätzung erfolgt subjektiv.

| #Karten | Algorithmen                     | Performance | Quality (1-5)   |
| ------- |:-------------------------------:|:-----------:|:---------------:|
| 1       | ORB + BF Matching/knn-Matching  | 26 FPS      | (2) POOR        |
| 1       | SIFT + BF Matching              | 10 FPS      | (2) POOR        |
| 1       | SIFT + BF knn-Matching          | 9.5 FPS     | (5) EXCELLENT   |
| 1       | SIFT (nfeatures 200)            | 9.5 FPS     | (5) EXCELLENT   |
| 1       | SIFT + Flann knn-Matching       | 9 FPS       | (5) EXCELLENT   |
| 1       | SURF + BF knn-Matching          | 12 FPS      | (3) MEDIOCRE    |
| ------- |:-------------------------------:|:-----------:|:---------------:|
| 2       | ORB + BF Matching/knn-Matching  | 20 FPS      | (1) NOT WORKING
| 2       | SIFT +  BF knn-Matching         | 5.5 FPS     | (5) EXCELLENT   |
| 2       | SIFT +  Flann knn-Matching      | 5 FPS       | (5) EXCELLENT   |
| 2       | SIFT (nfeatures 200)            | 8 FPS       | (5) EXCELLENT   |
| 2       | SURF + Flann knn-Matching       | 8 FPS       | (3) MEDIOCRE    |
| 2       | SURF + BF knn-Matching          | 8 FPS       | (3) MEDIOCRE    |
| ------- |:-------------------------------:|:-----------:|:---------------:|
| 4       | SIFT (nfeatures 200)            | 8 FPS       | (1) NOT WORKING |
| 4       | SIFT + BF knn-Matching          | 3 FPS       | (5) EXCELLENT   |

Hier lassen sich mehrere Erkenntnisse für unsere Anwendung extrahieren. Der verwendete Matching-Algorithmus hat wenig bis keine Auswirkungen auf Performance oder Qualität.
SURF ist schneller als SIFT und erzeugt qualitativ bessere Ergebnisse als ORB, allerdings ist der Algorithmus trotzdem insgesamt sehr langsam ohne die Ergebnisse soweit zu verbessern das die längere Berechnungszeit gerechtfertigt ist.
ORB bietet mit Abstand die beste Performance. Die Ergebnisse sind allerdings sehr instabil und zeigen starkes Flackern. Dieser Effekt wurde durch ein Smoothing über die Zeit versucht auszugleichen, damit wurde das Bild minimal ruhiger. Zudem kann ORB bereits bei zwei Karten gleichzeitig nicht mehr angewendet werden. Die zusätzliche Karte wird nur in seltenen Fällen erkannt und lässt sich aufgrund von Überschneidungen zur ersten Karte nicht identifizieren.

VIDEO ORB

SIFT bietet in jedem Fall exzellente Ergebnisse. Die Erkennung ist extrem stabil und verlässlich. Dies kommt bringt Abzüge in der Performance. Bereits bei einer einzigen Karte ist das Resultat mit knapp 10 Frames die Sekunde nur noch bedingt geeignet. Besonders bei mehreren Karten leidet die Performance enorm. Diesem Effekt wurde durch eine Reduktion der extrahierten Features entgegen gewirkt, allerdings finden sich dadurch bei mehreren Karten nicht mehr genug Features um jede Karte zu identifizieren.

VIDEO SIFT

Abschließend lässt sich hier festhalten, das keiner der Algorithmen alle Ansprüche erfüllen konnte. Das liegt natürlich auch daran, dass die Karten als Ersatz für AR Marker wenig geeignet sind. Die Karten weisen abseits des Bildes viele Überschneidungen in Text und Symbolik auf. Hier ist es vor allem für ORB schwierig zwischen den Karten zu unterscheiden. Wird lediglich das Bild der Karte verwendet findet ORB wiederum nicht genug Features um die Karte zu erkennen. SIFT bietet eine sehr sichere Erkennung auf Kosten der Performance. Möglicherweise lässt sich die Erkennung mit SIFT soweit optimieren als das die gefundenen Punkte nicht neu gematcht sondern im Bild verfolgt werden.

#### Homographie & Transformation

Aus den gefundenen Matches im Bild wird die Homographie ermittelt. Mithilfe Dieser können wir die Position und Lage der Karte bestimmen. In dem Szenario welches wir betrachten spielen zwei Spieler gegeneinander. Jedem Spieler ist eine Seite zugeteilt, ihre Karten zeigen damit mit ihrer Kopf-Seite Richtung Gegenspieler. Die Kamera filmt von oben auf das Szenario. Durch die statische Kamera welche von oben auf die Ebene zeigt lassen sich Informationen bereits aus der Homographie Matrix extrahieren da man sich hier sozusagen in einem 2D Szenario befindet. Dabei wird die Rotation um X betrachtet. Der Winkel wird ermittelt und ausgewertet. Alle Karten die einen negativen Winkel aufweisen gehören so zu einem Spieler, alle mit einem positiven Rotationswinkel zum Gegenspieler. Dies geht von der Annahme aus das die Karten gegeneinander gelegt werden, also 90° beziehungsweise -90° rotiert. Ob eine Karte getappt, also eingedreht, und damit als deaktiviert gilt, wird ebenfalls am Rotationswinkel um X abgelesen. Hierzu muss die Karte mindestens um 45° beziehungsweise -45° eingedreht sein.

```python
# Check if card belongs to left or right player
if homography[0,1] < 0:
    color = p1_color
else:
    color = p2_color

# Check if card is active or inactive
h_degree = np.degrees(math.atan2(homography[0,1] , homography[1,1]))
if (h_degree > 45 and h_degree < 135) or (h_degree < -45 and h_degree > -135):
    active = True

width = 3 if active else 1
```

Zur Augmentierung des 3D-Modells wird aus der Homographiematrix eine Projektionsmatrix errechnet. Um den den Duell-Effekt des Kartenspieles zu verstärken sollen hierbei alle Figuren entsprechend ihrer Spielerzugehörigkeit zum Gegenspieler gedreht sein. Dazu wird nach auslesen der Homograhie, diese mit einer Rotationsmatrix verrechnet. Es wird zwar der gewünschte Effekt erzielt, allerdings entsteht hier abhängig von der Rotation der Karte ein Offset zum Kartenmittelpunkt. Ein Herausrechnen der Verschiebung war uns nicht möglich.

```python
# rot_1 and rot_2 are normalized rotations from homography matrix
...
# Turns the model to the left / right based on card direction
# while giving the expected result, an offset to the center occurs
theta = np.radians(90)
row_1 = [np.cos(theta), -np.sin(theta), 0]
row_2 = [np.sin(theta), np.cos(theta), 0]
row_3 = [0, 0, 1]
rot_mat = np.array([row_1, row_2, row_3])

rotations = np.array([rot_1, rot_2, [0, 0, 1]]).T
rotations = rot_mat * rotations

rot_1 = rotations[:, 0]
rot_2 = rotations[:, 1]
...
```

### Rendering

Nachdem die Funktionalität des AR-Tracking stand, sollte noch das Rendering der 3D-Modelle verbessert werden. So bietet nur OpenCV alleine nicht die Möglichkeit die Objekte mit Texturen zu versehen oder sie zu beleuchten. Daher wurden drei Frameworks zum Rendering in Python ausprobiert: PyGame, PyOpenGL und Panda3D.
Alle drei Programmbibliothek enthalten Module zum Abspielen und Steuern von Grafikelementen. Ein weiteres Kriterium war die einfache Integrierung der OpenCV-Funktionen in die Render-Pipeline. Alle drei Kandidaten erfüllten diese Voraussetzung, allerdings gestaltete sich die Übersetzung der Zahlenräume und Koordinatensystem in die jeweilige Umgebung als äußerst schwierig. Deshalb wird in diesem Kapitel eine nur halbfunktionale Implementierung vorgestellt.
Der Prototyp wurde letztendlich in Panda3D umgesetzt. Die Entscheidung für Panda3D fiel insbesondere auf Grund der großen Community und guten Dokumentation, die das Arbeiten mit dem Framework extrem erleichtern.

Ein Panda3D-Programm geht immer von einer Klasse aus, die das ShowBase-Objekt erbt. In der __init__()-Funktion der Klasse befindet sich der 'Scene Graph'. In diesem werden alle Objekte definiert die während der Laufzeit gerendert werden sollen.

```python
class Game(ShowBase):
    ...
    def __init__(self):
    ShowBase.__init__(self)
    ...
```

Hier werden auch die bereits bekannten Klassen, die für das AR-Tracking benötigt werden initiiert. Zusätzlich zum Teil aus den vorangegangen Kapitel wird das über OpenCV abgerufene Kamerabild in eine Textur geschrieben, die später als Hintergrundbild gerendert wird.

```python
shape = img.shape  
self.img = cv2.flip(img, 0)
self.tex = Texture("detect")
self.tex.setup2dTexture(shape[1], shape[0],
                        Texture.TUnsignedByte, Texture.FRgb)
p = PTAUchar.emptyArray(0)
p.setData(self.img)
self.tex.setRamImage(CPTAUchar(p))

...

self.test = OnscreenImage(parent=self.render2d, image=self.tex, scale=1.0, pos=(0, 0, 0))

```

Die Modelle können in Panda3D ebenfalls problemlos mit Texturen geladen werden. Außerdem können Modelle über Animationen verfügen, die während der Laufzeit gestartet und gestoppt werden können.

```python
self.model = Actor("models/panda-model",
                   {"walk": "models/panda-walk4"})
```

Um eine Funktion für jedes Frame erneut aufzurufen nutzt Panda3D das Task-Prinzip. In diesen Tasks können Funktionen, wie zum Beispiel in diesem Fall das Verarbeiten und Rendern des Kamerabildes, definiert werden.

```python
    ...
    self.taskMgr.add(self.loop, "loop")

def loop(self, task):
    self.game()
    self.test.setTexture(self.tex)
    ...
    return task.cont
```
