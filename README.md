# AR-Cardgame

- Projektbeschreibung
- Requirements
    - Versionen
    - Installation
- Programm
    - Funktionaler Ablauf
    - Diskreptoren
    - Matcher
    - Homography & Transformation
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