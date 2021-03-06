# AR-Cardgame

- [Projektbeschreibung](#Projektbeschreibung)
- [Requirements](#Requirements)
    - [Versionen](#Versionen)
    - [Installation](#Installation)
- [Programm](#Programm)
    - [Funktionaler Ablauf](#Funktionaler-Ablauf)
    - [Feature Deskriptoren & Matching](#Feature-Deskriptoren-&-Matching)
    - [Homographie & Transformation](#Homographie-&-Transformation)
- [Rendering](#Rendering)


### Projektbeschreibung

Das Projekt 'AR-Cardgame' erweitert das beliebte 'Trading Card'-Spielprinzip um eine neue Erlebnisebene. Mit Hilfe von Augmented Reality(AR)-Techniken werden Figuren auf den Spielkarten eingeblendet. Außerdem wird die Lage der Karte, und somit ihr Zustand, automatisch erkannt. So befinden sich Karten, die parallel zum Gegner ausgerichtet liegen, in einer Art Verteidigungsposition.
Das zu diesem Zweck geschriebene Python-Programm bedient sich verschiedener Frameworks und Bibliotheken. Diese sowie der generelle Programmaufbau werden im Folgenden beschrieben. Weiterhin wird evaluiert welche Faktoren einen Einfluss auf die Performance und Stabilität des Programms nehmen. Zum Schluss werden noch einige Technologien zum Rendering der AR-Inhalte vorgestellt.


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

Das Programm wird über die Konsole ausgeführt:
```bash
python main.py
```
Ebenso die Render-Demo:
```bash
python pandaMain.py
```

### Programm
#### Funktionaler Ablauf

Das Programm startet durch das Drücken der Nummerntaste **'1'** mit einer Initialisierungsphase in der die verschiedenen verwendeten Klassen geladen werden. Zudem werden benötigte Spielkarten, das Modell sowie Bild geladen und deren Features extrahiert. Karten die während der Laufzeit erkannt werden sollen in eine Liste geschrieben werden, durch die im Loop des Programmes iteriert wird.
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
| ------- |---------------------------------|-------------|-----------------|
| 2       | ORB + BF Matching/knn-Matching  | 20 FPS      | (1) NOT WORKING
| 2       | SIFT +  BF knn-Matching         | 5.5 FPS     | (5) EXCELLENT   |
| 2       | SIFT +  Flann knn-Matching      | 5 FPS       | (5) EXCELLENT   |
| 2       | SIFT (nfeatures 200)            | 8 FPS       | (5) EXCELLENT   |
| 2       | SURF + Flann knn-Matching       | 8 FPS       | (3) MEDIOCRE    |
| 2       | SURF + BF knn-Matching          | 8 FPS       | (3) MEDIOCRE    |
| ------- |---------------------------------|-------------|-----------------|
| 4       | SIFT (nfeatures 200)            | 8 FPS       | (1) NOT WORKING |
| 4       | SIFT + BF knn-Matching          | 3 FPS       | (5) EXCELLENT   |

Hier lassen sich mehrere Erkenntnisse für unsere Anwendung extrahieren. Der verwendete Matching-Algorithmus hat wenig bis keine Auswirkungen auf Performance oder Qualität.
SURF ist schneller als SIFT und erzeugt qualitativ bessere Ergebnisse als ORB, allerdings ist der Algorithmus trotzdem insgesamt sehr langsam ohne die Ergebnisse soweit zu verbessern, dass die längere Berechnungszeit gerechtfertigt wäre.
ORB bietet mit Abstand die beste Performance. Die Ergebnisse sind allerdings sehr instabil und zeigen starkes Flackern. Dieser Effekt wurde durch ein Smoothing über die Zeit versucht auszugleichen, damit wurde das Bild minimal ruhiger. Zudem kann ORB bereits bei zwei Karten gleichzeitig nicht mehr angewendet werden. Die zusätzliche Karte wird nur in seltenen Fällen erkannt und lässt sich aufgrund von Überschneidungen zur ersten Karte nicht identifizieren.

![alt text](./assets/gifs/ORB_1_card_small.gif)

SIFT bietet in jedem Fall exzellente Ergebnisse. Die Erkennung ist extrem stabil und verlässlich. Dies kommt bringt Abzüge in der Performance. Bereits bei einer einzigen Karte ist das Resultat mit knapp 10 Frames die Sekunde nur noch bedingt geeignet. Besonders bei mehreren Karten leidet die Performance enorm. Diesem Effekt wurde durch eine Reduktion der extrahierten Features entgegen gewirkt, allerdings finden sich dadurch bei mehreren Karten nicht mehr genug Features um jede Karte zu identifizieren.

![alt text](./assets/gifs/SIFT_1_card_bf_knnmatch.gif)

Abschließend lässt sich hier festhalten, dass keiner der Algorithmen alle Ansprüche erfüllen konnte. Das liegt natürlich auch daran, dass die Karten als Ersatz für AR Marker wenig geeignet sind. Die Karten weisen abseits des Bildes viele Überschneidungen in Text und Symbolik auf. Hier ist es vor allem für ORB schwierig zwischen den Karten zu unterscheiden. Wird lediglich das Bild der Karte verwendet findet ORB wiederum nicht genug Features um die Karte zu erkennen. SIFT bietet eine sehr sichere Erkennung auf Kosten der Performance. Möglicherweise lässt sich die Erkennung mit SIFT soweit optimieren, dass die gefundenen Punkte nicht neu gematcht sondern im Bild verfolgt werden.

#### Homographie & Transformation

Aus den gefundenen Matches im Bild wird die Homographie ermittelt. Mithilfe Dieser können wir die Position und Lage der Karte bestimmen. 

![alt text](./assets/images/homography.png)

*https://forums.fast.ai/t/how-to-transform-4-points-parameter-matrix-to-homography-matrix/5770*

In dem Szenario welches wir betrachten spielen zwei Spieler gegeneinander. Jedem Spieler ist eine Seite zugeteilt, ihre Karten zeigen damit mit ihrer Kopf-Seite Richtung Gegenspieler. Die Kamera filmt von oben auf das Szenario. Durch die statische Kamera welche von oben auf die Ebene zeigt lassen sich Informationen bereits aus der 3*3 Homographiematrix extrahieren da man sich hier sozusagen in einem 2D Szenario befindet. Dabei wird die Rotation um X betrachtet. Der Winkel wird ermittelt und ausgewertet. Alle Karten die einen negativen Winkel aufweisen gehören so zu einem Spieler, alle mit einem positiven Rotationswinkel zum Gegenspieler. Dies geht von der Annahme aus das die Karten gegeneinander gelegt werden, also 90° beziehungsweise -90° rotiert. Ob eine Karte getappt, also eingedreht, und damit als deaktiviert gilt, wird ebenfalls am Rotationswinkel um X abgelesen. Hierzu muss die Karte mindestens um 45° beziehungsweise -45° eingedreht sein.

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

Neben der graphischen Darstellung dieser Informationen in dem Rechteck der Homographie werden die Informationen in einer Texteinblendung am oberen Bildschirmrand angegeben. Hier wird die Anzahl der Karten pro Spieler angezeigt und wie viele von diesen sich in einem aktiven Zustand befinden.

```python
def writeInformation(self, img, status):
      text = 'Player 1: ' + str(status[0]) + ' cards, ' + str(status[1]) + ' active | ' + 'Player 2: ' + str(status[2]) + ' cards, ' + str(status[3]) + ' active'
      drawn = cv2.putText(img, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 125, 0))
      return drawn
```

Zur Augmentierung des 3D-Modells wird aus Homographiematrix(H) eine Projektionsmatrix (P), die der Kameraposition entspricht, errechnet. Diese setzt sich zusammen aus:

**P = K [ R | t ]**

Wobei **K** die intrinsischen Kameraparameter sind, **t** die Translation darstellt und in **R** die Rotationen enthalten sind. Die Ableitung aus **H** ist möglich, da beide Matrizen die gleichen Informationen enthalten. So sind die ersten beiden Spalten von **H** identisch mit den jeweiligen Spalten in **R** und die dritte Spalte von **H** entspricht **t**. Die dritte Spalte von **R**, die Tiefe, kann nun mit dem Wissen, dass die Achsen orthogonal aufeinander stehen, aus dem Kreuzprodukt von Spalte eins und zwei berechnet werden. 

**R [ 3:] = R [ :1, ] ⊗ R [ 1:2, ]**

Somit ist die Projektionsmatrix komplett und wird wiederum verwendet, um ein 3D Objekt darzustellen. In einer frühen Phase des Programmes wurde dafür ein .obj Modell anhand der gegebenen Faces und Vertices ohne Beleuchtung direkt in OpenCV gezeichnet. Diverse Anpassungen der Projektionsmatrix im Nachhinein stellten sich als besonders knifflig dar, siehe Kapitel Rendering. Auch in OpenCV erzeugten beispielsweise nachträgliche Rotationen Verschiebungen, welche wegen der geplanten Überführung in ein Rendering Framework nicht weiter verfolgt wurden.

```python
# projection is the projection matrix without additional rotation
...
# Turns the card around the given degree
# however the model now has a noticable offset to the center
theta = np.radians(90)
row_1 = [np.cos(theta), -np.sin(theta), 0]
row_2 = [np.sin(theta), np.cos(theta), 0]
row_3 = [0, 0, 1]
rot_z = np.matrix([row_1, row_2, row_3])
projection = projection * rot_z
...
```

Die finale Anwendung, ohne Texteinbledungen, zeigt in etwa das folgende Bild.

![alt text](./assets/gifs/SIFT_full_demo.gif)


### Rendering

Nachdem die Funktionalität des AR-Tracking stand, sollte noch das Rendering der 3D-Modelle verbessert werden. So bietet nur OpenCV alleine nicht die Möglichkeit die Objekte mit Texturen zu versehen oder sie zu beleuchten. Daher wurden drei Frameworks zum Rendering in Python ausprobiert: PyGame, PyOpenGL und Panda3D.
Alle drei Programmbibliothek enthalten Module zum Abspielen und Steuern von Grafikelementen. Ein weiteres Kriterium war die einfache Integrierung der OpenCV-Funktionen in die Render-Pipeline. Alle drei Kandidaten erfüllten diese Voraussetzung, allerdings gestaltete sich die Übersetzung der Zahlenräume und Koordinatensystem in die jeweilige Umgebung als äußerst schwierig. Deshalb wird in diesem Kapitel eine nur halbfunktionale Implementierung vorgestellt.
Der Prototyp wurde letztendlich in Panda3D umgesetzt. Die Entscheidung für Panda3D fiel insbesondere auf Grund der großen Community und guten Dokumentation, die das Arbeiten mit dem Framework extrem erleichtern.

![alt text](./assets/gifs/panda_final.gif)

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
