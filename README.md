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
    - panda3d
    - OpenGL
    - PyGame


### Projektbeschreibung

Das Projekt 'AR-Cardgame' erweitert das beliebte 'Trading Card'-Spielprinzip um eine neue Erlebnisebene. Mit Hilfe von Augmented Reality(AR)-Techniken werden Figuren auf den Spielkarten eingeblendet. Außerdem wird die Lage der Karte, und somit ihr Zustand, automatisch erkannt. 
Das zu diesem Zweck geschriebene Python-Programm bedient sich verschiedener Frameworks und Bibliotheken. Diese sowie der generelle Programmaufbau werden im Folgenden beschrieben. Weiterhin wird untersucht welche Faktoren einen Einfluss auf die Performance und Stabilität des Programms nehmen. Zum Schluss werden noch einige Technologien zum Rendering der AR-Inhalte evaluiert.


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
