import os
import vtk
from caja_vtk import Caja  # Importamos la clase Caja del archivo caja_vtk.py

class Montacargas:
    """
    Representa un montacargas con un plano y cajas.
    """
    
    def __init__(self, num_cajas, espaciado, dimensiones_caja):
        """
        Inicializa el montacargas con un número específico de cajas.
        
        :param num_cajas: Número de cajas a crear (predeterminado: 10)
        :param espaciado: Factor de espaciado entre cajas (predeterminado: 1.2)
        :param dimensiones_caja: Tupla con dimensiones (x, y, z) de cada caja (predeterminado: (1.0, 1.0, 1.0))
        """
        self._num_cajas = num_cajas
        self._cajas = []
        self._lado_cuadricula = int(self._num_cajas ** 0.5) + 1  # Calcular lado de la cuadrícula
        self._espaciado = espaciado  # Factor de espaciado entre cajas
        self._dimensiones_caja = dimensiones_caja  # Dimensiones de las cajas (x, y, z)
        
        # Crear las cajas y posicionarlas en el plano
        self._crear_cajas()
        
        # El plano se crea después de las cajas para poder calcular su tamaño correctamente
        self._plano_actor = self._crear_plano()
    
    def _crear_plano(self):
        """
        Crea un plano que actuará como base para las cajas.
        El tamaño del plano será proporcional al número de cajas, su espaciado y dimensiones.
        
        :return: Actor VTK que representa el plano
        """
        # Calcular el tamaño real que ocupan las cajas
        ancho_max_x = 0
        ancho_max_y = 0
        
        # Si hay cajas, calcular el tamaño basado en las posiciones reales
        if self._cajas:
            # Encontrar los límites de las cajas
            min_x = float('inf')
            max_x = float('-inf')
            min_y = float('inf')
            max_y = float('-inf')
            
            for caja in self._cajas:
                pos = caja.actor.GetPosition()
                dim_x = self._dimensiones_caja[0] / 2  # Mitad del ancho en X
                dim_y = self._dimensiones_caja[1] / 2  # Mitad del ancho en Y
                
                # Calcular bordes de la caja actual
                left = pos[0] - dim_x
                right = pos[0] + dim_x
                bottom = pos[1] - dim_y
                top = pos[1] + dim_y
                
                # Actualizar límites
                min_x = min(min_x, left)
                max_x = max(max_x, right)
                min_y = min(min_y, bottom)
                max_y = max(max_y, top)
            
            # Calcular ancho total con margen
            # Usamos un margen proporcional al tamaño de la caja más grande
            margen_base = 0.8
            dim_max = max(self._dimensiones_caja[0], self._dimensiones_caja[1])
            margen = margen_base * dim_max  # Margen proporcional al tamaño de la caja
            
            # Calcular los anchos finales, considerando posibles diferencias de tamaño
            ancho_max_x = max_x - min_x + margen * 2
            ancho_max_y = max_y - min_y + margen * 2
            

        else:
            # Si no hay cajas, usar cálculo aproximado pero permitiendo diferentes proporciones
            dim_x = self._dimensiones_caja[0]
            dim_y = self._dimensiones_caja[1]
            dim_max = max(dim_x, dim_y)
            margen = 0.5 * dim_max  # Margen proporcional al tamaño de la caja
            
            # Calcular el tamaño total necesario, considerando las proporciones
            ancho_max_x = self._lado_cuadricula * self._espaciado * dim_x + margen * 2
            ancho_max_y = self._lado_cuadricula * self._espaciado * dim_y + margen * 2
            

        
        # Calcular las dimensiones del plano (puede ser rectangular)
        mitad_ancho_x = ancho_max_x / 2
        mitad_ancho_y = ancho_max_y / 2
        
        # Crear un plano con las dimensiones exactas necesarias
        plano = vtk.vtkPlaneSource()
        plano.SetOrigin(-mitad_ancho_x, -mitad_ancho_y, -0.1)  # Un poco por debajo del origen en Z
        plano.SetPoint1(mitad_ancho_x, -mitad_ancho_y, -0.1)  # Punto extendido en dirección X
        plano.SetPoint2(-mitad_ancho_x, mitad_ancho_y, -0.1)  # Punto extendido en dirección Y
        # Ajustar la resolución del plano proporcionalmente a sus dimensiones
        resolucion_x = max(20, int(ancho_max_x * 10))
        resolucion_y = max(20, int(ancho_max_y * 10))
        plano.SetResolution(resolucion_x, resolucion_y)  # Resolución del plano ajustada por eje
        plano.Update()
        
        # Crear mapper y actor para el plano
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(plano.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.3, 0.3, 0.3)  # Color gris oscuro
        
        return actor
    
    def _crear_cajas(self):
        """
        Crea las cajas y las posiciona en una cuadrícula sobre el plano.
        """
        # Usar el lado de la cuadrícula calculado en el constructor
        lado = self._lado_cuadricula
        
        # Crear y posicionar las cajas
        for i in range(self._num_cajas):
            # Calcular la posición en la cuadrícula
            fila = i // lado
            columna = i % lado
            
            # Crear una caja con las dimensiones especificadas
            # No es necesario aplicar textura aquí, ya que eso se maneja en la clase Caja
            caja = Caja(
                self._dimensiones_caja[0], 
                self._dimensiones_caja[1], 
                self._dimensiones_caja[2], 
                repeticiones=1
            )
            
            # Posicionar la caja en la cuadrícula con el espaciado configurado
            # El espaciado ahora considera también el tamaño de las cajas
            ancho_caja_x = self._dimensiones_caja[0]
            ancho_caja_y = self._dimensiones_caja[1]
            
            # Calcular el espaciado efectivo (proporción del tamaño de la caja)
            # Ajustamos el espaciado para tener en cuenta las dimensiones de las cajas
            espaciado_efectivo_x = ancho_caja_x * self._espaciado
            espaciado_efectivo_y = ancho_caja_y * self._espaciado
            
            # Calcular el offset para centrar la cuadrícula
            offset_x = (self._lado_cuadricula - 1) * espaciado_efectivo_x / 2
            offset_y = (self._lado_cuadricula - 1) * espaciado_efectivo_y / 2
            
            # Posicionar la caja considerando su tamaño
            # Ajuste para garantizar el posicionamiento correcto en ambas direcciones X e Y
            pos_x = columna * espaciado_efectivo_x - offset_x
            pos_y = fila * espaciado_efectivo_y - offset_y
            pos_z = self._dimensiones_caja[2] / 2  # La mitad de la altura para que se apoye en el plano
            
            caja.actor.SetPosition(pos_x, pos_y, pos_z)
            
            # Añadir la caja a nuestra lista
            self._cajas.append(caja)
    
    @property
    def plano_actor(self):
        """Devuelve el actor del plano."""
        return self._plano_actor
    
    @property
    def caja_actors(self):
        """Devuelve una lista de actores de las cajas."""
        return [caja.actor for caja in self._cajas]
    
    def añadir_actores_a_renderizador(self, renderizador):
        """
        Añade todos los actores (plano y cajas) al renderizador proporcionado.
        
        :param renderizador: Renderizador VTK donde añadir los actores
        """
        renderizador.AddActor(self._plano_actor)
        for caja in self._cajas:
            renderizador.AddActor(caja.actor)


# Ejemplo de uso (Solo prueba, se puede quitar)
if __name__ == "__main__":
    # Crear el montacargas con cajas de diferentes tamaños
    # El espaciado se mantiene en 1.1 para que las cajas estén cerca
    montacargas = Montacargas(10, espaciado=1.1, dimensiones_caja=(2.0, 1.0, 1.0))
    
    # Aplicar textura a cada caja
    ruta_base = os.path.dirname(__file__)
    ruta_textura = os.path.join(ruta_base, "textura.jpg")
    
    # Verificar si existe el archivo de textura
    if os.path.isfile(ruta_textura):
        for i, caja in enumerate(montacargas._cajas):
            caja.aplicar_textura(ruta_textura)
    else:
        print(f"Advertencia: No se encontró el archivo de textura '{ruta_textura}'")
        # Asignar colores diferentes a las cajas si no hay textura
        for i, caja in enumerate(montacargas._cajas):
            # Generar colores variados para cada caja
            r = 0.3 + (i % 3) * 0.2
            g = 0.3 + ((i + 1) % 3) * 0.2
            b = 0.3 + ((i + 2) % 3) * 0.2
            caja.actor.GetProperty().SetColor(r, g, b)
    
    # Configurar la visualización
    renderizador = vtk.vtkRenderer()
    renderizador.SetBackground(0.1, 0.1, 0.2)  # Fondo azul oscuro
    
    # Añadir todos los actores al renderizador
    montacargas.añadir_actores_a_renderizador(renderizador)
    
    # Configurar la cámara para una buena vista
    # Ajustar posición de la cámara considerando la proporción del plano
    dim_x = montacargas._dimensiones_caja[0]
    dim_y = montacargas._dimensiones_caja[1]
    ancho_x = montacargas._lado_cuadricula * montacargas._espaciado * dim_x
    ancho_y = montacargas._lado_cuadricula * montacargas._espaciado * dim_y
    tamano_escena = max(ancho_x, ancho_y) * 1.2  # Un poco más grande para ver todo
    
    # Ajustar la posición de la cámara según las proporciones de la escena
    camara = renderizador.GetActiveCamera()
    camara.SetPosition(tamano_escena, -tamano_escena*2, tamano_escena*3)
    camara.SetFocalPoint(0, 0, 0)
    camara.SetViewUp(0, 0, 1)
    
    # Configurar la ventana de renderizado
    ventana = vtk.vtkRenderWindow()
    ventana.AddRenderer(renderizador)
    ventana.SetSize(800, 600)
    ventana.SetWindowName("Montacargas con Cajas")
    
    # Configurar el interactor
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(ventana)
    
    # Añadir un estilo de interacción para controlar la cámara
    estilo = vtk.vtkInteractorStyleTrackballCamera()
    interactor.SetInteractorStyle(estilo)
    
    # Iniciar la visualización
    ventana.Render()
    interactor.Initialize()
    interactor.Start()
