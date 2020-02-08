from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import cv2
from PIL import Image
import numpy as np
from webcam import Webcam
from objloader import *
from featureClass import FeatureClass
from geometryClass import GeometryClass
from card import Card


class OpenGLGlyphs:
    # constants
    INVERSE_MATRIX = np.array([[1.0, 1.0, 1.0, 1.0],
                               [-1.0, -1.0, -1.0, -1.0],
                               [-1.0, -1.0, -1.0, -1.0],
                               [1.0, 1.0, 1.0, 1.0]])

    def __init__(self):
        # initialise webcam and start thread
        self.webcam = Webcam()
        self.webcam.start()

        # Initialize instances
        self.features = FeatureClass(min_matches=20, max_matches=75)
        self.geometry = GeometryClass()

        self.card = Card('card_1', 50, (27, 27, 211), self.features)

        # initialise shapes
        self.cone = None


        # initialise texture
        self.texture_background = None

    def _init_gl(self, Width, Height):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glDisable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(33.7, 1.3, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

        # assign shapes
        self.cone = OBJ('assets/card_1.obj')


        # assign texture
        glEnable(GL_TEXTURE_2D)
        self.texture_background = glGenTextures(1)

    def _draw_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()

        # get image from webcam
        image = self.webcam.get_current_frame()

        image, projection, translation = self.open_cv(image)

        # convert image to OpenGL texture format
        bg_image = cv2.flip(image, 0)
        bg_image = Image.fromarray(bg_image)
        ix = bg_image.size[0]
        iy = bg_image.size[1]
        bg_image = bg_image.tobytes("raw", "BGRX", 0, -1)

        glDepthMask(0)
        # create background texture
        glBindTexture(GL_TEXTURE_2D, self.texture_background)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, bg_image)

        # draw background
        glBindTexture(GL_TEXTURE_2D, self.texture_background)
        glPushMatrix()
        #glScalef(100000, 100000, 100000)
        glTranslatef(0.0, 0.0, -10.0)
        self._draw_background()
        glPopMatrix()

        # handle glyphs
        image = self._handle_glyphs(image, projection, translation)

        glutSwapBuffers()

    def open_cv(self, image):
        kp, des = self.features.extract(image)
        matches = self.features.match(des, self.card.des)

        if len(matches) > self.features.MINMATCHES:
            # Calculate homography matrix
            H = self.geometry.computeHomography(kp, self.card.kp, matches)
            frame = self.geometry.drawRect(image, self.card.img, self.card.color, H)
            projection, translation = self.geometry.calcProjection(H)
            projection = np.append(projection, [[0, 0, 0, 1]], axis=0)
            # frame = render(frame, card.obj, card.scale, card.color, card.img, projection, False)
        return frame, projection, translation

    def _handle_glyphs(self, image, view_matrix, translation):

        """
        # attempt to detect glyphs
        glyphs = []

        try:
            glyphs = self.glyphs.detect(image)
        except Exception as ex:
            print(ex)

        if not glyphs:
            return

        for glyph in glyphs:

            rvecs, tvecs, glyph_name = glyph

            # build view matrix
            rmtx = cv2.Rodrigues(rvecs)[0]

            view_matrix = np.array([[rmtx[0][0], rmtx[0][1], rmtx[0][2], tvecs[0]],
                                    [rmtx[1][0], rmtx[1][1], rmtx[1][2], tvecs[1]],
                                    [rmtx[2][0], rmtx[2][1], rmtx[2][2], tvecs[2]],
                                    [0.0, 0.0, 0.0, 1.0]])

            view_matrix = view_matrix * self.INVERSE_MATRIX

            view_matrix = np.transpose(view_matrix)

            # load view matrix and draw shape
            glPushMatrix()
            glLoadMatrixd(view_matrix)

            if glyph_name == SHAPE_CONE:
                glCallList(self.cone.gl_list)
            elif glyph_name == SHAPE_SPHERE:
                glCallList(self.sphere.gl_list)

            glPopMatrix()
        """
        #print(view_matrix)
        #view_matrix = matrix * self.INVERSE_MATRIX

        #view_matrix = np.transpose(view_matrix)
        glPushMatrix()
        view_matrix = view_matrix * 0.1
        #glLoadMatrixd(view_matrix)
        #print(translation)
        #glScaled(1,1,1)
        translation = translation * 0.1
        glTranslatef(-1*(translation[0]),translation[1],translation[2])
        #glTranslatef(translation[0]/10,translation[1]/10, translation[2]/10)
        glCallList(self.cone.gl_list)
        glPopMatrix()

    def _draw_background(self):
        # draw background
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0);
        glVertex3f(-4.0, -3.0, 0.0)
        glTexCoord2f(1.0, 1.0);
        glVertex3f(4.0, -3.0, 0.0)
        glTexCoord2f(1.0, 0.0);
        glVertex3f(4.0, 3.0, 0.0)
        glTexCoord2f(0.0, 0.0);
        glVertex3f(-4.0, 3.0, 0.0)
        glEnd()

    def main(self):
        # setup and run OpenGL
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
        glutInitWindowSize(1280, 720)
        glutInitWindowPosition(800, 400)
        self.window_id = glutCreateWindow("OpenGL Glyphs")
        glutDisplayFunc(self._draw_scene)
        glutIdleFunc(self._draw_scene)
        self._init_gl(1280, 720)

        glutMainLoop()


# run an instance of OpenGL Glyphs
openGLGlyphs = OpenGLGlyphs()
openGLGlyphs.main()