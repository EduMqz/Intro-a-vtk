import os
import vtk
from caja_vtk import Caja
from montacargas import Montacargas

class EscenaAlmacen:
    """
    Clase que representa una escena de almacén con varios montacargas y una rampa.
    """
    
    def __init__(self):
        """
        Inicializa la escena con tres montacargas y una rampa.
        """
        self._renderizador = vtk.vtkRenderer()
        self._renderizador.SetBackground(0.1, 0.15, 0.2)  # Azul oscuro
        
        # Crear tres montacargas con diferentes tamaños de cajas
        self._montacargas = []
        self._crear_montacargas()
        
        # Crear la rampa
        self._rampa_actor = self._crear_rampa(6.0, 3.0, 2.0)  # 6 largo x 3 ancho x 2 alto
        self._renderizador.AddActor(self._rampa_actor)
        
        # Configurar cámara para visualizar toda la escena
        self._configurar_camara()
    
    def _crear_montacargas(self):
        """
        Crea tres montacargas con diferentes dimensiones de cajas.
        """
        # Definir las dimensiones para cada montacargas
        dimensiones = [
            (1.0, 1.0, 1.0),  # Montacargas 1: cajas de 1x1x1
            (2.0, 1.0, 1.0),  # Montacargas 2: cajas de 2x1x1
            (1.0, 2.0, 1.0),  # Montacargas 3: cajas de 1x2x1
        ]
        
        # Posiciones para cada montacargas
        posiciones = [
            (-7.0, -5.0, 0.0),  # Izquierda
            (0.0, -5.0, 0.0),    # Centro
            (7.0, -5.0, 0.0),    # Derecha
        ]
        
        # Ruta a la textura
        ruta_base = os.path.dirname(__file__)
        ruta_textura = os.path.join(ruta_base, "textura.jpg")
        tiene_textura = os.path.isfile(ruta_textura)
        
        # Crear los tres montacargas
        for i in range(3):
            # Crear montacargas con 10 cajas y dimensiones específicas
            montacargas = Montacargas(10, espaciado=1.1, dimensiones_caja=dimensiones[i])
            
            # Aplicar texturas o colores
            if tiene_textura:
                for caja in montacargas._cajas:
                    caja.aplicar_textura(ruta_textura)
            else:
                # Si no hay textura, asignar colores distintos según el montacargas
                color_base = [
                    (0.7, 0.3, 0.3),  # Rojo para el primer montacargas
                    (0.3, 0.7, 0.3),  # Verde para el segundo montacargas
                    (0.3, 0.3, 0.7),  # Azul para el tercer montacargas
                ]
                
                for j, caja in enumerate(montacargas._cajas):
                    # Variar ligeramente el color para cada caja
                    r = color_base[i][0] - (j % 5) * 0.05
                    g = color_base[i][1] - (j % 5) * 0.05
                    b = color_base[i][2] - (j % 5) * 0.05
                    caja.actor.GetProperty().SetColor(r, g, b)
            
            # Mover el montacargas completo a su posición
            self._mover_montacargas(montacargas, posiciones[i])
            
            # Añadir al renderizador
            montacargas.añadir_actores_a_renderizador(self._renderizador)
            
            # Guardar referencia
            self._montacargas.append(montacargas)
    
    def _mover_montacargas(self, montacargas, posicion):
        """
        Mueve todas las cajas de un montacargas a una posición específica.
        
        :param montacargas: Objeto Montacargas a mover
        :param posicion: Tupla (x, y, z) con la posición destino
        """
        # Mover el plano
        montacargas._plano_actor.SetPosition(posicion)
        
        # Mover cada caja, ajustando su posición relativa
        for caja in montacargas._cajas:
            pos_actual = caja.actor.GetPosition()
            caja.actor.SetPosition(
                pos_actual[0] + posicion[0],
                pos_actual[1] + posicion[1],
                pos_actual[2] + posicion[2]
            )
    
    def _crear_rampa(self, largo, ancho, alto):
        """
        Crea una rampa rectangular con las dimensiones especificadas.
        
        :param largo: Longitud de la rampa
        :param ancho: Ancho de la rampa
        :param alto: Altura de la rampa
        :return: Actor VTK que representa la rampa
        """
        # Crear una caja para la rampa
        rampa = vtk.vtkCubeSource()
        rampa.SetXLength(largo)    # Largo (eje X)
        rampa.SetYLength(ancho)    # Ancho (eje Y)
        rampa.SetZLength(alto)     # Alto (eje Z)
        rampa.Update()
        
        # Mapper y actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(rampa.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.5, 0.5, 0.6)  # Gris azulado
        
        # Posicionar la rampa
        # La rampa estará en el centro de la escena, con su base alineada con el plano XY
        actor.SetPosition(0.0, 6.0, alto/2)
        
        return actor
    
    def _configurar_camara(self):
        """
        Configura la cámara para visualizar toda la escena.
        """
        camara = self._renderizador.GetActiveCamera()
        camara.SetPosition(-25.0, 0.0, 15.0)  # Posición más alejada para ver toda la escena
        camara.SetFocalPoint(0.9, 0.0, -0.9)
        camara.SetViewUp(1.0, 0.0, 0.0)  # Orientación horizontal
    
    def iniciar_visualizacion(self):
        """
        Inicia la visualización de la escena.
        """
        # Configurar la ventana de renderizado
        ventana = vtk.vtkRenderWindow()
        ventana.AddRenderer(self._renderizador)
        ventana.SetSize(1024, 768)
        ventana.SetWindowName("Escena de Almacén")
        
        # Configurar el interactor
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(ventana)
        
        # Añadir estilo de interacción
        estilo = vtk.vtkInteractorStyleTrackballCamera()
        interactor.SetInteractorStyle(estilo)
        
        # Iniciar visualización
        ventana.Render()
        interactor.Initialize()
        interactor.Start()


# Punto de entrada principal
if __name__ == "__main__":
    escena = EscenaAlmacen()
    escena.iniciar_visualizacion()
